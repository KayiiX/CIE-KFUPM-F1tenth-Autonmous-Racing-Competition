#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WS="$REPO_ROOT/starter_ws"

source_environment() {
  set +u
  # shellcheck disable=SC1090
  source "$1"
  set -u
}

source_environment /opt/ros/jazzy/setup.bash
source_environment "$WS/.venv/bin/activate"
source_environment "$WS/install/setup.bash"

require_node() {
  local node="$1"
  if ! ros2 node list | grep -Fxq "$node"; then
    echo "Missing required node: $node"
    return 1
  fi
}

require_topic() {
  local topic="$1"
  if ! ros2 topic list | grep -Fxq "$topic"; then
    echo "Missing required topic: $topic"
    return 1
  fi
}

require_node /bridge
require_node /map_server
require_node /race_monitor
require_node /rviz2
require_topic /scan
require_topic /ego_racecar/odom
require_topic /drive
require_topic /map
require_topic /tf
require_topic /tf_static
require_topic /ego_racecar/lap_count
require_topic /ego_racecar/lap_time
require_topic /competition/current_lap_time
require_topic /competition/last_lap_time
require_topic /competition/best_lap_time
require_topic /competition/lap_count
require_topic /competition/race_status

echo "Core nodes and topics are present."
echo
ros2 topic info /scan
ros2 topic info /ego_racecar/odom
ros2 topic info /drive
ros2 topic echo /competition/race_status --once
ros2 topic echo /competition/lap_count --once
