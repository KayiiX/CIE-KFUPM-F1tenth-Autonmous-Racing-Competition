#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
WS="$REPO_ROOT/starter_ws"
ROS_SETUP="/opt/ros/jazzy/setup.bash"
ROS_REPO="$WS/src/f1tenth_gym_ros"
GYM_REPO="$ROS_REPO/f1tenth_gym"

ROS_COMMIT="2c019810b4098ed82d44cad1d7d282a2dfc12421"
GYM_COMMIT="ec3b1a4693ed20317e42e57a9454d94b824cec81"

# ROS and colcon-generated setup files may read variables before defining them.
# Temporarily disable Bash nounset while sourcing those trusted environment files.
source_environment() {
  set +u
  # shellcheck disable=SC1090
  source "$1"
  set -u
}

if [[ ! -f "$ROS_SETUP" ]]; then
  echo "ROS 2 Jazzy was not found at $ROS_SETUP."
  echo "Follow docs/INSTALL.md before running this script."
  exit 1
fi

if [[ "$(uname -m)" != "x86_64" ]]; then
  echo "This setup was validated only on x86_64."
  exit 1
fi

source_environment "$ROS_SETUP"
mkdir -p "$WS/src"

if [[ ! -d "$ROS_REPO/.git" ]]; then
  git clone --branch dev-jazzy     https://github.com/f1tenth/f1tenth_gym_ros.git "$ROS_REPO"
fi

if [[ -n "$(git -C "$ROS_REPO" status --porcelain --untracked-files=no)" ]]; then
  echo "Refusing to change a modified simulator checkout: $ROS_REPO"
  exit 1
fi

git -C "$ROS_REPO" fetch origin dev-jazzy
git -C "$ROS_REPO" checkout --detach "$ROS_COMMIT"

if [[ ! -d "$GYM_REPO/.git" ]]; then
  git clone --branch dev-jax     https://github.com/f1tenth/f1tenth_gym.git "$GYM_REPO"
fi

if [[ -n "$(git -C "$GYM_REPO" status --porcelain)" ]]; then
  echo "Refusing to change a modified simulator backend: $GYM_REPO"
  exit 1
fi

git -C "$GYM_REPO" fetch origin dev-jax
git -C "$GYM_REPO" checkout --detach "$GYM_COMMIT"

if [[ ! -d "$WS/.venv" ]]; then
  python3 -m venv --system-site-packages "$WS/.venv"
fi

source_environment "$WS/.venv/bin/activate"

python -m pip install --upgrade pip wheel
python -m pip install 'setuptools==79.0.1'
python -m pip install --upgrade 'coverage>=7.6' cffi
python -m pip install --editable "$GYM_REPO"
python -m pip check

if [[ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]]; then
  echo "rosdep is not initialized. Run: sudo rosdep init"
  exit 1
fi

rosdep update
rosdep install   --from-paths "$WS/src"   --ignore-src   --rosdistro jazzy   -r -y

cd "$WS"
python /usr/bin/colcon build --symlink-install
source_environment "$WS/install/setup.bash"

ros2 pkg prefix f1tenth_gym_ros
ros2 pkg prefix pure_pursuit
python -c "import f1tenth_gym; print(f1tenth_gym.__file__)"
python -m pip check

echo
echo "Setup completed successfully."
echo "Start the simulator with: $REPO_ROOT/scripts/launch_sim.sh"

