import type { HearApiClient } from '@h-ear/core';
import { formatClassifySubmitted } from '../formatter.js';

/** Default gateway webhook receiver — OpenClaw routes results back to the user's channel. */
const GATEWAY_CALLBACK = 'https://gateway.openclaw.ai/webhooks/h-ear';

export async function classifyCommand(
    client: HearApiClient,
    url: string,
    options?: { threshold?: number; callbackUrl?: string },
): Promise<string> {
    const accepted = await client.submitClassify({
        url,
        threshold: options?.threshold ?? 0.3,
        callbackUrl: options?.callbackUrl ?? GATEWAY_CALLBACK,
    });
    return formatClassifySubmitted(accepted);
}
