#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WS="$REPO_ROOT/starter_ws"

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 TEAM_ID [CONTROLLER_REVISION]"
  exit 2
fi

TEAM_ID="$1"
CONTROLLER_REVISION="${2:-unspecified}"
if [[ ! "$TEAM_ID" =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]]; then
  echo "TEAM_ID may contain only letters, numbers, dot, underscore, and hyphen."
  exit 2
fi

source_environment() {
  set +u
  # shellcheck disable=SC1090
  source "$1"
  set -u
}

source_environment /opt/ros/jazzy/setup.bash
source_environment "$WS/.venv/bin/activate"
source_environment "$WS/install/setup.bash"

TOPIC_LIST="$(ros2 topic list)"
for required_topic in /scan /ego_racecar/odom /drive; do
  if ! grep -Fxq "$required_topic" <<< "$TOPIC_LIST"; then
    echo "Required topic is missing: $required_topic"
    echo "Start the simulator and controller before recording."
    exit 1
  fi
done

RUN_ID="${TEAM_ID}_$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$REPO_ROOT/run_logs/$RUN_ID"
mkdir -p "$RUN_DIR"

cat > "$RUN_DIR/run_metadata.txt" <<EOF
team_id=$TEAM_ID
controller_revision=$CONTROLLER_REVISION
recording_started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)
repository_release=v1
EOF

echo "Recording run $RUN_ID"
echo "Press Ctrl+C to stop the bag cleanly."
echo "Output: $RUN_DIR/bag"

# Keep the hidden occupancy map out of the run record.
ros2 bag record -o "$RUN_DIR/bag" \
  /scan \
  /ego_racecar/odom \
  /drive \
  /ego_racecar/lap_time \
  /ego_racecar/lap_count \
  /ego_racecar/collision \
  /competition/current_lap_time \
  /competition/last_lap_time \
  /competition/best_lap_time \
  /competition/lap_count \
  /competition/lap_history \
  /competition/collision_count \
  /competition/race_status
