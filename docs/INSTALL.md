# Installation guide

These instructions reproduce the native installation validated for the
competition starter workspace.

## 1. Supported system

- Ubuntu 24.04 LTS, x86_64
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

## 2. Update Ubuntu

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

## 3. Install ROS 2 Jazzy

Enable Universe and install the ROS apt-source helper:

```bash
sudo apt install software-properties-common curl -y
sudo add-apt-repository universe
sudo apt update

export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F '"tag_name"' | awk -F'"' '{print $4}')

curl -L -o /tmp/ros2-apt-source.deb \
  "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"

sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update
sudo apt upgrade -y
```

Install ROS, development tools, Git, and virtual-environment support:

```bash
sudo apt install ros-jazzy-desktop ros-dev-tools git python3-venv -y
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

## 4. Clone this repository

```bash
git clone https://github.com/KayiiX/CIE-KFUPM-F1tenth-Autonmous-Racing-Competition.git
cd CIE-KFUPM-F1tenth-Autonmous-Racing-Competition
```

## 5. Set up and build

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

## 6. Launch

Simulator:

```bash
./scripts/launch_sim.sh
```

Pure Pursuit, in another terminal:

```bash
./scripts/launch_pure_pursuit.sh
```

The controller starts moving the car immediately.

## 7. Validate topics

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

## 8. RViz

```bash
source /opt/ros/jazzy/setup.bash
source starter_ws/.venv/bin/activate
source starter_ws/install/setup.bash

rviz2 -d starter_ws/src/f1tenth_gym_ros/config/rviz/gym_bridge.rviz
```

A message containing the following can appear when the map first renders:

```text
active samplers with a different type refer to the same texture image unit
```

It is non-blocking when the map, vehicle, and LiDAR remain visible and RViz
continues running.

## 9. Foxglove

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

