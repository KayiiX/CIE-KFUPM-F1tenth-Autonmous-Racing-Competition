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

echo "Warning: Pure Pursuit starts moving the simulated car immediately."
exec ros2 launch pure_pursuit sim_pure_pursuit_launch.py

