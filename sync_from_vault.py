#!/usr/bin/env python3
"""
Publish selected Obsidian notes from the vault into this Quartz site.

Replaces the old update_from_brain.py, which was copy-only: it never deleted,
never handled renames, never copied attachments, and matched "#publish-this"
as a bare substring anywhere in the file (including inside code blocks).

A note is published when ALL of these hold:
  1. its path is not on the DENY list (checked first, so a stray flag can't
     leak a private note),
  2. its frontmatter has `publish: true`,
  3. it contains nothing that looks like a credential.

Usage:
    python3 sync_from_vault.py              # dry run, prints a plan
    python3 sync_from_vault.py --apply      # actually write
    python3 sync_from_vault.py --apply --quiet
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path

import yaml

VAULT = Path("/home/jaden/Documents/brain")
SITE = Path(__file__).resolve().parent
CONTENT = SITE / "content"
ATTACH_DIR = "attachments"

# Files in content/ that this script does not manage and must never delete.
# Hand-written landing pages live in the repo, not the vault; never delete them.
PRESERVE_NAMES = {"index.md"}

# Directories that never publish, regardless of frontmatter. Belt and
# suspenders: a publish flag can be set by accident, a path cannot.
DENY_DIRS = {
    ".git", ".obsidian", ".trash", "templates", "private", "church",
    "dragn-obsidian",     # shared lab vault, not solely ours
    "archive",            # third-party clippings and PDF conversions
    "zotero_notes",       # third-party paper annotations
    "Excalidraw",
    "node_modules", ".opencode",
}

# Individual notes that stay private even if flagged.
DENY_FILES = {
    "health.md", "Meds.md", "personal-finance.md", "student loan updates.md",
    "adhd-burnout-provider-search.md", "adhd-burnout-provider-detail.md",
    "provo-life.md", "small claims mill race.md", "a fools errand.md",
    "homelab-wishlist.md",
}

# Daily notes are a private log, never a garden page.
DAILY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}.*\.md$")

# Coursework and answer keys: publishing these is an academic-integrity hazard.
COURSEWORK_RE = re.compile(
    r"(answer_key|RCHW|walkthrough|^hw\d|^HW\d|Written HW|transcribed hw|"
    r"Solution to Problem|assignment_problems|quiz\d)",
    re.IGNORECASE,
)

SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{20,}"), "OpenAI-style API key"),
    (re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,})"), "GitHub token"),
    (re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----"), "private key"),
    (re.compile(r"(?i)\b(?:api[_-]?key|secret|passwd|password|access[_-]?token)\s*[:=]\s*['\"]?[A-Za-z0-9/_\-+.]{12,}"), "credential assignment"),
    # "the login password is `1212`" — prose, not an assignment. Caught this
    # phrasing only after it nearly shipped a live sudo password.
    (re.compile(r"(?i)\b(?:password|passphrase|pin|passcode)\b[^.\n]{0,40}?\bis\b[^.\n]{0,20}?[`'\"*]{0,2}[A-Za-z0-9!@#$%^&*_\-]{4,}"), "password stated in prose"),
    (re.compile(r"(?i)\b[a-z0-9-]+\.ts\.net\b"), "Tailscale MagicDNS name"),
    (re.compile(r"(?i)\btskey-[A-Za-z0-9-]+"), "Tailscale auth key"),
    (re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"), "UUID (drive/device identifier)"),
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "IP address"),
    (re.compile(r"\b[a-z0-9]{6,}\.dns\.nextdns\.io\b"), "NextDNS profile"),
    (re.compile(r"\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b"), "phone number"),
]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
# A tag line: only hashtags and whitespace on the line.
TAGLINE_RE = re.compile(r"^[ \t]*(?:#[A-Za-z0-9_/\-]+[ \t]*)+$", re.MULTILINE)
BLOCK_ANCHOR_RE = re.compile(r"[ \t]*\^[a-zA-Z0-9]{6,}[ \t]*$", re.MULTILINE)
EMBED_RE = re.compile(r"!\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]*))?\]\]")
MD_IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)\s]+)")
WIKILINK_RE = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#([^\]|]*))?(?:\|([^\]]*))?\]\]")
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".avif", ".pdf"}


def log(msg: str, quiet: bool = False) -> None:
    if not quiet:
        print(msg)


def split_frontmatter(text: str):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}, text
    if not isinstance(fm, dict):
        return {}, text
    return fm, text[m.end():]


def is_denied(rel: Path) -> str | None:
    parts = set(rel.parts[:-1])
    hit = parts & DENY_DIRS
    if hit:
        return f"in denied directory '{sorted(hit)[0]}'"
    if rel.name in DENY_FILES:
        return "on the private-file denylist"
    if DAILY_RE.match(rel.name):
        return "daily note"
    if COURSEWORK_RE.search(rel.name):
        return "coursework / answer key"
    return None


def scan_secrets(text: str) -> list[str]:
    hits = []
    for pat, label in SECRET_PATTERNS:
        m = pat.search(text)
        if m:
            snippet = m.group(0)
            if len(snippet) > 12:
                snippet = snippet[:6] + "…" + snippet[-4:]
            hits.append(f"{label} ({snippet})")
    return hits


def build_vault_index():
    """basename (and stem) -> path, for resolving wikilinks and embeds."""
    notes: dict[str, Path] = {}
    assets: dict[str, Path] = {}
    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in DENY_DIRS]
        for fn in files:
            p = Path(root) / fn
            rel = p.relative_to(VAULT)
            if fn.endswith(".md"):
                notes.setdefault(p.stem, rel)
                notes.setdefault(str(rel.with_suffix("")), rel)
            elif p.suffix.lower() in IMAGE_EXTS:
                assets.setdefault(fn, rel)
                assets.setdefault(p.stem, rel)
    return notes, assets


def clean_body(body: str) -> str:
    body = TAGLINE_RE.sub("", body)          # stray "#hebbian #phd" lines
    body = BLOCK_ANCHOR_RE.sub("", body)     # Obsidian block anchors ^85af19
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip() + "\n"


def derive_description(body: str, limit: int = 240) -> str:
    """First real prose paragraph, for <meta description> and social cards.

    Skips headings, callouts, blockquotes, tables, code fences and images so the
    AI-disclosure banner (or a leading figure) doesn't become the page summary.
    """
    in_fence = False
    for block in re.split(r"\n\s*\n", body):
        block = block.strip()
        if not block:
            continue
        if block.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence or block[0] in "#>|!" or block.startswith(("---", "$$", "- ", "* ", "1.")):
            continue
        text = re.sub(r"[*`]", "", block)
        text = re.sub(r"\[\[([^\]|]*\|)?([^\]]*)\]\]", r"\2", text)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = " ".join(text.split())
        if len(text) < 40:
            continue
        return text[: limit - 1] + "…" if len(text) > limit else text
    return ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    q = args.quiet

    if not VAULT.is_dir():
        print(f"error: vault not found at {VAULT}", file=sys.stderr)
        return 2

    notes_idx, assets_idx = build_vault_index()

    selected: dict[Path, tuple[Path, dict, str]] = {}   # dest rel -> (src rel, fm, body)
    secret_hits: list[tuple[Path, list[str]]] = []
    skipped_denied: list[tuple[Path, str]] = []

    for root, dirs, files in os.walk(VAULT):
        dirs[:] = [d for d in dirs if d not in DENY_DIRS]
        for fn in sorted(files):
            if not fn.endswith(".md"):
                continue
            src = Path(root) / fn
            rel = src.relative_to(VAULT)

            reason = is_denied(rel)
            try:
                raw = src.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            fm, body = split_frontmatter(raw)
            flagged = fm.get("publish") is True
            if not flagged:
                continue
            if reason:
                skipped_denied.append((rel, reason))
                continue

            if not fm.get("secrets_reviewed"):
                hits = scan_secrets(body)
                if hits:
                    secret_hits.append((rel, hits))
                    continue

            # destination: `section:` overrides the vault folder,
            # `slug:` overrides the filename (and therefore the URL)
            section = fm.get("section")
            stem = str(fm.get("slug") or src.stem)
            dest = Path(section) / f"{stem}.md" if section else rel.with_name(f"{stem}.md")
            selected[dest] = (rel, fm, body)

    # --- fail closed on anything that smells like a credential -----------
    if secret_hits:
        print("\nABORTED — possible secrets in notes flagged for publish:\n", file=sys.stderr)
        for rel, hits in secret_hits:
            print(f"  {rel}", file=sys.stderr)
            for h in hits:
                print(f"      {h}", file=sys.stderr)
        print(
            "\nNothing was written. Either remove the secret, unset `publish: true`,\n"
            "or — if it is a false positive you have actually read — add\n"
            "`secrets_reviewed: true` to that note's frontmatter.",
            file=sys.stderr,
        )
        return 1

    # Map every name a note might be referenced by (its vault stem, its vault
    # path) onto the stem it is actually published under, so renaming a note via
    # `slug:` does not break inbound wikilinks.
    name_to_slug: dict[str, str] = {}
    for dest, (rel, _fm, _body) in selected.items():
        name_to_slug[Path(rel).stem] = dest.stem
        name_to_slug[str(Path(rel).with_suffix(""))] = dest.stem
        for alias in (_fm.get("aliases") or []):
            if isinstance(alias, str):
                name_to_slug.setdefault(alias, dest.stem)

    # --- transform bodies ------------------------------------------------
    outputs: dict[Path, str] = {}
    wanted_assets: dict[str, Path] = {}
    unwrapped = 0
    for dest, (rel, fm, body) in selected.items():
        body = clean_body(body)

        def embed_sub(m):
            nonlocal unwrapped
            target, alias = m.group(1).strip(), m.group(2)
            base = Path(target).name
            if Path(base).suffix.lower() in IMAGE_EXTS or base in assets_idx or Path(base).stem in assets_idx:
                key = base if base in assets_idx else Path(base).stem
                if key in assets_idx:
                    srcp = assets_idx[key]
                    wanted_assets[srcp.name] = srcp
                    return f"![[{ATTACH_DIR}/{srcp.name}]]"
                return alias or Path(base).stem
            # transclusion of a note: keep only if that note is published
            slug = name_to_slug.get(base) or name_to_slug.get(target)
            if slug:
                return f"![[{slug}]]"
            unwrapped += 1
            return alias or base

        def link_sub(m):
            nonlocal unwrapped
            target, anchor, alias = m.group(1).strip(), m.group(2), m.group(3)
            base = Path(target).name
            slug = name_to_slug.get(base) or name_to_slug.get(target)
            if slug:
                shown = alias or base
                frag = f"#{anchor}" if anchor else ""
                return f"[[{slug}{frag}|{shown}]]"
            unwrapped += 1
            return alias or base   # unwrap to plain text, not a dead link

        body = EMBED_RE.sub(embed_sub, body)
        body = MD_IMAGE_RE.sub(
            lambda m: m.group(0), body
        )
        body = WIKILINK_RE.sub(link_sub, body)

        body_for_desc = body
        # Disclosure banner for notes drafted with an AI assistant.
        if fm.get("authorship") == "ai-generated":
            model = fm.get("model")
            who = f" ({model})" if model else ""
            body = (
                f"> [!note] Drafted with an AI assistant{who}\n"
                "> I wrote this note with model help and then read it, checked the\n"
                "> math, and kept it because I agree with it. Errors are still mine.\n\n"
            ) + body

        fm_out = {k: v for k, v in fm.items() if k not in ("section", "secrets_reviewed", "slug")}
        if not fm_out.get("description"):
            desc = derive_description(body_for_desc)
            if desc:
                fm_out["description"] = desc
        fm_out.setdefault("title", Path(rel).stem)
        if not fm_out.get("tags"):
            fm_out.pop("tags", None)
        head = yaml.safe_dump(fm_out, sort_keys=False, allow_unicode=True).strip()
        outputs[dest] = f"---\n{head}\n---\n\n{body}"

    # --- compute the mirror diff ----------------------------------------
    CONTENT.mkdir(parents=True, exist_ok=True)
    existing = set()
    for p in CONTENT.rglob("*"):
        if p.is_file():
            r = p.relative_to(CONTENT)
            if r.name in PRESERVE_NAMES or r.parts[0] == ".obsidian":
                continue
            existing.add(r)

    desired = set(outputs) | {Path(ATTACH_DIR) / n for n in wanted_assets}
    to_delete = sorted(existing - desired)
    to_write = sorted(outputs)

    log(f"\npublish gate     : {len(selected)} notes flagged `publish: true`", q)
    log(f"attachments      : {len(wanted_assets)} referenced files", q)
    log(f"links unwrapped  : {unwrapped} (pointed at unpublished notes)", q)
    if skipped_denied:
        log(f"blocked by denylist: {len(skipped_denied)}", q)
        for rel, why in skipped_denied:
            log(f"    - {rel}  ({why})", q)
    log(f"will write       : {len(to_write)}", q)
    log(f"will delete      : {len(to_delete)}", q)
    for r in to_delete:
        log(f"    - {r}", q)

    if not args.apply:
        log("\ndry run — nothing written. re-run with --apply\n", q)
        return 0

    for r in to_delete:
        (CONTENT / r).unlink(missing_ok=True)
    for dest, text in outputs.items():
        out = CONTENT / dest
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
    if wanted_assets:
        (CONTENT / ATTACH_DIR).mkdir(parents=True, exist_ok=True)
        for name, srcp in wanted_assets.items():
            shutil.copy2(VAULT / srcp, CONTENT / ATTACH_DIR / name)
    # prune now-empty directories
    for p in sorted(CONTENT.rglob("*"), key=lambda x: -len(x.parts)):
        if p.is_dir() and not any(p.iterdir()):
            p.rmdir()

    log(f"\nwrote {len(to_write)} notes, {len(wanted_assets)} attachments, deleted {len(to_delete)}\n", q)
    return 0


if __name__ == "__main__":
    sys.exit(main())
