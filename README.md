# CIE-KFUPM F1TENTH Autonomous Racing Competition

Native ROS 2 starter workspace for the CIE-KFUPM F1TENTH Autonomous Racing
Competition.

This repository gives students:

- a validated Ubuntu 24.04 and ROS 2 Jazzy simulator setup;
- pinned F1TENTH simulator revisions;
- RViz and Foxglove visualization instructions;
- a live lap timer, completed-lap counter, best time, and lap history;
- a conservative Pure Pursuit controller for the Levine map;
- repeatable setup, launch, stop, and smoke-test commands.

> The Pure Pursuit package is starter code, not a competition solution. Teams
> should understand, test, and improve it.

## Validated platform

- Ubuntu 24.04.5 LTS, x86_64
- ROS 2 Jazzy Jalisco
- Native installation
- Python virtual environment with system ROS packages
- RViz and Foxglove
- One simulated vehicle on the Levine map

## Quick start

First install ROS 2 Jazzy Desktop and the prerequisites in
[docs/INSTALL.md](docs/INSTALL.md). Then:

```bash
git clone https://github.com/KayiiX/CIE-KFUPM-F1tenth-Autonomous-Racing-Competition.git
cd CIE-KFUPM-F1tenth-Autonomous-Racing-Competition

./scripts/setup_workspace.sh
```

### Terminal 1: simulator and RViz

```bash
./scripts/launch_sim.sh
```

RViz opens automatically with the map, vehicle, LiDAR, and race-status display.
The first finish-line crossing completes the out-lap and starts the live timer.

Foxglove remains available as an optional second visualization:

1. Open <https://app.foxglove.dev>.
2. Select **Open connection** and **Foxglove WebSocket**.
3. Connect to `ws://localhost:8765`.
4. Import:
   `starter_ws/src/f1tenth_gym_ros/config/foxglove/gym_bridge_foxglove.json`.

### Terminal 2: Pure Pursuit kickstart

The car starts moving immediately:

```bash
./scripts/launch_pure_pursuit.sh
```

Stop the controller with `Ctrl+C`, then stop the retained drive command:

```bash
./scripts/stop_car.sh
```

Run the interface smoke test while the simulator is active:

```bash
./scripts/smoke_test.sh
```

## Reset the car

For an exact reset, stop the simulator with `Ctrl+C` and relaunch it.

For a live reposition, stop the car, then use RViz **2D Pose Estimate** to publish
a pose on `/initialpose`.

## ROS interface

| Topic | Type | Direction |
|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | Simulator output |
| `/ego_racecar/odom` | `nav_msgs/msg/Odometry` | Simulator output |
| `/drive` | `ackermann_msgs/msg/AckermannDriveStamped` | Controller input |
| `/waypoints` | `visualization_msgs/msg/MarkerArray` | Starter visualization |
| `/ego_racecar/lap_time` | `std_msgs/msg/Float32` | Simulator output |
| `/ego_racecar/lap_count` | `std_msgs/msg/Int32` | Simulator output |
| `/ego_racecar/collision` | `std_msgs/msg/Bool` | Simulator output |
| `/competition/current_lap_time` | `std_msgs/msg/Float32` | Live current lap |
| `/competition/last_lap_time` | `std_msgs/msg/Float32` | Last completed lap |
| `/competition/best_lap_time` | `std_msgs/msg/Float32` | Best completed lap |
| `/competition/lap_count` | `std_msgs/msg/Int32` | Completed laps |
| `/competition/lap_history` | `std_msgs/msg/Float32MultiArray` | Completed times |
| `/competition/race_status` | `std_msgs/msg/String` | Monitor state |

## Tested revisions

| Component | Branch | Commit |
|---|---|---|
| `f1tenth/f1tenth_gym_ros` | `dev-jazzy` | `2c019810b4098ed82d44cad1d7d282a2dfc12421` |
| `f1tenth/f1tenth_gym` | `dev-jax` | `ec3b1a4693ed20317e42e57a9454d94b824cec81` |
| Waterloo Pure Pursuit source | `main` | `c20cf63d04b9841ffdb6b2f963bd737d78074136` |

## Official simulator reference

This starter workspace uses the official
[F1TENTH Gym ROS repository (`dev-jazzy` branch)](https://github.com/f1tenth/f1tenth_gym_ros/tree/dev-jazzy).
The setup script clones that repository and checks out the tested revision listed
above so every student uses the same simulator version.

## Repository layout

```text
.
├── README.md
├── THIRD_PARTY_NOTICES.md
├── docs/
│   └── INSTALL.md
├── scripts/
│   ├── launch_pure_pursuit.sh
│   ├── launch_sim.sh
│   ├── setup_workspace.sh
│   ├── smoke_test.sh
│   └── stop_car.sh
└── starter_ws/
    └── src/
        ├── competition_bringup/
        ├── race_monitor/
        └── pure_pursuit/
```

The setup script creates `starter_ws/.venv`, clones the pinned simulator source
under `starter_ws/src`, and generates `build`, `install`, and `log`. Those
machine-generated paths are intentionally ignored by Git.

## Safety

The simulator is not a substitute for physical-car safety validation. Before
using student code on a real vehicle, add speed limits, a physical emergency
stop, a dead-man mechanism, controlled low-speed tests, and trackside
supervision.
