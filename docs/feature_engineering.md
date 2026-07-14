# Feature Engineering

This document defines the features calculated from the raw Garmin Connect activity export.

The initial version uses activity-level running data. Features requiring second-by-second or lap-level data are deferred to a future version.

---

## Feature Status

- **MVP:** Planned for the first working version
- **Later:** Useful, but not required for the MVP
- **Future Data:** Requires more detailed data than the current Garmin CSV export provides

---

## Training Volume Features

| Feature | Formula / Method | Raw Inputs | Purpose | Status |
|---|---|---|---|---|
| Weekly Distance | Sum of `Distance` for each calendar week | Date, Distance | Measures changes in weekly running volume | MVP |
| Weekly Running Time | Sum of `Moving Time` for each calendar week | Date, Moving Time | Measures total weekly time spent running | MVP |
| Weekly Training Stress | Sum of `Training Stress Score` for each calendar week | Date, Training Stress Score | Estimates accumulated weekly training load | MVP |
| Weekly Run Count | Count of running activities per week | Date, Activity Type | Measures training frequency | MVP |
| Rolling 7-Day Distance | Sum of distance completed during the previous 7 days | Date, Distance | Measures recent running volume independent of calendar weeks | MVP |
| Rolling 28-Day Distance | Sum of distance completed during the previous 28 days | Date, Distance | Represents longer-term training volume | MVP |
| Days Since Previous Run | Difference between the current run date and previous run date | Date | Measures recovery spacing and training consistency | MVP |

---

## Intensity Features

| Feature | Formula / Method | Raw Inputs | Purpose | Status |
|---|---|---|---|---|
| Average Speed | `Distance / Moving Time` | Distance, Moving Time | Converts pace into a numerical value that is easier to use in calculations and models | MVP |
| Relative Heart-Rate Intensity | `Avg HR / estimated maximum HR` | Avg HR, athlete maximum HR | Normalizes cardiovascular intensity across activities | Later |
| Training Stress per Minute | `Training Stress Score / Moving Time` | Training Stress Score, Moving Time | Distinguishes concentrated high-intensity sessions from longer low-intensity runs | MVP |
| Aerobic Effect per Minute | `Aerobic TE / Moving Time` | Aerobic TE, Moving Time | Describes aerobic stimulus relative to workout duration | Later |

---

## Aerobic-Efficiency Features

| Feature | Formula / Method | Raw Inputs | Purpose | Status |
|---|---|---|---|---|
| Heart-Rate Efficiency Proxy | `Average Speed / Avg HR` | Distance, Moving Time, Avg HR | Estimates the amount of running speed produced per heartbeat | MVP |
| Power-to-Heart-Rate Ratio | `Avg Power / Avg HR` | Avg Power, Avg HR | Estimates external output relative to cardiovascular demand | MVP |
| Speed-to-Power Ratio | `Average Speed / Avg Power` | Distance, Moving Time, Avg Power | Explores how much speed is produced for a given power output | MVP |
| Pace per Watt | `Avg Pace / Avg Power` | Avg Pace, Avg Power | Alternative representation of running output relative to power | Later |

### Interpretation Note

These are project-defined performance proxies, not clinically validated measures of running economy. Comparisons should be made primarily between similar activities and conditions.

---

## Terrain Features

| Feature | Formula / Method | Raw Inputs | Purpose | Status |
|---|---|---|---|---|
| Climbing Density | `Total Ascent / Distance` | Total Ascent, Distance | Measures how hilly a route was and helps contextualize pace | MVP |
| Ascent per Hour | `Total Ascent / Moving Time` | Total Ascent, Moving Time | Measures the rate of climbing during a run | Later |
| Pause Ratio | `(Elapsed Time - Moving Time) / Elapsed Time` | Moving Time, Elapsed Time | Identifies activities affected by stops or long pauses | MVP |

---

## Running-Mechanics Features

| Feature | Formula / Method | Raw Inputs | Purpose | Status |
|---|---|---|---|---|
| Estimated Stride Count | `Steps / 2` | Steps | Approximates the number of complete stride cycles | Later |
| Vertical Movement per Step | Exploratory combination of vertical oscillation and step count | Avg Vertical Oscillation, Steps | Describes vertical motion over the activity | Later |
| Ground Contact Load Proxy | `Avg Ground Contact Time × Steps` | Avg Ground Contact Time, Steps | Exploratory estimate of cumulative ground-contact exposure | Later |
| Mechanics Efficiency Proxy | Weighted combination of cadence, stride length, vertical ratio, and ground contact time | Avg Run Cadence, Avg Stride Length, Avg Vertical Ratio, Avg Ground Contact Time | Explores whether running mechanics change alongside performance | Later |

### Mechanics Note

A combined mechanics score should not be created until the relationships between the individual variables are explored. The first analysis should examine each feature independently rather than assigning arbitrary weights.

---

## Time and Context Features

| Feature | Formula / Method | Raw Inputs | Purpose | Status |
|---|---|---|---|---|
| Month | Extract month from activity date | Date | Supports monthly comparisons and seasonal trend analysis | MVP |
| Week | Extract calendar week from activity date | Date | Supports weekly aggregation | MVP |
| Day of Week | Extract weekday from activity date | Date | Explores training patterns across the week | Later |
| Activity Title Keywords | Identify terms such as `easy`, `tempo`, `interval`, `race`, or `long` within the activity title | Title | Helps create initial workout-type labels | MVP |
| Distance Category | Assign runs to short, medium, and long-distance ranges | Distance | Supports comparisons between broadly similar runs | Later |

---

## Comparison Features and Analyses

The following are not single dataset columns. They are analyses calculated across multiple comparable activities.

### Pace–Heart Rate Trend

Compare average heart rate at similar running paces across time.

Example output:

> At approximately 5:30 min/km, average heart rate was 6 bpm lower during the most recent training block.

Possible method:

1. Group runs into pace ranges.
2. Compare average heart rate within each pace range by month or training block.
3. Require a minimum number of comparable runs before reporting a trend.

**Status:** MVP

### Aerobic-Efficiency Trend

Track the heart-rate efficiency proxy across time using a rolling average.

Possible method:

1. Calculate efficiency for each valid run.
2. Filter extreme or incomplete activities.
3. Compute a four-week rolling average.
4. Compare recent values with an earlier baseline.

**Status:** MVP

### Comparable-Run Score

Compare runs only when their distance, terrain, and intensity are sufficiently similar.

Possible comparison variables:

- distance
- climbing density
- average heart rate
- workout type
- moving time

**Status:** Later

---

## Missing-Value Rules

- Features requiring heart rate are not calculated when `Avg HR` is missing or zero.
- Features requiring power are not calculated when `Avg Power` is missing or zero.
- Rate features are not calculated when distance or moving time is zero.
- Missing values are retained as null values rather than automatically replaced with zero.

---

## Features Deferred from the MVP

### Cadence Consistency

The current export contains only average cadence, not cadence variation throughout the run. A true consistency measure would require lap-level or time-series cadence data.

### Instantaneous Elevation-Adjusted Pace

The current CSV includes total ascent but not point-by-point elevation and pace. This requires FIT, GPX, or TCX time-series data.

### True Running Economy

Running economy is normally assessed using physiological measurements such as oxygen consumption. The project can calculate transparent proxies but should not describe them as a direct measurement of running economy.

### Fatigue Score

A defensible fatigue estimate would benefit from sleep, HRV, resting heart rate, recent workload, and subjective recovery data. It is outside the initial scope.