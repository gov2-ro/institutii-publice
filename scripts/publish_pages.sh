#!/bin/sh
# Publish the explorer to GitHub Pages (https://org.gov2.ro).
#
# The site is the committed explorer/ of HEAD plus the generated data (metadata.json, rows.json, institutii.csv).
# In the repo those two are symlinks into the ignored data/consolidated/; this script copies the real files.
# CI cannot rebuild the data (the inputs stay out of git), so publishing runs from the owner's machine.
#
# Preflight (also in the dry run): the tests pass; scripts/, curation/, explorer/ and institutii.csv have no
# uncommitted change; dataset.build_hash of metadata.json equals the hash of the same files at HEAD.
# After a real push, the script polls the live metadata.json for 3 minutes and prints the record count.
#
# The gh-pages branch holds one commit, replaced on each publish (force push): the data does not
# accumulate in git history. The commit message names the source commit and the data generation time.
#
#   sh scripts/publish_pages.sh --dry-run   # build the site in a temp folder, print its path and size, push nothing
#   sh scripts/publish_pages.sh             # build and force-push to origin/gh-pages
set -eu

DOMAIN=org.gov2.ro
REMOTE=origin
BRANCH=gh-pages
ROOT=$(git rev-parse --show-toplevel)
cd "$ROOT"

dry=0
[ "${1:-}" = "--dry-run" ] && dry=1

# Preflight. It runs in the dry run too. Each check names its fix.
dirty=$(git status --porcelain -- scripts curation explorer data/consolidated/institutii.csv)
if [ -n "$dirty" ]; then
  echo "scripts/, curation/, explorer/ or data/consolidated/institutii.csv has uncommitted changes. Commit them first: the site must match a commit." >&2
  echo "$dirty" >&2
  exit 1
fi
for f in metadata.json rows.json institutii.csv; do
  [ -s "data/consolidated/$f" ] || { echo "missing data/consolidated/$f. Run: uv run scripts/consolidate.py" >&2; exit 1; }
done
if grep -q '"/Users/\|"/home/' data/consolidated/metadata.json; then
  echo "metadata.json contains an absolute local path. Fix write_explorer_data before publishing." >&2
  exit 1
fi

site=$(mktemp -d)
index=$(mktemp)
headfiles=$(mktemp -d)
testlog=$(mktemp)
trap 'rm -rf "$site" "$index" "$headfiles" "$testlog"' EXIT

if ! python3 -m unittest discover -s tests >"$testlog" 2>&1; then
  tail -n 30 "$testlog" >&2
  echo "The tests fail. Fix them, then run: python3 -m unittest discover -s tests" >&2
  exit 1
fi

# The build hash must equal the hash of the same files at HEAD. build_hash in consolidate.py is the one rule.
built=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["dataset"].get("build_hash", ""))' data/consolidated/metadata.json)
if [ -z "$built" ]; then
  echo "metadata.json has no dataset.build_hash. Run: uv run scripts/consolidate.py" >&2
  exit 1
fi
git archive HEAD scripts/consolidate.py curation | tar -x -C "$headfiles"
committed=$(python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1] + "/scripts"); import consolidate; print(consolidate.build_hash(sys.argv[1]))' "$headfiles") || {
  echo "HEAD cannot compute the build hash (no build_hash in scripts/consolidate.py at HEAD). Commit the function." >&2
  exit 1
}
if [ "$built" != "$committed" ]; then
  echo "The data does not come from the committed code. Build hash of the data: $built. Build hash of HEAD: $committed." >&2
  echo "Run: uv run scripts/consolidate.py. The files of the build must equal the committed files." >&2
  exit 1
fi

git archive HEAD explorer | tar -x -C "$site" --strip-components 1
rm -f "$site/metadata.json" "$site/rows.json"
cp data/consolidated/metadata.json data/consolidated/rows.json data/consolidated/institutii.csv "$site/"
echo "$DOMAIN" > "$site/CNAME"
touch "$site/.nojekyll"

generated=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["dataset"]["generated_at"])' "$site/metadata.json")
src=$(git rev-parse --short HEAD)
echo "site: $(du -sh "$site" | cut -f1), $(find "$site" -type f | wc -l | tr -d ' ') files; source $src; data $generated" >&2

if [ $dry = 1 ]; then
  trap - EXIT
  rm -rf "$index" "$headfiles" "$testlog"
  echo "dry run: site built in $site (not pushed)" >&2
  exit 0
fi

# commit the folder without touching the working tree: a temporary index, then an orphan commit
rm -f "$index"
GIT_INDEX_FILE="$index" GIT_WORK_TREE="$site" git add -A
tree=$(GIT_INDEX_FILE="$index" git write-tree)
commit=$(git commit-tree "$tree" -m "Publish $src (data $generated)")
git update-ref "refs/heads/$BRANCH" "$commit"
git push --force "$REMOTE" "$BRANCH"
echo "published $src to $REMOTE/$BRANCH -> https://$DOMAIN" >&2

# Check the live site: poll for at most 3 minutes. A lag of Pages or Cloudflare gives a warning, not a failure.
live_url="https://$DOMAIN/metadata.json"
tries=0
while [ $tries -lt 18 ]; do
  live=$(curl -fsS --max-time 15 "$live_url?t=$(date +%s)" 2>/dev/null | python3 -c 'import json, sys; print(json.load(sys.stdin)["dataset"]["generated_at"])' 2>/dev/null || true)
  if [ "$live" = "$generated" ]; then
    count=$(curl -fsS --max-time 60 "https://$DOMAIN/rows.json?t=$(date +%s)" | python3 -c 'import json, sys; print(len(json.load(sys.stdin)))' 2>/dev/null) || count="an unknown number of"
    echo "live check passed: https://$DOMAIN serves data $generated with $count records" >&2
    exit 0
  fi
  tries=$((tries + 1))
  sleep 10
done
echo "WARNING: after 3 minutes https://$DOMAIN does not serve data $generated (it serves: ${live:-nothing}). The push is done. Pages or Cloudflare can lag: check the site later." >&2
