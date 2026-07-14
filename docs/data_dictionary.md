# Data Dictionary

| Stat | Category | Units | Description |
|------|----------|-------|-------------|
| Date | Metadata | Date | Date the activity was recorded. |
| Activity Type | Metadata | — | Type of activity (e.g., Running, Trail Running). |
| Distance | Training Load | km | Total distance covered during the activity. |
| Moving Time | Training Load | min | Time spent actively moving, excluding pauses. |
| Elapsed Time | Training Load | min | Total elapsed activity time, including pauses. |
| Calories | Training Load | kcal | Estimated calories burned during the activity. |
| Steps | Training Load | steps | Total number of running steps. |
| Training Stress Score (TSS) | Training Load | score | Garmin's estimate of the physiological training load of the session. |
| Avg HR | Cardiovascular Response | bpm | Average heart rate during the activity. |
| Max HR | Cardiovascular Response | bpm | Maximum heart rate recorded during the activity. |
| Aerobic TE | Cardiovascular Response | score (0–5+) | Garmin's estimate of the aerobic training effect of the workout. |
| Avg Stress | Cardiovascular Response | score | Average stress level estimated from heart rate variability during the activity. |
| Avg Pace | Performance | min/km | Average pace maintained throughout the activity. |
| Best Pace | Performance | min/km | Fastest pace achieved during the activity. |
| Avg Power | Power | W | Average estimated running power output. |
| Avg Run Cadence | Running Mechanics | spm | Average running cadence (steps per minute). |
| Avg Stride Length | Running Mechanics | m | Average stride length throughout the run. |
| Avg Vertical Ratio | Running Mechanics | % | Ratio of vertical oscillation to stride length; lower values generally indicate more economical running mechanics. |
| Avg Vertical Oscillation | Running Mechanics | cm | Average vertical movement of the torso while running. |
| Avg Ground Contact Time | Running Mechanics | ms | Average time each foot spends in contact with the ground. |
| Total Ascent | Terrain | m | Total elevation gain accumulated during the activity. |

## Notes
- All variables above are directly exported from Garmin Connect.
- Additional engineered features (e.g., Weekly Distance, HR Efficiency, Climbing Density, Pace per Watt) are documented separately in `feature_engineering.md`.
- Unless otherwise specified, all calculations are performed using running activities only.