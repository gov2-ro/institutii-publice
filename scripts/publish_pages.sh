#!/bin/sh
# Publish the explorer to GitHub Pages (https://org.gov2.ro).
#
# The site is the committed explorer/ of HEAD plus the generated data (metadata.json, rows.json).
# In the repo those two are symlinks into the ignored data/consolidated/; this script copies the real files.
# CI cannot rebuild the data (the inputs stay out of git), so publishing runs from the owner's machine.
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

if ! git diff --quiet HEAD -- explorer; then
  echo "explorer/ has uncommitted changes. Commit them first: the site must match a commit." >&2
  exit 1
fi
for f in metadata.json rows.json; do
  [ -s "data/consolidated/$f" ] || { echo "missing data/consolidated/$f. Run: uv run scripts/consolidate.py" >&2; exit 1; }
done
if grep -q '"/Users/\|"/home/' data/consolidated/metadata.json; then
  echo "metadata.json contains an absolute local path. Fix write_explorer_data before publishing." >&2
  exit 1
fi

site=$(mktemp -d)
index=$(mktemp)
trap 'rm -rf "$site" "$index"' EXIT
git archive HEAD explorer | tar -x -C "$site" --strip-components 1
rm -f "$site/metadata.json" "$site/rows.json"
cp data/consolidated/metadata.json data/consolidated/rows.json "$site/"
echo "$DOMAIN" > "$site/CNAME"
touch "$site/.nojekyll"

generated=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["dataset"]["generated_at"])' "$site/metadata.json")
src=$(git rev-parse --short HEAD)
echo "site: $(du -sh "$site" | cut -f1), $(find "$site" -type f | wc -l | tr -d ' ') files; source $src; data $generated" >&2

if [ $dry = 1 ]; then
  trap - EXIT
  rm -f "$index"
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
