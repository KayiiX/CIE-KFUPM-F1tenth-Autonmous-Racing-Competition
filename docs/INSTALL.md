# Installation guide

These instructions reproduce the native installation validated for the
competition starter workspace.

## 1. Supported system

- Ubuntu 24.04.5 LTS, x86_64
- ROS 2 Jazzy
- Bash shell
- Native installation, not Docker

Check the machine:

```bash
lsb_release -a
uname -m
locale
```

A UTF-8 locale is required. An empty `LC_ALL` is normal when categories inherit
from `LANG`.

## 2. Install all system prerequisites

Install the Ubuntu packages required to add the ROS repository, clone and build
the workspace, and create the Python virtual environment:

```bash
sudo apt update
sudo apt install -y \
  locales \
  software-properties-common \
  curl \
  ca-certificates \
  git \
  build-essential \
  pkg-config \
  python3 \
  python3-dev \
  python3-pip \
  python3-venv
```

Configure a UTF-8 locale if the machine does not already use one:

```bash
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
locale
```

`LANG=en_US.UTF-8` is expected. An empty `LC_ALL` is also valid when locale
categories inherit from `LANG`.

## 3. Install ROS 2 Jazzy

Enable Universe and install the ROS apt-source helper:

```bash
sudo add-apt-repository universe
sudo apt update

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F '"tag_name"' | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
```

Install ROS 2 Desktop and its development tools:

```bash
sudo apt install -y ros-jazzy-desktop ros-dev-tools
```

Load and verify ROS:

```bash
source /opt/ros/jazzy/setup.bash
echo "$ROS_DISTRO"
ros2 pkg prefix rviz2
```

Expected:

```text
jazzy
/opt/ros/jazzy
```

Initialize rosdep once:

```bash
sudo rosdep init
rosdep update
```

If rosdep reports that `20-default.list` already exists, continue with
`rosdep update`.

At this point, the manually installed prerequisites are complete. During
workspace setup, `rosdep` installs package-level dependencies such as
Ackermann messages, Nav2 map server, robot state publisher, Eigen, RViz, and
the Foxglove bridge. The setup script also creates the virtual environment and
installs the pinned Python simulator dependencies inside it.

## 4. Verify prerequisites

```bash
git --version
python3 --version
python3 -m venv --help >/dev/null && echo "python3-venv: OK"
rosdep --version
colcon --help >/dev/null && echo "colcon: OK"
test -f /opt/ros/jazzy/setup.bash && echo "ROS 2 Jazzy: OK"
```

If all commands finish without an error, continue with the repository setup.

## 5. Clone this repository

```bash
git clone https://github.com/KayiiX/CIE-KFUPM-F1tenth-Autonomous-Racing-Competition.git
cd CIE-KFUPM-F1tenth-Autonomous-Racing-Competition
```

## 6. Set up and build

```bash
./scripts/setup_workspace.sh
```

The script:

1. clones the Jazzy ROS bridge at the tested commit;
2. clones the JAX simulator backend at the tested commit;
3. creates `starter_ws/.venv` with access to system ROS Python packages;
4. pins setuptools below version 80;
5. installs the simulator backend and Python compatibility fixes;
6. resolves ROS dependencies with rosdep;
7. builds the workspace through the virtual-environment Python interpreter.

## 7. Launch

Simulator:

```bash
./scripts/launch_sim.sh
```

RViz opens automatically with the competition simulator and shows a race-status
label near the car. The first finish-line crossing is an out-lap; it starts the
live stopwatch, and the next crossing completes lap 1. The Foxglove bridge also
runs in the background and remains available at `ws://localhost:8765`, but the
browser is not opened automatically.

Pure Pursuit, in another terminal:

```bash
./scripts/launch_pure_pursuit.sh
```

The controller starts moving the car immediately.

## 8. Validate topics

With the simulator running:

```bash
./scripts/smoke_test.sh
```

Manual checks:

```bash
ros2 topic info /scan
ros2 topic info /ego_racecar/odom
ros2 topic info /drive
```

Expected:

- `/scan`: one publisher;
- `/ego_racecar/odom`: one publisher;
- `/drive`: one simulator subscriber;
- when Pure Pursuit runs, `/drive` also has one publisher.

## 9. Validate lap timing

The simulator publishes authoritative completed-lap data. The competition race
monitor adds a live stopwatch, best time, and session history:

```bash
ros2 topic echo /competition/race_status
ros2 topic echo /competition/current_lap_time
ros2 topic echo /competition/lap_count
ros2 topic echo /competition/last_lap_time
ros2 topic echo /competition/best_lap_time
ros2 topic echo /competition/lap_history
```

Expected sequence:

1. `OUT_LAP` after startup;
2. `RACING` after the first finish-line crossing;
3. `/competition/lap_count` becomes `1` after the next crossing;
4. last, best, and history receive the simulator's completed-lap time.

Using RViz **2D Pose Estimate** resets the timing session along with the car.

## 10. RViz

The normal simulator launch starts RViz automatically. To restart RViz
manually while the simulator is still running:

```bash
source /opt/ros/jazzy/setup.bash
source starter_ws/.venv/bin/activate
source starter_ws/install/setup.bash

rviz2 -d starter_ws/src/competition_bringup/config/competition.rviz
```

A message containing the following can appear when the map first renders:

```text
active samplers with a different type refer to the same texture image unit
```

It is non-blocking when the map, vehicle, and LiDAR remain visible and RViz
continues running.

## 11. Foxglove

Connect <https://app.foxglove.dev> to:

```text
ws://localhost:8765
```

Import the supplied layout:

```text
starter_ws/src/f1tenth_gym_ros/config/foxglove/gym_bridge_foxglove.json
```

## Troubleshooting

### The bridge cannot import f1tenth_gym

Symptom:

```text
ModuleNotFoundError: No module named 'f1tenth_gym'
```

Rebuild using the virtual-environment interpreter:

```bash
cd starter_ws
source /opt/ros/jazzy/setup.bash
source .venv/bin/activate
python /usr/bin/colcon build --symlink-install
```

Verify the generated bridge shebang starts with the workspace virtual
environment path.

### Numba fails while importing coverage

Symptom:

```text
AttributeError: module 'coverage.types' has no attribute 'Tracer'
```

Repair:

```bash
source starter_ws/.venv/bin/activate
python -m pip install --upgrade 'coverage>=7.6'
python -m pip check
```

### setuptools conflict

```text
colcon-core requires setuptools<80
```

Repair:

```bash
source starter_ws/.venv/bin/activate
python -m pip install 'setuptools==79.0.1'
python -m pip check
```

### PyNaCl requires cffi

```bash
source starter_ws/.venv/bin/activate
python -m pip install --upgrade cffi
python -m pip check
```
