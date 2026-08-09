# Athlete Intelligence

> **Status: In Progress**

Athlete Intelligence is an independent Python project for turning raw Garmin running data into structured, analysis-ready datasets and interpretable insights about training and performance.

The project is currently focused on building a reliable data and feature-engineering foundation before moving into visualization, comparative analysis, and machine-learning experiments.

## Project Goals

The longer-term goal is to build a lightweight athlete analytics system that can identify meaningful patterns across training history while keeping the outputs transparent and interpretable.

Planned areas of analysis include:

- Training volume and workload trends
- Pace–heart rate relationships
- Aerobic-efficiency proxies
- Running power and cadence
- Terrain and elevation effects
- Comparable-run performance over time
- Recovery and training-context relationships
- Athlete-focused performance visualizations

Where physiological concepts are approximated from wearable data, they will be treated as analytical proxies rather than clinical measurements or diagnoses.

## Current Progress

The project currently includes an initial data-exploration workflow and a reusable cleaning pipeline for Garmin activity exports.

The pipeline:

- Filters the dataset to running and treadmill activities
- Normalizes Garmin placeholders and missing values
- Parses activity dates and timestamps
- Converts duration and pace fields into analysis-ready numeric formats
- Converts formatted Garmin measurements into numeric values where appropriate
- Removes fields that are unavailable or uninformative for the current dataset
- Preserves meaningful missing values rather than replacing them with zero
- Leaves the original source data unchanged

Automated tests validate key pipeline behavior, including:

- Missing-value handling
- Numeric conversion
- Pace parsing
- Duration parsing
- Activity filtering
- End-to-end cleaning behavior

This foundation is intended to make later analysis reproducible rather than relying on notebook-specific transformations.

## Planned Feature Engineering

The next stage of development will transform cleaned activities into features that are more useful for longitudinal training analysis.

Initial features will likely include:

- Weekly running distance and duration
- Rolling training-volume metrics
- Average pace and heart-rate relationships
- Pace at comparable heart-rate ranges
- Aerobic-efficiency proxies
- Running power relative to pace
- Cadence trends
- Elevation-adjusted comparisons
- Activity-level workload indicators
- Similar-run comparison features

Feature definitions and assumptions will be documented so that resulting insights remain interpretable.

## Planned Analysis

Once the feature pipeline is established, the project will explore questions such as:

- Is running efficiency improving over time?
- How does pace change at similar heart rates?
- How do power and cadence relate to running performance?
- How does terrain affect otherwise similar activities?
- Which past runs are most comparable to a given activity?
- Are changes in training volume associated with changes in performance?

Machine learning will only be introduced where it adds useful information beyond straightforward statistical analysis.

## Repository Structure

```text
athlete-intelligence/
├── src/
│   ├── cleaning.py
│   ├── data_loader.py
│   ├── features.py
│   ├── analysis.py
│   └── model.py
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   └── 03_model_experiments.ipynb
├── tests/
│   ├── test_cleaning.py
│   └── test_features.py
├── docs/
├── app/
└── requirements.txt
```

Some modules and notebooks are placeholders for upcoming development and do not yet represent completed functionality.

## Technology

**Python · pandas · pytest · Jupyter Notebook**

Additional visualization and machine-learning libraries will be added as the project develops.

## Data Privacy

The project uses personal Garmin activity exports during local development.

Raw Garmin data is excluded from the public repository to avoid publishing private health, activity, or location information. The codebase is designed to operate on locally stored data while keeping the analysis pipeline reproducible.

## Roadmap

- [x] Explore raw Garmin activity data
- [x] Build reusable cleaning pipeline
- [x] Add automated cleaning tests
- [ ] Build feature-engineering pipeline
- [ ] Add training and performance visualizations
- [ ] Implement comparable-run analysis
- [ ] Develop an initial interactive dashboard
- [ ] Evaluate interpretable machine-learning approaches
- [ ] Document findings and model limitations
