# MCSManager API notes

Use this file only when actually operating MCSManager.

## Local assumptions

Keep these values in mind unless the user says otherwise:

- Host machine: `olddell`
- Default instance UUID: `32e62fa5ba064d27997a94713e125260`

## Credentials and config

Use `config.json` in this skill directory as the primary local config file when present:

- `/home/szabi/.openclaw/workspace/skills/mcsmanager-controller/config.json`

Expected fields:

- `baseUrl` — base URL of the web/API panel
- `apiKey` — token or API key
- `instanceUuid` — default instance UUID
- `daemonId` — optional, only if your setup needs it

Do not bake real secrets into docs or examples that may be shared publicly.

If `config.json` is missing, create it from `config.example.json` first.

If `config.json` is incomplete, then look for environment variables or existing deployment files.

## Safe action order

For most tasks, use this order:

1. Confirm panel/API reachability.
2. Confirm target instance identity.
3. Read current status.
4. Read recent logs.
5. Perform the requested action.
6. Verify post-action status.

## Typical operations to implement

Different MCSManager versions expose slightly different endpoints and payloads. Adapt to the installed version instead of assuming exact paths.

Common operation categories:

- list instances
- get one instance status/details
- get recent output / logs
- start instance
- stop instance
- restart instance
- kill instance
- send console command to instance

## Fallback strategy when API shape is unclear

If exact endpoints are unknown:

1. Inspect local docs, reverse proxy config, compose files, or existing scripts.
2. Search the workspace for `MCSManager`, panel URL, token names, or curl snippets.
3. Use host-side checks:
   - container/process status
   - bound ports
   - Java process command line
   - server log files
4. Tell the user what is known vs unknown.

## Reporting style

Keep reports short and admin-useful:

- instance checked
- status before
- action performed
- status after
- one or two key log lines

Example:

- Checked instance `32e62fa5ba064d27997a94713e125260`
- Status before: online but throwing plugin errors during join
- Action: read latest log, no restart yet
- Key finding: `NoClassDefFoundError` from plugin X after startup
- Next move: disable/update plugin X, then restart once
