import type { HearApiClient } from '@h-ear/core';

/** Default gateway webhook receiver — OpenClaw routes results back to the user's channel. */
const GATEWAY_CALLBACK = 'https://gateway.openclaw.ai/webhooks/h-ear';

export async function classifyBatchCommand(
    client: HearApiClient,
    urls: string[],
    options?: { threshold?: number; callbackUrl?: string },
): Promise<string> {
    const files = urls.map((url, i) => ({ url, id: `file-${i + 1}` }));
    const result = await client.classifyBatch({
        files,
        callbackUrl: options?.callbackUrl ?? GATEWAY_CALLBACK,
        threshold: options?.threshold ?? 0.3,
    });

    return [
        `**Batch Submitted**`,
        `Batch ID: ${result.batchId}`,
        `Files: ${result.fileCount}`,
        `Estimated: ~${result.estimatedCompletionMinutes} min`,
        `Status: ${result.status}`,
    ].join('\n');
}
