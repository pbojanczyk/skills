#!/bin/bash
# ==========================================
# BOOTSTRAP: DEPLOYMENT SCRIPT (v0.0.1)
# ==========================================
# Promotes leio-sdlc from workspace to runtime.

DEV_DIR="/root/.openclaw/workspace/leio-sdlc"
PROD_DIR="/root/.openclaw/skills/leio-sdlc"

RUN_TESTS=false
DRY_RUN=false

for arg in "$@"; do
    case $arg in
        --preflight)
        RUN_TESTS=true
        DRY_RUN=true
        shift
        ;;
    esac
done

echo "[$(date '+%H:%M:%S')] Starting deployment flow: $DEV_DIR -> $PROD_DIR"

# 1. Optional Safety Check (Only runs if --preflight is passed)
if [ "$RUN_TESTS" = true ]; then
    echo "🧪 Running Preflight CUJ Tests..."
    bash "$DEV_DIR/scripts/test_sdlc_cujs.sh"
    if [ $? -ne 0 ]; then
        echo "❌ PREFLIGHT FAILED: CUJ test suite failed."
        exit 1
    fi
    echo "✅ PREFLIGHT PASSED."
else
    echo "⚠️ Skipping CUJ Tests (run with --preflight to enable)"
fi

if [ "$DRY_RUN" = true ]; then
    echo "🛑 Dry run (--preflight) active. Exiting before actual deployment."
    exit 0
fi

# 2. Sync Files
bash "$DEV_DIR/scripts/build_release.sh" || exit 1
mkdir -p "$PROD_DIR"
cp -r "$DEV_DIR/dist/"* "$PROD_DIR/"

echo "✅ DEPLOYMENT SUCCESS: leio-sdlc v0.0.1 is now live."
