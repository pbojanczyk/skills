/**
 * Format H-ear API responses as chat-friendly markdown.
 * Designed for messaging channels: Telegram, Slack, Discord, WhatsApp, Teams.
 */

import type {
    ClassifyResult, ClassesResult, HealthResult,
    UsageResult, JobsResult, JobResult, AsyncAccepted,
} from '@h-ear/core';

export function formatClassifyResult(result: ClassifyResult): string {
    const lines: string[] = [
        `**Audio Classification Complete**`,
        `Duration: ${result.duration?.toFixed(1) ?? '?'}s | ${result.eventCount} noise events detected`,
        '',
    ];

    if (result.classifications && result.classifications.length > 0) {
        lines.push('| Sound | Confidence | Category |');
        lines.push('|-------|-----------|----------|');

        const top = result.classifications
            .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
            .slice(0, 10);

        for (const cls of top) {
            const name = cls.className || cls.class || 'Unknown';
            const pct = `${Math.round((cls.confidence || 0) * 100)}%`;
            const cat = cls.category || cls.tier1 || '-';
            lines.push(`| ${name} | ${pct} | ${cat} |`);
        }
    } else {
        lines.push('No sound events detected above threshold.');
    }

    if (result.reportUrl) {
        lines.push('', `Full report: ${result.reportUrl}`);
    }

    return lines.join('\n');
}

export function formatClassesList(result: ClassesResult, search?: string): string {
    const lines: string[] = [
        `**Sound Classes** (${result.taxonomy})`,
        `${result.totalFiltered} of ${result.totalAvailable} classes`,
        '',
    ];

    if (result.classes.length > 0) {
        lines.push('| # | Class | Category |');
        lines.push('|---|-------|----------|');

        for (const cls of result.classes.slice(0, 20)) {
            lines.push(`| ${cls.index} | ${cls.name} | ${cls.category} |`);
        }

        if (result.pagination?.hasMore) {
            lines.push('', `_Showing ${result.classes.length} of ${result.totalFiltered} — use pagination for more._`);
        }
    } else {
        const hint = search ? ` matching "${search}"` : '';
        lines.push(`No classes found${hint}.`);
    }

    return lines.join('\n');
}

export function formatHealth(result: HealthResult): string {
    return [
        `**H-ear API Status**`,
        `Status: ${result.status}`,
        `Version: ${result.version}`,
        `Deployed: ${result.deployedTimestamp}`,
    ].join('\n');
}

export function formatUsage(result: UsageResult): string {
    const minutesPct = result.minutesTotal > 0
        ? Math.round((result.minutesUsed / result.minutesTotal) * 100)
        : 0;
    const callsPct = result.callsLimit > 0
        ? Math.round((result.callsToday / result.callsLimit) * 100)
        : 0;

    return [
        `**H-ear API Usage**`,
        `Plan: ${result.plan}`,
        `Minutes: ${result.minutesUsed.toLocaleString()} / ${result.minutesTotal.toLocaleString()} (${minutesPct}%)`,
        `Today: ${result.callsToday.toLocaleString()} / ${result.callsLimit.toLocaleString()} calls (${callsPct}%)`,
        `Active keys: ${result.activeKeys}`,
        `Period: ${result.periodStart} to ${result.periodEnd}`,
    ].join('\n');
}

export function formatJobsList(result: JobsResult): string {
    const lines: string[] = [
        `**Recent Jobs** (${result.total} total)`,
        '',
    ];

    if (result.jobs.length > 0) {
        lines.push('| Job ID | Status | File | Events | Created |');
        lines.push('|--------|--------|------|--------|---------|');

        for (const job of result.jobs) {
            const id = job.jobId.substring(0, 8);
            const status = job.status === 'completed' ? 'done' : job.status;
            const file = job.fileName || '-';
            const events = job.eventCount ?? '-';
            const created = job.createdAt.substring(0, 16).replace('T', ' ');
            lines.push(`| ${id}... | ${status} | ${file} | ${events} | ${created} |`);
        }

        if (result.pagination.hasMore) {
            lines.push('', `_Showing ${result.jobs.length} of ${result.total} — use "jobs last N" for more._`);
        }
    } else {
        lines.push('No jobs found.');
    }

    return lines.join('\n');
}

export function formatJobDetail(result: JobResult): string {
    const lines: string[] = [
        `**Job ${result.jobId.substring(0, 8)}...**`,
        `Status: ${result.status}`,
    ];

    if (result.fileName) lines.push(`File: ${result.fileName}`);
    if (result.duration) lines.push(`Duration: ${result.duration.toFixed(1)}s`);
    if (result.eventCount !== undefined) lines.push(`Events: ${result.eventCount}`);
    lines.push(`Created: ${result.createdAt}`);
    if (result.completedAt) lines.push(`Completed: ${result.completedAt}`);

    if (result.classifications && result.classifications.length > 0) {
        lines.push('', '| Sound | Confidence | Category |');
        lines.push('|-------|-----------|----------|');

        const top = result.classifications
            .sort((a, b) => (b.confidence || 0) - (a.confidence || 0))
            .slice(0, 10);

        for (const cls of top) {
            const name = cls.className || cls.class || 'Unknown';
            const pct = `${Math.round((cls.confidence || 0) * 100)}%`;
            const cat = cls.category || cls.tier1 || '-';
            lines.push(`| ${name} | ${pct} | ${cat} |`);
        }
    }

    if (result.reportUrl) {
        lines.push('', `Full report: ${result.reportUrl}`);
    }

    return lines.join('\n');
}

export function formatClassifySubmitted(accepted: AsyncAccepted): string {
    return [
        `**Analyzing Audio**`,
        `Job ID: ${accepted.requestId}`,
        `Status: ${accepted.status}`,
        `Results will be delivered when ready.`,
        '',
        `Check status: \`job ${accepted.requestId}\``,
    ].join('\n');
}

export function formatAlertRegistered(soundClass: string): string {
    return `Alert registered. You'll be notified whenever **${soundClass}** is detected.`;
}

export function formatAlertDeregistered(soundClass: string): string {
    return `Alert for **${soundClass}** has been removed.`;
}
