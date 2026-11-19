#!/bin/bash
# merge_builders.sh: bring every standing builder branch into backdrop2/s11-full and push (the coordinator runs it
# whenever a builder reports BUILT). Builders own disjoint files, so merges are clean; a conflict stops the script.
set -e
cd "$(git rev-parse --show-toplevel)"
git fetch -q origin
git checkout -q backdrop2/s11-full
git merge -q --ff-only origin/backdrop2/s11-full 2>/dev/null || true
for b in s11-b-zion s11-b-stage s11-b-core s11-r7-ends s11-models; do
  if git rev-parse -q --verify "origin/backdrop2/$b" >/dev/null; then
    if [ -n "$(git log --oneline HEAD..origin/backdrop2/$b)" ]; then
      git merge -q --no-edit -m "Merge builder branch backdrop2/$b" "origin/backdrop2/$b" && echo "merged $b"
    fi
  fi
done
git push -q origin backdrop2/s11-full
git log --oneline -1
