import type { HearApiClient } from '@h-ear/core';
import { formatAlertRegistered, formatAlertDeregistered } from '../formatter.js';

/** Default gateway webhook receiver — OpenClaw routes alerts back to the user's channel. */
const GATEWAY_CALLBACK = 'https://gateway.openclaw.ai/webhooks/h-ear';

export async function alertOnCommand(
    client: HearApiClient,
    soundClass: string,
    options?: { callbackUrl?: string },
): Promise<string> {
    await client.registerWebhook({
        url: options?.callbackUrl ?? GATEWAY_CALLBACK,
        events: ['job.completed'],
        soundClass,
    });
    return formatAlertRegistered(soundClass);
}

export async function alertOffCommand(
    client: HearApiClient,
    webhookId: string,
    soundClass: string,
): Promise<string> {
    await client.deregisterWebhook(webhookId);
    return formatAlertDeregistered(soundClass);
}
