#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WS="$REPO_ROOT/starter_ws"

source /opt/ros/jazzy/setup.bash
source "$WS/.venv/bin/activate"
source "$WS/install/setup.bash"

ros2 topic pub --once   /drive ackermann_msgs/msg/AckermannDriveStamped   "{drive: {steering_angle: 0.0, speed: 0.0}}"

