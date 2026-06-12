# winter-ari-hospitalisation-crd

ARI-CRD Winter Hospitalisation Study
OpenSAFELY Research Project
Study Overview
Retrospective cohort study of adults (≥18 years) registered with TPP GP practices in England (OpenSAFELY platform), September 2016 to latest available date.
Research Questions:
Burden of winter ARI hospitalisation with/without chronic respiratory disease (CRD)
Modifiable risk factors associated with winter ARI admissions
Prognostic risk prediction models for (i) individuals and (ii) GP practices
---
Project Structure
```
opensafely-ari-crd/
├── project.yaml                          # Pipeline definition
├── analysis/
│   ├── dataset_definition.py             # ehrQL cohort definition (all seasons)
│   ├── 00_utils.R                        # Shared utility functions
│   ├── 01_descriptive_stats.R            # Table 1, demographics, CRD prevalence
│   ├── 02_temporal_trends.R              # Weekly time-series, epidemic threshold
│   ├── 03_risk_factors.R                 # Multilevel risk factor regression
│   ├── 04_individual_prediction_model.R  # LASSO individual-level model
│   └── 05_gp_practice_model.R            # GP practice-level NB model
├── codelists/
│   ├── local/                            # Local ICD-10 / SNOMED codelists
│   │   ├── bronchiectasis-icd10.csv
│   │   ├── bronchiectasis-snomed.csv
│   │   ├── cardiac-arrest-arrhythmia-icd10.csv
│   │   ├── heart-failure-icd10.csv
│   │   ├── rsv-icd10.csv
│   │   └── rsv-vaccination-snomed.csv
│   └── [downloaded from OpenCodelists — see codelists/codelists.txt]
├── output/
│   ├── tables/                           # CSV tables (moderately sensitive)
│   ├── figures/                          # PNG figures (moderately sensitive)
│   └── models/                           # Model outputs
└── tests/
    └── dummy_tables/                     # Dummy data for local testing
```
---
Season Windows
Season	Registration from	Outcome window	COVID era
2017-18	Sep 2016	Oct 2017 – Mar 2018	Pre-COVID
2018-19	Apr 2017	Oct 2018 – Mar 2019	Pre-COVID
2019-20	Apr 2018	Oct 2019 – Mar 2020	Pre-COVID
2020-21	Apr 2019	Oct 2020 – Mar 2021	COVID era
2021-22	Apr 2020	Oct 2021 – Mar 2022	COVID era
2022-23	Apr 2021	Oct 2022 – Mar 2023	Post-COVID
2023-24	Apr 2022	Oct 2023 – Mar 2024	Post-COVID
Note: Winter dates are used as extract windows. The epidemic threshold analysis (script 02) uses a data-driven approach (PHE/UKHSA baseline excess method) to define true winter excess periods.
---
Population
Adults ≥18 years
Registered ≥12 months before each season index date (1 October)
Alive at index date
TPP SystmOne GP practices only
Dummy data size: 500,000 (set in project.yaml to capture sufficient ILD/bronchiectasis cases)
---
Outcomes
Variable	Description
`ari_primary_diag`	ARI as primary (1st) diagnosis in APCS
`ari_any_diag`	ARI in any of the 20 APCS diagnosis positions
`ari_pneumonia_primary`	Pneumonia as primary ARI subtype
`ari_rsv_primary`	RSV as primary ARI subtype
`ari_other_primary`	Influenza / COVID / other ARI
`ari_los_days`	Length of stay for first ARI admission
`ari_death`	Death with ARI recorded (ONS + APCS) — sensitivity
`resp_exacerbation`	Non-ARI acute respiratory admission
`acute_cardiac_event`	Cardiac arrest / arrhythmia / heart failure admission
---
Running Locally (with OpenSAFELY CLI)
```bash
# Install opensafely CLI
pip install opensafely

# Run a single action (generates dummy data automatically)
opensafely run generate_dataset_2022_23

# Run all actions
opensafely run --all

# Run specific analysis
opensafely run descriptive_stats
```
---
Codelists Required (download from OpenCodelists)
The following codelists are referenced in `dataset_definition.py` but must be downloaded separately from https://www.opencodelists.org:
`opensafely-ethnicity` (CTV3, 6-category)
`opensafely-smoking-clear` (CTV3)
`opensafely-bmi-stage` (SNOMED)
`opensafely-systolic-blood-pressure-qof` (SNOMED)
`opensafely-total-cholesterol` (SNOMED)
`opensafely-diabetes` (SNOMED)
`opensafely-hypertension` (SNOMED)
`opensafely-heart-failure` (SNOMED)
`opensafely-chronic-kidney-disease-snomed`
`opensafely-asthma-oral-prednisolone-medication` (SNOMED)
`opensafely-asthma-inhaled-corticosteroids` (SNOMED)
`opensafely-antibiotics` (SNOMED)
`opensafely-statin-medication` (SNOMED)
`opensafely-antihypertensives` (SNOMED)
---
Key Analytical Decisions
Winter definition: Data-driven epidemic threshold (script 02). Full-year weekly counts extracted; winters defined analytically as consecutive weeks where rate exceeds baseline mean + 2SD (summer weeks 27–39 of pre-COVID era).
Denominator:
Weekly time-series (Q1): registered and alive that week (approximated per season file)
Individual models (Q2/Q3): 12 months prior registration before season index date
COVID era stratification:
Pre-COVID: Sep 2016 – Feb 2020
COVID: Mar 2020 – Mar 2022
Post-COVID: Apr 2022 – latest
Model families:
Temporal trends: Negative binomial mixed model (`glmmTMB`) with seasonal Fourier terms
Risk factors: Multilevel logistic regression clustered at practice/region
Prediction: LASSO logistic (individual), LASSO Poisson/NB (GP practice)
Validation: Internal-external cross-validation (leave-one-region-out)
---
Output Disclosure Control
All outputs follow OpenSAFELY disclosure control:
Counts < 5 suppressed / redacted
Counts rounded to nearest 5
No individual-level data in `moderately_sensitive` outputs