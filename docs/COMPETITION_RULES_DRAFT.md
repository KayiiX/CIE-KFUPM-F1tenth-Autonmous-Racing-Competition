# CIE-KFUPM F1TENTH Competition — Proposed Stages and Rules

**Status:** Organizer draft for the first edition. Adopt only after organizer review.  
**Repository baseline:** frozen `v1` branch, commit `648778c`.  
**Development:** stage V1.1 changes on a separate branch; do not change the student-facing V1 release.

This document turns the proposed competition format into a concrete, reviewable default. Dates and venue details are announced separately. The intended field is approximately 20–30 teams, with about 3–4 weeks between major stages for teams to improve their controllers.

## Competition stages

### Stage 0 — Workshop and simulator onboarding (unscored)

All teams install and run the same V1 environment. Organizers demonstrate the simulator, ROS topics, the race dashboard, and PS5 teleoperation. Teams may practice and modify their controller in the practice workspace.

This stage is for learning and technical checks; it does not affect ranking.

### Stage 1 — Clean-lap qualification (simulation)

- Track: the simple Levine course supplied in the starter environment.
- Each team receives up to **three official attempts**.
- An attempt is a maximum of **three timed laps**, following the out-lap behavior of the official race monitor.
- A team qualifies by completing all three laps with **zero recorded collisions** in at least one attempt.
- Teams that qualify advance to Stage 2.

### Stage 2 — Known-track time trial (simulation)

- Track: the announced Levine obstacle course, initially proposed as `levine_blocked`.
- The map and official route are supplied before the stage.
- Each team receives up to **three official attempts** of three timed laps.
- A collision invalidates that attempt; it does not invalidate a separate clean attempt.
- The team's result is the fastest total time across its valid three-lap attempts.
- The **qualified teams** advance to Stage 3. Ties are resolved by the fastest single lap, then by a supervised rerun.

### Stage 3 — Hidden-track adaptability (simulation)

- The map, route, and track-specific coordinates are not provided. Teams may use the permitted runtime sensor topics listed below.
- Teams receive a **10-minute setup and inspection period with the car stationary**. 
- Each team receives up to **two official attempts**, each capped at **five minutes** and three timed laps.
- Any collision invalidates that attempt. A valid result requires three completed timed laps and zero collisions.
- The **top two valid finishers**, ranked by their fastest three-lap time, advance to the physical final. If fewer than two teams achieve a valid run, more than two may advance.
- Ties are resolved by fastest single lap, followed by a supervised rerun.

### Final — Supervised real-car demonstration (TBD)

- The two finalists run their submitted controller on the organizer-provided F1TENTH car and the same rehearsed physical course.
- The organizers announce a common speed cap and run procedure before the final. The car, battery condition, start pose, and controller interface are kept as consistent as practical between teams.
- Each finalist receives up to **two attempts** of three laps.
- Any contact, marshal intervention, or emergency-stop activation invalidates that attempt.
- The fastest clean three-lap run wins. If neither finalist completes a clean run, the team completing more laps without intervention places higher; a tie is resolved by a supervised rerun.
- A safety marshal has authority to stop a run at any time.

## Controller interface and permitted information

- Controllers receive `/scan` (`sensor_msgs/msg/LaserScan`) and `/ego_racecar/odom` (`nav_msgs/msg/Odometry`).
- Controllers publish driving commands to `/drive` (`ackermann_msgs/msg/AckermannDriveStamped`).
- Only one team controller may publish to `/drive` during an official attempt. Manual teleoperation must be stopped.
- Teams may modify their controller package. They may not modify the simulator, race monitor, collision detection, official launch configuration, maps, or scoring code used for an official run.
- Stages 1 and 2 may use the officially released map and route.
- Stage 3 controllers may use live sensor/odometry data but may not use a hidden map, hidden route, track-specific waypoint file, or other track-specific coordinates. These assets must be withheld from the public student checkout until after the challenge.
- No human may send driving commands, reposition the car, or change controller code/configuration during a scored attempt.

## Run administration and scoring

- Organizers reset the simulator, starting pose, lap timer, and collision counter before each official attempt.
- The official race monitor is the scoring source for simulator lap times, completed laps, and collisions. Organizers track the team identifier, submitted controller version/hash, attempt number, result, and any intervention in the official results sheet.
- A run ends when the attempt limit is reached, three timed laps are complete, the controller stops, or an organizer stops the run.
- A collision or other invalidation applies only to that attempt; other attempts remain eligible.
- Teams may request a score review immediately after their run. Organizers review the official race-monitor result and timing display.

## Safety and conduct

- The simulator stages are run only in the competition's pinned environment.
- The organizer confirms the controller, speed cap, emergency stop, physical course, and marshal procedure in a full rehearsal before the real-car final.
- For the physical final, the car remains inside a controlled course area. Nobody enters the course while the car is moving.
- The marshal may stop a car for unsafe behavior, loss of control, equipment problems, or risk to people or property.
- The official speed cap and physical emergency-stop procedure take precedence over controller settings.
