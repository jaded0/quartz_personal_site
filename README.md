# jadenlorenc.com

My digital garden. [Quartz 5](https://github.com/jackyzha0/quartz), deployed to GitHub Pages.

## Where things live

Everything under `content/` is **generated**. Never edit it — the next sync overwrites it.
Edit the note in the vault (`~/Documents/brain`) instead.

- Topic notes stay where they naturally live: vault root, `robust_control/`,
  `stack breakdown/`, `uConsole/`.
- **Site furniture lives in `personal-site/`** — `homepage.md` plus one intro page per
  section. These exist only because the site does, so they're kept together.
- `garden.base` at the vault root is the control panel: what's published, what's been pulled
  down, and what's missing a slug or description.

## Publishing a note

Add `publish: true` to a note's frontmatter in the vault. That's it — the daily timer picks
it up. Remove the flag and the page comes down.

```yaml
---
title: A thing I figured out
publish: true
section: notebook      # essays | research | control | notebook | reference
slug: a-thing          # optional; controls the URL
description: ...       # optional; derived from the first paragraph otherwise
---
```

Other frontmatter the sync understands:

| key | effect |
|---|---|
| `authorship: ai-generated` | prepends a disclosure banner (uses `model:` if present) |
| `secrets_reviewed: true` | silences the credential scanner for that note — only after you've actually read it |

`section: ""` puts a page at the site root; that plus `slug: index` is how
`personal-site/homepage.md` becomes `/`. The sync refuses to run if nothing resolves to the
root, so an accidental unflag can't silently delete the homepage.

## Running it

```bash
python3 sync_from_vault.py            # dry run: what would change
python3 sync_from_vault.py --apply    # write into content/
./publish.sh                          # sync + commit + push (CI deploys)
npx quartz build --serve              # preview at localhost:8080
```

Needs Node 22+ (`nvm use 22`).

## How the sync protects you

`sync_from_vault.py` replaced an older script that only ever copied files in — it never
deleted, never handled renames, never copied attachments, and matched its publish tag as a
bare substring anywhere in the file.

The current one:

- **Denies by path first.** Daily notes, `private/`, `church/`, `archive/`, `dragn-obsidian/`,
  `zotero_notes/`, coursework and answer keys never publish, even if flagged. A flag can be
  set by accident; a path can't.
- **Scans for credentials** and aborts the whole run without writing anything if a flagged
  note contains something key-shaped, an IP, a UUID, or a phone number.
- **Mirrors with delete**, so unflagging a note actually takes it down.
- **Copies referenced attachments** into `content/attachments/`.
- **Rewrites links.** Wikilinks to published notes are remapped onto their slugs; links to
  unpublished notes are unwrapped to plain text instead of shipping as dead links.
- **Cleans bodies** — strips stray inline hashtag lines and Obsidian block anchors.

## Automation

```bash
systemctl --user enable --now garden-sync.timer
systemctl --user start garden-sync          # run once now
journalctl --user -u garden-sync -n 50      # why did it not publish?
```

A failed run means nothing was published, which is the intended direction.
