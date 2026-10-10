# Pure Pursuit kickstart

This package is a conservative reference controller for the Levine simulator map.
It subscribes to `/ego_racecar/odom`, publishes Ackermann commands on `/drive`,
and publishes waypoint markers for RViz or Foxglove.

Build from the repository root:

```bash
python /usr/bin/colcon build --symlink-install --packages-select pure_pursuit
source install/setup.bash
```

Start the simulator first, then launch the controller:

```bash
ros2 launch pure_pursuit sim_pure_pursuit_launch.py
```

The car starts moving immediately. Stop the controller with `Ctrl+C`, then send
a zero-speed command as documented in the top-level README.

This is starter code, not a competition solution. Students are expected to
understand, test, and improve it.

