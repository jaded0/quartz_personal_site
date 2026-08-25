#!/usr/bin/env bash
# Sync `publish: true` notes out of the vault and, if anything changed, push.
# GitHub Actions builds and deploys from there.
#
# Run by hand, or on a timer via garden-sync.service.
set -euo pipefail

SITE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SITE"

BRANCH="v5"
if [[ "$(git rev-parse --abbrev-ref HEAD)" != "$BRANCH" ]]; then
  echo "publish: refusing to run, not on $BRANCH" >&2
  exit 1
fi

# The sync exits nonzero (and writes nothing) if a flagged note looks like it
# contains a credential. `set -e` turns that into a failed run, which is the
# safe direction: nothing gets published.
python3 sync_from_vault.py --apply

if git diff --quiet -- content && git diff --quiet --cached -- content && \
   [[ -z "$(git status --porcelain -- content)" ]]; then
  echo "publish: no content changes"
  exit 0
fi

git add -A content
COUNT=$(git diff --cached --numstat -- content | wc -l)
git -c user.name=jaden -c user.email=jaded79@student.byu.edu \
    commit -q -m "garden: sync $COUNT changed file(s) from vault"
git push -q origin "$BRANCH"
echo "publish: pushed $COUNT changed file(s)"
