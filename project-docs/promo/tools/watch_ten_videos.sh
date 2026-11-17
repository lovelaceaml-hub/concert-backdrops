#!/usr/bin/env bash
# Emit one line for each finished full video of the ten films (branches ten/*) that has a share copy.
# Line format: RUN <run id> <branch> <share artifact id> <artifact name>
SEEN=/tmp/claude-0/-home-user-concert-backdrops/db54c2bc-2c12-56a6-9c8e-79b78a0f3317/scratchpad/tools/ten_seen.txt
touch "$SEEN"
R=repos/lovelaceaml-hub/concert-backdrops
while true; do
  gh api "$R/actions/runs?status=completed&per_page=60" \
    --jq '.workflow_runs[] | select(.head_branch|test("^(master/|engine-p3d-(styles|bodies|words|brand)$)")) | select(.conclusion=="success") | "\(.id) \(.head_branch)"' 2>/dev/null |
  while read -r id br; do
    grep -qx "$id" "$SEEN" && continue
    line=$(gh api "$R/actions/runs/$id/artifacts" --jq '.artifacts[] | select(.name|endswith("(share)")) | "\(.id)\t\(.name)"' 2>/dev/null | head -1)
    echo "$id" >> "$SEEN"
    [[ -n "$line" ]] || continue
    aid=${line%%$'\t'*}; name=${line#*$'\t'}
    echo "RUN $id $br $aid $name"
  done
  sleep 90
done
