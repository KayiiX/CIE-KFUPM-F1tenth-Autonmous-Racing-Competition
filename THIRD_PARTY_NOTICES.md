# Third-party notices

This repository includes and integrates software and data from the following
projects.

## F1TENTH Gym ROS

- Project: <https://github.com/f1tenth/f1tenth_gym_ros>
- Validated branch: `dev-jazzy`
- Validated commit: `2c019810b4098ed82d44cad1d7d282a2dfc12421`
- License: MIT

The simulator repository is cloned by the setup script and is not vendored here.
The Levine centerline used to produce
`starter_ws/src/pure_pursuit/racelines/levine_centerline_pp.csv` comes from
this validated revision. The conversion retains the first two columns and adds
a conservative `1.5 m/s` reference velocity column.

## F1TENTH Gym

- Project: <https://github.com/f1tenth/f1tenth_gym>
- Validated branch: `dev-jax`
- Validated commit: `ec3b1a4693ed20317e42e57a9454d94b824cec81`
- License: MIT

The simulator backend is cloned by the setup script and is not vendored here.

## Waterloo Pure Pursuit

- Project: <https://github.com/CL2-UWaterloo/f1tenth_ws>
- Source package: `src/pure_pursuit`
- Source commit: `c20cf63d04b9841ffdb6b2f963bd737d78074136`
- License: MIT
- Original copyright: xLab for Safe Autonomous Systems

The vendored starter package preserves its upstream `LICENSE`. Competition
adaptations include Jazzy dependency metadata, portable installed waypoint
paths, Levine waypoints, a path-length-safe search window, and conservative
simulation tuning.

