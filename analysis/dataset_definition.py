"""
dataset_definition.py
=====================
OpenSAFELY ehrQL dataset definition for the ARI-CRD winter hospitalisation study.

Usage (called by project.yaml with --season argument):
    ehrql generate-dataset analysis/dataset_definition.py \
        --output output/dataset_YYYY_YY.csv.gz -- --season 2022_23

Season windows
--------------
Each season file covers:
  • Registration window : 1 April of preceding year → end of winter (31 March)
  • CRD lookback       : from 1 April of preceding year (or study start Sep 2016)
  • Outcome window     : 1 October → 31 March of that winter season
  • COVID era flags    : pre-COVID (Sep2016–Feb2020), COVID (Mar2020–Mar2022),
                         post-COVID (Apr2022–latest)
"""

import argparse
from datetime import date

from ehrql import Dataset, codelist_from_csv, days, months, years
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    clinical_events,
    hospital_admissions,
    ons_deaths,
    addresses,
    vaccinations,
)

# ─────────────────────────────────────────────────────────────
# 0.  PARSE SEASON ARGUMENT
# ─────────────────────────────────────────────────────────────

parser = argparse.ArgumentParser()
parser.add_argument("--season", required=True,
    choices=["2017_18","2018_19","2019_20","2020_21","2021_22","2022_23","2023_24"])
args = parser.parse_args()

# Map season → key dates
SEASON_DATES = {
    "2017_18": dict(
        reg_start   = date(2016, 9,  1),   # study start — ask from Apr 2016 next time
        outcome_start = date(2017, 10, 1),
        outcome_end   = date(2018,  3, 31),
        index_date    = date(2017, 10,  1),
    ),
    "2018_19": dict(
        reg_start   = date(2017, 4,  1),
        outcome_start = date(2018, 10, 1),
        outcome_end   = date(2019,  3, 31),
        index_date    = date(2018, 10,  1),
    ),
    "2019_20": dict(
        reg_start   = date(2018, 4,  1),
        outcome_start = date(2019, 10, 1),
        outcome_end   = date(2020,  3, 31),
        index_date    = date(2019, 10,  1),
    ),
    "2020_21": dict(
        reg_start   = date(2019, 4,  1),
        outcome_start = date(2020, 10, 1),
        outcome_end   = date(2021,  3, 31),
        index_date    = date(2020, 10,  1),
    ),
    "2021_22": dict(
        reg_start   = date(2020, 4,  1),
        outcome_start = date(2021, 10, 1),
        outcome_end   = date(2022,  3, 31),
        index_date    = date(2021, 10,  1),
    ),
    "2022_23": dict(
        reg_start   = date(2021, 4,  1),
        outcome_start = date(2022, 10, 1),
        outcome_end   = date(2023,  3, 31),
        index_date    = date(2022, 10,  1),
    ),
    "2023_24": dict(
        reg_start   = date(2022, 4,  1),
        outcome_start = date(2023, 10, 1),
        outcome_end   = date(2024,  3, 31),
        index_date    = date(2023, 10,  1),
    ),
}

s          = SEASON_DATES[args.season]
REG_START  = s["reg_start"]
OUT_START  = s["outcome_start"]
OUT_END    = s["outcome_end"]
INDEX_DATE = s["index_date"]
SEASON_TAG = args.season   # stored as variable in output

# COVID era
COVID_START    = date(2020, 3,  1)
COVID_END      = date(2022, 3, 31)
POST_COVID_START = date(2022, 4,  1)

def covid_era(dt: date) -> str:
    if dt < COVID_START:
        return "pre_covid"
    elif dt <= COVID_END:
        return "covid"
    else:
        return "post_covid"

ERA = covid_era(INDEX_DATE)

# ─────────────────────────────────────────────────────────────
# 1.  CODELISTS
# ─────────────────────────────────────────────────────────────

# --- CRD (primary care, SNOMED) ---
asthma_snomed        = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-ast_cod.csv",
                            column="code")
copd_snomed          = codelist_from_csv("codelists/bristol-copd.csv",
                            column="code")
ild_snomed           = codelist_from_csv("codelists/bristol-ild-snomed.csv",
                            column="code")
bronchiectasis_snomed = codelist_from_csv("codelists/local/bronchiectasis-snomed.csv",
                            column="code")

# --- ARI (secondary care, ICD-10) ---
pneumonia_icd10      = codelist_from_csv("codelists/bristol-pneumonia-secondary-care.csv",
                            column="code")
rsv_icd10            = codelist_from_csv("codelists/local/rsv-icd10.csv",
                            column="code")
# COVID and influenza — OpenSAFELY secondary-care codelist covers both
ari_secondary_icd10  = codelist_from_csv(
                            "codelists/opensafely-acute-respiratory-illness-secondary-care.csv",
                            column="code")

# --- ARI (primary care, SNOMED) ---
ari_primary_care_snomed = codelist_from_csv(
                            "codelists/opensafely-acute-respiratory-illness-primary-care.csv",
                            column="code")

# --- Other respiratory (SNOMED) ---
other_resp_snomed    = codelist_from_csv("codelists/opensafely-other-respiratory-conditions.csv",
                            column="code")
urti_snomed          = codelist_from_csv("codelists/bristol-urti-snomed.csv",
                            column="code")
pf_snomed            = codelist_from_csv("codelists/bristol-pulmonary-fibrosis-interstitial-lung-disease.csv",
                            column="code")

# --- Cardiac (ICD-10) ---
cardiac_arrest_icd10 = codelist_from_csv("codelists/local/cardiac-arrest-arrhythmia-icd10.csv",
                            column="code")
heart_failure_icd10  = codelist_from_csv("codelists/local/heart-failure-icd10.csv",
                            column="code")

# --- Vaccines (SNOMED) ---
rsv_vacc_snomed      = codelist_from_csv("codelists/local/rsv-vaccination-snomed.csv",
                            column="code")

# --- COPD QOF / management ---
copd_qof_snomed      = codelist_from_csv("codelists/nhsd-primary-care-domain-refsets-copdres_cod.csv",
                            column="code")
asthma_review_snomed = codelist_from_csv("codelists/opensafely-asthma-annual-review-qof.csv",
                            column="code")

# ─────────────────────────────────────────────────────────────
# 2.  DATASET INITIALISATION
# ─────────────────────────────────────────────────────────────

dataset = Dataset()

# ─────────────────────────────────────────────────────────────
# 3.  POPULATION INCLUSION/EXCLUSION
# ─────────────────────────────────────────────────────────────

# Registered ≥12 months before index date AND alive at index date
registration = practice_registrations.for_patient_on(INDEX_DATE)

has_12m_registration = practice_registrations.where(
    practice_registrations.start_date.is_on_or_before(INDEX_DATE - months(12))
).exists_for_patient()

died_before_index = ons_deaths.where(
    ons_deaths.date.is_before(INDEX_DATE)
).exists_for_patient()

is_adult = patients.age_on(INDEX_DATE) >= 18

dataset.define_population(
    has_12m_registration
    & ~died_before_index
    & is_adult
    & registration.exists_for_patient()
)

# ─────────────────────────────────────────────────────────────
# 4.  DEMOGRAPHICS
# ─────────────────────────────────────────────────────────────

dataset.age        = patients.age_on(INDEX_DATE)
dataset.sex        = patients.sex
dataset.date_of_birth = patients.date_of_birth

# Age groups
age = patients.age_on(INDEX_DATE)
dataset.age_group = (
    "18_44"  if (age >= 18)  & (age < 45)  else
    "45_64"  if (age >= 45)  & (age < 65)  else
    "65_84"  if (age >= 65)  & (age < 85)  else
    "85plus" if  age >= 85   else
    "unknown"
)

# Ethnicity (6-category)
dataset.ethnicity = (
    clinical_events.where(
        clinical_events.ctv3_code.is_in(
            codelist_from_csv("codelists/opensafely-ethnicity.csv", column="Code",
                              category_column="Grouping_6")
        )
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(
        codelist_from_csv("codelists/opensafely-ethnicity.csv", column="Code",
                          category_column="Grouping_6")
    )
)

# IMD quintile (deprivation)
dataset.imd_quintile = addresses.for_patient_on(INDEX_DATE).imd_rounded

# NHS region / practice
dataset.practice_id    = registration.practice_pseudo_id
dataset.practice_region = registration.practice_nuts1_region_name

# Urban/rural classification
dataset.rural_urban    = addresses.for_patient_on(INDEX_DATE).rural_urban_classification

# Season tag and COVID era (constant per file, useful after collation)
dataset.season = SEASON_TAG
dataset.covid_era = ERA

# ─────────────────────────────────────────────────────────────
# 5.  CHRONIC RESPIRATORY DISEASE (CRD) FLAGS
#     Look back to REG_START (or earlier for existing diagnoses)
# ─────────────────────────────────────────────────────────────

def has_crd_code(codelist):
    return clinical_events.where(
        clinical_events.snomedct_code.is_in(codelist)
        & clinical_events.date.is_on_or_before(INDEX_DATE)
    ).exists_for_patient()

dataset.has_asthma        = has_crd_code(asthma_snomed)
dataset.has_copd          = has_crd_code(copd_snomed)
dataset.has_ild           = has_crd_code(ild_snomed) | has_crd_code(pf_snomed)
dataset.has_bronchiectasis = has_crd_code(bronchiectasis_snomed)

dataset.has_any_crd = (
    dataset.has_asthma
    | dataset.has_copd
    | dataset.has_ild
    | dataset.has_bronchiectasis
)

# CRD combination flags (for Q1 subgroup analyses)
dataset.crd_count = (
    dataset.has_asthma.as_int()
    + dataset.has_copd.as_int()
    + dataset.has_ild.as_int()
    + dataset.has_bronchiectasis.as_int()
)
dataset.has_multimorbid_crd = dataset.crd_count >= 2

# ─────────────────────────────────────────────────────────────
# 6.  ARI HOSPITAL ADMISSIONS — outcome window only
# ─────────────────────────────────────────────────────────────

# Helper: admissions in outcome window
admissions_in_window = hospital_admissions.where(
    hospital_admissions.admission_date.is_on_or_between(OUT_START, OUT_END)
)

# --- 6a.  ARI PRIMARY diagnosis (first position) ---
ari_primary_admissions = admissions_in_window.where(
    hospital_admissions.primary_diagnoses.is_in(ari_secondary_icd10)
    | hospital_admissions.primary_diagnoses.is_in(pneumonia_icd10)
    | hospital_admissions.primary_diagnoses.is_in(rsv_icd10)
)

dataset.ari_primary_diag       = ari_primary_admissions.exists_for_patient()
dataset.ari_primary_diag_count = ari_primary_admissions.count_for_patient()
dataset.ari_primary_diag_first_date = (
    ari_primary_admissions.sort_by(hospital_admissions.admission_date)
    .first_for_patient().admission_date
)

# --- 6b.  ARI ANY diagnosis position ---
ari_any_admissions = admissions_in_window.where(
    hospital_admissions.all_diagnoses.is_in(ari_secondary_icd10)
    | hospital_admissions.all_diagnoses.is_in(pneumonia_icd10)
    | hospital_admissions.all_diagnoses.is_in(rsv_icd10)
)

dataset.ari_any_diag       = ari_any_admissions.exists_for_patient()
dataset.ari_any_diag_count = ari_any_admissions.count_for_patient()

# --- 6c.  ARI sub-type flags (for breakdown tables) ---
#   Pneumonia
dataset.ari_pneumonia_primary = admissions_in_window.where(
    hospital_admissions.primary_diagnoses.is_in(pneumonia_icd10)
).exists_for_patient()

#   RSV
dataset.ari_rsv_primary = admissions_in_window.where(
    hospital_admissions.primary_diagnoses.is_in(rsv_icd10)
).exists_for_patient()

#   Influenza / COVID / other ARI (combined from secondary care codelist)
dataset.ari_other_primary = admissions_in_window.where(
    hospital_admissions.primary_diagnoses.is_in(ari_secondary_icd10)
    & ~hospital_admissions.primary_diagnoses.is_in(pneumonia_icd10)
    & ~hospital_admissions.primary_diagnoses.is_in(rsv_icd10)
).exists_for_patient()

# --- 6d.  Length of stay (first ARI admission) ---
first_ari_admission = (
    ari_primary_admissions
    .sort_by(hospital_admissions.admission_date)
    .first_for_patient()
)
dataset.ari_los_days = (
    first_ari_admission.discharge_date - first_ari_admission.admission_date
)

# --- 6e.  Respiratory exacerbation (non-ARI acute resp admission) ---
resp_exacerb_admissions = admissions_in_window.where(
    hospital_admissions.primary_diagnoses.is_in(other_resp_snomed)
    & ~hospital_admissions.primary_diagnoses.is_in(ari_secondary_icd10)
    & ~hospital_admissions.primary_diagnoses.is_in(pneumonia_icd10)
)
dataset.resp_exacerbation = resp_exacerb_admissions.exists_for_patient()

# --- 6f.  Cardiac events (ICD-10) ---
dataset.acute_cardiac_event = admissions_in_window.where(
    hospital_admissions.primary_diagnoses.is_in(cardiac_arrest_icd10)
    | hospital_admissions.primary_diagnoses.is_in(heart_failure_icd10)
).exists_for_patient()

# ─────────────────────────────────────────────────────────────
# 7.  ARI DEATH (sensitivity outcome)
# ─────────────────────────────────────────────────────────────

dataset.ari_death = ons_deaths.where(
    ons_deaths.date.is_on_or_between(OUT_START, OUT_END)
    & (
        ons_deaths.cause_of_death_01.is_in(ari_secondary_icd10)
        | ons_deaths.cause_of_death_01.is_in(pneumonia_icd10)
        | ons_deaths.underlying_cause_of_death.is_in(ari_secondary_icd10)
        | ons_deaths.underlying_cause_of_death.is_in(pneumonia_icd10)
    )
).exists_for_patient()

dataset.ari_death_with_admission = dataset.ari_death & dataset.ari_any_diag
dataset.ari_death_without_admission = dataset.ari_death & ~dataset.ari_any_diag

# ─────────────────────────────────────────────────────────────
# 8.  MODIFIABLE RISK FACTORS (measured ≤12m before INDEX_DATE)
# ─────────────────────────────────────────────────────────────

LOOKBACK_12M = INDEX_DATE - months(12)

# --- Smoking status ---
dataset.smoking_status = (
    clinical_events.where(
        clinical_events.ctv3_code.is_in(
            codelist_from_csv("codelists/opensafely-smoking-clear.csv", column="CTV3Code",
                              category_column="Category")
        )
        & clinical_events.date.is_on_or_before(INDEX_DATE)
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .ctv3_code.to_category(
        codelist_from_csv("codelists/opensafely-smoking-clear.csv", column="CTV3Code",
                          category_column="Category")
    )
)

# --- BMI (most recent ≤5 years, adult-plausible range 15–70) ---
dataset.bmi = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(
            codelist_from_csv("codelists/opensafely-bmi-stage.csv", column="code")
        )
        & clinical_events.date.is_on_or_between(INDEX_DATE - years(5), INDEX_DATE)
        & clinical_events.numeric_value.is_between(15, 70)
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .numeric_value
)

# --- Vaccination status (prior to outcome window start) ---
dataset.flu_vacc_12m = vaccinations.where(
    vaccinations.target_disease.is_in(["INFLUENZA"])
    & vaccinations.date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
).exists_for_patient()

dataset.covid_vacc_ever = vaccinations.where(
    vaccinations.target_disease.is_in(["COVID-19"])
    & vaccinations.date.is_on_or_before(INDEX_DATE)
).exists_for_patient()

dataset.covid_vacc_count = vaccinations.where(
    vaccinations.target_disease.is_in(["COVID-19"])
    & vaccinations.date.is_on_or_before(INDEX_DATE)
).count_for_patient()

dataset.rsv_vacc_ever = clinical_events.where(
    clinical_events.snomedct_code.is_in(rsv_vacc_snomed)
    & clinical_events.date.is_on_or_before(INDEX_DATE)
).exists_for_patient()

dataset.pneumo_vacc_ever = vaccinations.where(
    vaccinations.target_disease.is_in(["PNEUMOCOCCAL"])
    & vaccinations.date.is_on_or_before(INDEX_DATE)
).exists_for_patient()

# --- Blood pressure (systolic, most recent ≤12m) ---
dataset.systolic_bp = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(
            codelist_from_csv("codelists/opensafely-systolic-blood-pressure-qof.csv", column="code")
        )
        & clinical_events.date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
        & clinical_events.numeric_value.is_between(40, 300)
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .numeric_value
)

# --- Total cholesterol (most recent ≤5 years) ---
dataset.total_cholesterol = (
    clinical_events.where(
        clinical_events.snomedct_code.is_in(
            codelist_from_csv("codelists/opensafely-total-cholesterol.csv", column="code")
        )
        & clinical_events.date.is_on_or_between(INDEX_DATE - years(5), INDEX_DATE)
        & clinical_events.numeric_value.is_between(0.5, 20)
    )
    .sort_by(clinical_events.date)
    .last_for_patient()
    .numeric_value
)

# --- Medications (prescriptions in ≤12m before index) ---
def rx_in_12m(bnf_codelist_path):
    return clinical_events.where(
        clinical_events.ctv3_code.is_in(
            codelist_from_csv(bnf_codelist_path, column="code")
        )
        & clinical_events.date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
    ).exists_for_patient()

dataset.rx_oral_corticosteroid = rx_in_12m("codelists/opensafely-asthma-oral-prednisolone-medication.csv")
dataset.rx_inhaled_corticosteroid = rx_in_12m("codelists/opensafely-asthma-inhaled-corticosteroids.csv")
dataset.rx_antibiotic_12m = rx_in_12m("codelists/opensafely-antibiotics.csv")
dataset.rx_statin = rx_in_12m("codelists/opensafely-statin-medication.csv")
dataset.rx_antihypertensive = rx_in_12m("codelists/opensafely-antihypertensives.csv")
dataset.rx_copd_medication = rx_in_12m("codelists/bristol-copd-medications-bnf.csv")

# --- Chronic disease management ---
dataset.asthma_annual_review_12m = clinical_events.where(
    clinical_events.snomedct_code.is_in(asthma_review_snomed)
    & clinical_events.date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
).exists_for_patient()

dataset.copd_review_12m = clinical_events.where(
    clinical_events.snomedct_code.is_in(copd_qof_snomed)
    & clinical_events.date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
).exists_for_patient()

# ─────────────────────────────────────────────────────────────
# 9.  PRIOR HEALTHCARE UTILISATION (12m before index)
# ─────────────────────────────────────────────────────────────

dataset.gp_consultations_12m = (
    clinical_events.where(
        clinical_events.date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
    ).count_for_patient()
)

dataset.hospitalisations_12m = hospital_admissions.where(
    hospital_admissions.admission_date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
).count_for_patient()

dataset.ari_hosp_prev_12m = hospital_admissions.where(
    (
        hospital_admissions.primary_diagnoses.is_in(ari_secondary_icd10)
        | hospital_admissions.primary_diagnoses.is_in(pneumonia_icd10)
    )
    & hospital_admissions.admission_date.is_on_or_between(LOOKBACK_12M, INDEX_DATE)
).exists_for_patient()

# ─────────────────────────────────────────────────────────────
# 10.  COMORBIDITIES (for confounding / stratification)
# ─────────────────────────────────────────────────────────────

def has_comorbidity(codelist):
    return clinical_events.where(
        clinical_events.snomedct_code.is_in(codelist)
        & clinical_events.date.is_on_or_before(INDEX_DATE)
    ).exists_for_patient()

dataset.has_diabetes = has_comorbidity(
    codelist_from_csv("codelists/opensafely-diabetes.csv", column="code")
)
dataset.has_hypertension = has_comorbidity(
    codelist_from_csv("codelists/opensafely-hypertension.csv", column="code")
)
dataset.has_heart_failure = has_comorbidity(
    codelist_from_csv("codelists/opensafely-heart-failure.csv", column="code")
)
dataset.has_ckd = has_comorbidity(
    codelist_from_csv("codelists/opensafely-chronic-kidney-disease-snomed.csv", column="code")
)
dataset.has_cancer = has_comorbidity(
    codelist_from_csv("codelists/opensafely-cancer-excluding-lung-and-haematological.csv",
                      column="code")
)
dataset.has_immunosuppression = has_comorbidity(
    codelist_from_csv("codelists/opensafely-immunosuppressive-therapy-sic.csv", column="code")
)
