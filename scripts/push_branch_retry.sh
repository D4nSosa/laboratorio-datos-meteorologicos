#!/usr/bin/env bash
set -euo pipefail
target="${TARGET_BRANCH:?TARGET_BRANCH is required}"
for attempt in $(seq 1 12); do
  echo "Push attempt ${attempt}/12 to ${target}"
  git fetch origin "${target}"
  if ! git rebase FETCH_HEAD; then
    echo "Rebase conflict; aborting attempt ${attempt}"
    git rebase --abort || true
    sleep 3
    continue
  fi
  if git push origin "HEAD:${target}"; then
    echo "Push succeeded."
    exit 0
  fi
  echo "Remote branch moved during push; retrying after fetch/rebase."
  sleep 3
done
echo "Could not push after 12 retries."
exit 1
