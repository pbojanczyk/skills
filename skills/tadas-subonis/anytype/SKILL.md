---
name: anytype
description: Interact with Anytype via anytype-cli and its HTTP API. Use when reading, creating, updating, or searching objects/pages in Anytype spaces; managing spaces; or automating Anytype workflows. Covers first-time setup (account creation, service start, space joining, API key) and ongoing API usage.
---

# Anytype Skill

Binary: `/root/.local/bin/anytype` (v0.1.9, already installed)
API base: `http://127.0.0.1:31012`
Auth: `Authorization: Bearer <ANYTYPE_API_KEY>` (key stored in `.env` as `ANYTYPE_API_KEY`)
API docs: https://developers.anytype.io

## Check Status First

```bash
anytype auth status     # is an account set up?
anytype space list      # is the service running + spaces joined?
```

If either fails → follow **Setup** below. Otherwise skip to **API Usage**.

## Setup (one-time)

```bash
# 1. Create a dedicated bot account (generates a key, NOT mnemonic-based)
anytype auth create tippy-bot

# 2. Install and start as a user service
anytype service install
anytype service start

# 3. Have Tadas send an invite link from Anytype desktop, then join
anytype space join <invite-link>

# 4. Create an API key
anytype auth apikey create tippy

# 5. Store the key
echo "ANYTYPE_API_KEY=<key>" >> /root/.openclaw/workspace/.env
```

Ask Tadas for the space invite link if not already provided.

## API Usage

Load `.env` first:
```python
import json, os, urllib.request
env = dict(l.strip().split('=',1) for l in open('/root/.openclaw/workspace/.env') if '=' in l and not l.startswith('#'))
API_KEY = env.get('ANYTYPE_API_KEY', '')
BASE = 'http://127.0.0.1:31012'
HEADERS = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}
```

See `references/api.md` for all endpoints and request shapes.

### Common Patterns

**List spaces:**
```
GET /v1/spaces
```

**Search objects globally:**
```
POST /v1/search
{"query": "meeting notes", "limit": 10}
```

**List objects in a space:**
```
GET /v1/spaces/{space_id}/objects?limit=50
```

**Create an object:**
```
POST /v1/spaces/{space_id}/objects
{"type_key": "page", "name": "My Page", "body": "Markdown content here"}
```

**Update an object (patch body/properties):**
```
PATCH /v1/spaces/{space_id}/objects/{object_id}
{"markdown": "Updated content"}
```
⚠️ **Create uses `body`, Update uses `markdown`** — different field names for the same content. Easy to mix up.

⚠️ **CRITICAL: PATCH does NOT update the body/content field.** Sending `body` or `markdown` in a PATCH silently succeeds (HTTP 200) but the content is NOT updated in Anytype. Only metadata fields like `name` are updated via PATCH.

**The only reliable way to update an object's content is: DELETE + recreate.**
```python
# Step 1: delete old object
requests.delete(f"{BASE}/v1/spaces/{space_id}/objects/{old_id}", headers=headers)

# Step 2: create new object with full updated content
resp = requests.post(f"{BASE}/v1/spaces/{space_id}/objects",
    json={"name": name, "type_key": "ot-note", "body": new_content},
    headers=headers)
new_id = resp.json()["object"]["id"]
```
This means callers must update any stored references to the object ID after recreation.

Use `scripts/anytype_api.py` as a ready-made helper for making API calls.

## Key Constraints (learned from testing)

- **`links` property is read-only** — system-managed, populated only by the desktop editor. API returns 400 if you try to set it.
- **Collections cannot have an `icon` set on create** — it causes a 500. Create without icon first.
- **`body` vs `markdown`** — create uses `body`, update uses `markdown`.
- **PATCH cannot update content** — `body`/`markdown` fields in PATCH are silently ignored. HTTP 200 is returned but content is unchanged. To update content: DELETE the object and recreate it with the new content. Store the new object ID.
- **`related_pages` custom property** (key: `related_pages`, format: `objects`) exists in the space for API-writable object links.

---

## Object Type Preference

**Default to `page` for all content.** Notes (`note` type) are the exception — use only when content is explicitly informal/scratchpad and doesn't need to be linked into the knowledge graph.

Everything meaningful (call notes, research, hub pages, product docs, meeting summaries) → `type_key: "page"`.

---

## Knowledge Graph Principles — Apply These Always

Anytype is a **linked knowledge base**, not a flat file store. Every time you create or update content, ask: *how does this connect to what already exists?*

### 1. Link Everything
- Use `[[Page Name]]` style inline links in markdown body to reference related objects.
- When creating a new page, search for related existing pages first and link back to them.
- When updating an existing page, add links to any newly created pages that are related.

### 2. Collections as Cluster Containers
- For any topic cluster, create a **Collection** (`type_key: collection`) — not a plain page hub.
- Collections are Anytype's native container type. They appear in the sidebar, support multiple views (grid, list, kanban), and are queryable.
- Use the **Lists API** to add child objects to a collection.
- Also maintain a **hub page** inside the collection as the written overview (description + links).
- Collections in this space:
  - `Merkys — Healthcare Chatbot` → `bafyreicm3a7xj6zhq2l3ouuo74klcxixnvilo3xif24yoijb4wghjpepm4`
  - `Mercoder.ai` → `bafyreigvkwfrtbmrkureuoxfj4ewjrccvpla7dndd7d3ygsyjxuqzorgja`
  - `Vibe Coding Metrics` → `bafyreicejuvonwzo5sgjieana65l4pjbsrhlij5fpbjdrbjc5kdogwwalu`

**Create + populate a collection:**
```python
# 1. Create (no icon on create — causes 500)
col = api('POST', f'/v1/spaces/{SPACE}/objects', {'type_key': 'collection', 'name': 'My Cluster'})
col_id = col['object']['id']

# 2. Add objects
api('POST', f'/v1/spaces/{SPACE}/lists/{col_id}/objects', {'objects': [id1, id2, id3]})
```

**Sidebar note:** Sidebar pinning is manual only — no API. Ask the user to pin the Homepage and Collections in the Anytype desktop app.

### 3. Bidirectional Awareness
- Anytype shows backlinks automatically, but you must **write forward links** in the body.
- After creating content, update the hub page to include a link to the new object.

### 4. Before Creating a Page
```
1. Search: POST /v1/spaces/{space_id}/search {"query": "<topic>", "limit": 10}
2. Check if a page already exists — update it rather than duplicate
3. Identify the parent hub page(s) this belongs to
4. Create the page with inline links to related pages in the body
5. Patch the hub page(s) to add a link to the new page
```

### 5. Hub Page Template
When creating a hub page, use this structure:

```markdown
## Overview
<2-3 sentence summary>

## Pages
- [Child Page Name](anytype://object/<id>) — one-line description
- [Another Page](anytype://object/<id>) — one-line description

## Key Facts
- Fact 1
- Fact 2
```

### 6. Native Object Links (Anytype Graph Feature)

Anytype has two link mechanisms. Use **both**:

#### A. System `links` property (read-only via API)
The built-in `links` property is auto-populated by the Anytype desktop app when you use `@mention` or `[[]]` syntax in the rich text editor. **The API cannot set it directly** — attempting to do so returns `400: property 'links' cannot be set directly as it is a reserved system property`.

#### B. Custom `related_pages` property (writable via API) ✅
A custom `objects`-type property called **`related_pages`** (key: `related_pages`) has been created in the space. This shows up in each object's sidebar and is used by the API to express object relationships. **Always set this when creating or updating objects.**

```json
// On create:
POST /v1/spaces/{space_id}/objects
{
  "type_key": "page",
  "name": "My Page",
  "body": "...",
  "properties": [
    {"key": "related_pages", "objects": ["<hub_id>", "<sibling_id>"]}
  ]
}

// On update:
PATCH /v1/spaces/{space_id}/objects/{object_id}
{
  "markdown": "...",
  "properties": [
    {"key": "related_pages", "objects": ["<hub_id>", "<sibling_id>"]}
  ]
}
```

**Rule:** Hub pages must have `related_pages` set to all their children + the homepage. Child pages must have `related_pages` set back to their hub (and any directly related siblings). This creates visible edges in the Anytype graph view.

### 7. Inline Links Syntax

**Use `anytype://` deep links — NOT `object.any.coop` URLs.**

`object.any.coop` URLs in body text are rendered as plain text and are NOT clickable inside the Anytype app. The only format that renders as a clickable internal link is:

```markdown
[Link Text](anytype://object?objectId=<object_id>&spaceId=<space_id>)
```

Example:
```markdown
[Vibe Coding Metrics — Hub](anytype://object?objectId=bafyreigkp2yirhk7epzialjvevnoh6l3wcsr2ifr4zl6umunzhhgspxetq&spaceId=bafyreial7tzkey5sntoizw7scv2lrywqdicd7m6ru2k6wae7w3z6igm5ke.1f4pitw5ca9gc)
```

Helper function:
```python
def anytype_link(name, obj_id, space_id):
    return f"[→ Open: {name}](anytype://object?objectId={obj_id}&spaceId={space_id})"
```

**⚠️ Do NOT put links inside markdown headings (`## [Name](anytype://...)`)** — Anytype strips the link and renders only the plain text. Links only work as inline text in the body, not as part of a heading.

**Correct pattern for a hub entry:**
```markdown
## Speaker Name
[→ Open: Speaker Name](anytype://object?objectId=<id>&spaceId=<space_id>)

One-line summary here.

---
```

Use `object.any.coop` links only when sharing with external users (outside Anytype app).

### 9. Tags — Always Apply

Every page must have tags set via the `tag` property (key: `tag`, format: `multi_select`). Tags power search filtering and cross-cluster grouping in the Anytype UI.

**Tag property ID:** `bafyreicsoqz7qja7uqrpfvtub4c4gg7djsv24ojc42em6j3a2ctaeiy7r4`

**Important:** The `tag` property requires pre-existing tag option IDs — you cannot pass free-text strings. Use the IDs below or create new tags first via the Tags API.

**Create a new tag:**
```
POST /v1/spaces/{space_id}/properties/{TAG_PROP_ID}/tags
{"name": "my-tag", "color": "blue"}
→ returns tag.id — use that ID in multi_select
```

**Set tags on an object:**
```json
PATCH /v1/spaces/{space_id}/objects/{object_id}
{
  "properties": [
    {"key": "tag", "multi_select": ["<tag_id_1>", "<tag_id_2>"]}
  ]
}
```

**Defined tags (use these IDs):**

| Tag | ID | Use for |
|-----|----|---------|
| `merkys` | `bafyreiatxjki2c6zy6pyxf6e3xkfnjheqvfmajhqmtpyssiw6wvz3z4x3e` | Merkys chatbot pages |
| `mercoder` | `bafyreibmnkru5tu4ltfo6xwu5ijmzgt54dy5dsbekz7l7ppxqjrntgceam` | Mercoder.ai pages |
| `vibe-coding` | `bafyreib5fo4pfeq5s46akb6wqk4jufu3j63cp5ay5wrxn2hda2bbtdo3ou` | Vibe coding metrics |
| `paceflow` | `bafyreicnhcmlzav2olnejjpgi6mznthckbheypbwddxtrrsekddmqojica` | Paceflow product pages |
| `call-notes` | `bafyreicuka2zitbrqbae6khc7sse2mnwlcx3a3i2gig2jqvffknjyzt3fe` | Meeting/call notes |
| `research` | `bafyreihtobisskd2ctgs7r74k5gfa6tzejxdtf5qkbyvac6okdgj43uv4y` | Research documents |
| `product` | `bafyreib27tsqjemixmc76yam7ui66x4dsp2vncwbqd7ci7c7mwkqp7gvba` | Product strategy/roadmap |
| `hub` | `bafyreic2y3u3iai4z36wrnebj4pejstdkov7p3oj6dokho5xhmaog27jzi` | Hub/index pages |
| `healthcare` | `bafyreid3nw4casmj4obscsk53jwowbs7x2yjgsm6l4guivrr4nmts5r42i` | Healthcare domain |
| `devops` | `bafyreieqpordkymw7jo5lp3habdyqomytp7bvtpxvwt4m32zby3kcbs3au` | DevOps/infrastructure |
| `security` | `bafyreieazhkkfmtojxin6d35fh5kgfdkqb6t25d77p2i6dkixsj5ppaqii` | Security topics |
| `ai` | `bafyreibdo3qelsyuapt44fbjjkhl3w6jnw3ohpqdzecs5rro4awjlawrwq` | AI/ML topics |

**Tagging rules:**
- Always add the project tag (`merkys`, `mercoder`, `vibe-coding`, `paceflow`)
- Always add the content type tag (`call-notes`, `research`, `product`, `hub`)
- Add domain tag when relevant (`healthcare`, `devops`, `security`, `ai`)
- Hub pages always get the `hub` tag

### 10. Proactive Organization Checklist
After any write operation, run through:
- [ ] Does a hub page exist for this topic? If not, create one.
- [ ] Did I link the new/updated page from the hub?
- [ ] Did I link related pages from within the new content?
- [ ] Are there orphan pages (no incoming links) I should connect?
- [ ] Did I set `tag` (project + content type + domain) on the new page?
- [ ] Did I set `related_pages` pointing to the hub?

---

## Sharing Links

**Always use the public web link format — NOT `anytype://` deep links.**

```
https://object.any.coop/{object_id}?spaceId={space_id}&inviteId={invite_id}#{hash}
```

The `inviteId` and `#hash` are space-level constants (stored in TOOLS.md under Anytype).
Only `object_id` changes per object.

Example:
```
https://object.any.coop/bafyreigcwv5psopd27jcek5ba7if2lamskahwp7aylzsbw2aunibfr7kei?spaceId=bafyreial7tzkey5sntoizw7scv2lrywqdicd7m6ru2k6wae7w3z6igm5ke.1f4pitw5ca9gc&inviteId=bafybeifel75s42deh74lbjx3socdyung4ojspjgbr64jxrduf3dghlx35i#CvFB12csDDVDpYxi5J1FewXmdsLmifnLx4p3fBCRG6Jt
```
