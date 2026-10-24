# Student Controller Package and Submission Guide

**Status:** Organizer draft for V1.1. Follow the official event announcement if it changes any of these instructions.

This guide shows how to create a ROS 2 Python package, connect it to the competition simulator, and submit the version organizers should build. Your controller is a separate package. Do not edit the simulator package to add your controller.

## 1. The required ROS interface

The simulator and controller communicate through ROS 2 topics:

| Topic | Message type | Direction | Meaning |
|---|---|---|---|
| `/scan` | `sensor_msgs/msg/LaserScan` | Simulator → controller | LiDAR ranges and their angles |
| `/ego_racecar/odom` | `nav_msgs/msg/Odometry` | Simulator → controller | Simulated vehicle position and motion |
| `/drive` | `ackermann_msgs/msg/AckermannDriveStamped` | Controller → simulator | Requested steering and speed |

Steering is in **radians** and speed is in **metres per second**. Your controller sends a desired Ackermann steering angle and speed; it does not send PWM values. The simulator or vehicle interface handles converting drive commands into actuator signals.

Use the topic names and message types above unless the organizers publish a different interface for a particular stage. Use the stage’s permitted sensor information. In particular, do not assume a map or route is available in a stage where the rules withhold it.

## 2. Create a Python ROS package

Open a terminal and create a separate workspace for your controller:

~~~bash
source /opt/ros/jazzy/setup.bash
mkdir -p ~/controller_ws/src
cd ~/controller_ws/src
ros2 pkg create --build-type ament_python --license MIT \
  team_name_controller \
  --dependencies rclpy sensor_msgs nav_msgs ackermann_msgs
~~~

Replace `team_name_controller` with your team’s lowercase package name, using underscores instead of spaces. Keep the package name consistent in the commands and files below.

The command creates a package folder similar to this:

~~~text
controller_ws/
└── src/
    └── team_name_controller/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/
        └── team_name_controller/
            └── __init__.py
~~~

Create the Python node file:

~~~bash
cd ~/controller_ws/src/team_name_controller/team_name_controller
touch controller_node.py
~~~

### Register a command for your node

Open `~/controller_ws/src/team_name_controller/setup.py`. In the existing `entry_points` section inside `setup(...)`, register this command:

~~~python
entry_points={
    'console_scripts': [
        'controller = team_name_controller.controller_node:main',
    ],
},
~~~

Keep this block inside the existing `setup(...)` call. Do not add a second `entry_points` block after the final closing parenthesis.

The name on the left, `controller`, is the executable name. The part after `=` identifies the Python module and function: `team_name_controller/controller_node.py` and its `main()` function.

### Implement the ROS node

Your node needs to create:

- a subscription to `/scan`;
- a subscription to `/ego_racecar/odom` if your algorithm uses odometry;
- a publisher to `/drive`.

For `/scan`, use the sensor-data QoS profile so the subscription matches the simulator’s LiDAR publisher. A useful first check is to make the node receive scans and publish a **zero-speed** command. Then replace the placeholder behavior with your controller algorithm and test at low speed before increasing it.

Your `package.xml` must list every ROS package your Python code imports. The package creation command above covers the common interfaces for this competition. If you add another ROS message or package dependency, declare it in `package.xml` and tell the organizers before the submission deadline. Do not rely on installing undeclared packages during the event.

## Learning from the official F1TENTH labs

The [F1TENTH labs repository](https://github.com/f1tenth/f1tenth_labs_openrepo) offers examples of algorithms such as Follow the Gap, wall following, Pure Pursuit, and MPC.

**When adapting lab code, follow this guide’s required ROS topics, package dependencies, build steps, and submission rules. Lab code may not work here unchanged.**

## 3. Build your package

The simulator repository provides the ROS environment and Python virtual environment. Build your controller in its own workspace, using the simulator workspace as an underlay.

Replace `<competition-repo>` with the actual path where you cloned the competition repository:

~~~bash
source /opt/ros/jazzy/setup.bash
source <competition-repo>/starter_ws/.venv/bin/activate
source <competition-repo>/starter_ws/install/setup.bash

cd ~/controller_ws
python /usr/bin/colcon build --symlink-install
source install/setup.bash
~~~

For example, if the competition repository is in your home folder at `~/CIE-KFUPM-F1tenth-Autonomous-Racing-Competition`, use that path in the two `source` commands.

Confirm that ROS can see your executable:

~~~bash
ros2 pkg executables team_name_controller
~~~

You should see `team_name_controller controller`.

## 4. Test it with the simulator

Use two terminals.

**Terminal 1 — start the simulator:**

~~~bash
cd <competition-repo>
./scripts/launch_sim.sh
~~~

**Terminal 2 — source the environments and start your node:**

~~~bash
source /opt/ros/jazzy/setup.bash
source <competition-repo>/starter_ws/.venv/bin/activate
source <competition-repo>/starter_ws/install/setup.bash
source ~/controller_ws/install/setup.bash
ros2 run team_name_controller controller
~~~

Check the connections from another sourced terminal:

~~~bash
ros2 topic info /scan
ros2 topic info /ego_racecar/odom
ros2 topic info /drive
~~~

During a controller run, the controller should subscribe to the sensor topics and publish to `/drive`; the simulator should subscribe to `/drive`. Stop the controller with `Ctrl+C`. Stop any teleoperation process before starting it: only one controller may publish to `/drive` during a run.

## 5. Rules your package must follow

- Build as a ROS 2 Jazzy `ament_python` package.
- Provide one executable named `controller`, runnable with `ros2 run <your_package> controller`.
- Subscribe to the required topic names and message types listed in Section 1.
- Publish valid `AckermannDriveStamped` commands to `/drive`; set the message timestamp and use radians and metres per second.
- Respect the speed cap announced for the stage. Start testing at low speed.
- Keep the node running and producing fresh commands while the attempt is active. If sensor data is missing or invalid, use a safe response such as stopping.
- Declare dependencies in `package.xml`. Do not require organizers to guess which packages to install.
- Do not edit or replace the simulator, maps, race monitor, official launch files, or scoring code.
- Do not publish from more than one controller to `/drive` during an attempt.
- Do not change source code or controller settings during an official attempt.
- Follow the information and map restrictions for the active stage, including the hidden-track restrictions where applicable.

## 6. Submit the exact version you want tested

### Option A: Git repository

Submit:

1. The repository URL.
2. The full commit ID for the version to build (40 hexadecimal characters).
3. The package name and the command to run it: `ros2 run <your_package> controller`.
4. A short README listing dependencies, build/run steps, configurable parameters, and the maximum speed your controller may request.

The commit ID identifies one exact saved snapshot. Organizers will use that snapshot even if you continue making changes in your repository afterward. Do not submit only a branch name such as `main`, because that branch can move.

### Option B: USB drive

Bring a ZIP containing the controller package source and its README. Name it with your team name and submission version, for example `TeamBlue_controller_submission1.zip`. Include the package files needed to build it: `package.xml`, `setup.py`, `setup.cfg`, the `resource/` marker, and your Python source files.

Do **not** include generated `build/`, `install/`, or `log/` folders, a Python virtual environment, or the simulator itself. After the submission deadline, the submitted copy is the version organizers will build.

## What organizers will do

Organizers will place the submitted package source in a separate workspace on the competition laptop, build it against the installed ROS 2 Jazzy and competition simulator, and run the declared controller command. They will not need to merge your controller into the simulator source.

A package that builds only on one team member’s machine, depends on undeclared software, uses different topic names, or needs manual source edits before launch is not ready for submission. Test from a clean copy of your submitted source before the deadline.
