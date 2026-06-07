# =================================================================
# WINTER ARI HOSPITALISATION BY CRD 
# dataset_definition.py
# Defines study population and extracts variables using ehrQL
# OpenSAFELY-TPP backend
#
# Study period: 1 Sep 2016 to latest available date
# Population: adults >= 18, registered >= 12 months with TPP practice
# Primary outcome: ARI hospital admission (COVID, influenza, RSV, pneumonia)
# =================================================================

from ehrql import create_dataset, days, years, months, weeks
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    apcs,
    clinical_events,
    medications,
    vaccinations,
)
from codelists import (
    # --- CRD diagnosis ~ primary care (SNOMED) ---
    asthma_snomed,
    asthma_resolved_snomed,
    copd_snomed,
    copd_resolved_snomed,
    ild_snomed,
    # --- CRD diagnosis ~ hospital (ICD-10) ---
    asthma_icd10,
    copd_icd10,
    ild_icd10_narrow,
    ild_icd10_broad,
    # --- ARI outcomes ~ hospital (ICD-10) ---
    pneumonia_icd10,
    covid_icd10,
    ari_broad_icd10,
)

# =================================================================
# STUDY DATES
# =================================================================

study_start   = "2016-09-01"
study_end     = "2026-04-30"   # update to latest available before real run

# Pre/COVID/post-COVID periods
pre_covid_end    = "2020-02-29"
covid_start      = "2020-03-01"
covid_end        = "2022-03-31"
post_covid_start = "2022-04-01"

# =================================================================
# CREATE DATASET
# =================================================================

dataset = create_dataset()

# =================================================================
# POPULATION DEFINITION
# =================================================================
# Adults >= 18 registered for >= 12 months before study start
# with a TPP practice in England

registration = practice_registrations.for_patient_on(study_start)

has_registration = registration.exists_for_patient()

age_at_start = patients.age_on(study_start)

registered_12m = (
    practice_registrations
    .where(practice_registrations.start_date.is_on_or_before(
        study_start - days(365)
    ))
    .exists_for_patient()
)

dataset.define_population(
    has_registration
    & registered_12m
    & age_at_start.is_between_but_not_on(17, 130)
    & patients.date_of_death.is_after(study_start)
      | patients.date_of_death.is_null()
)

# =================================================================
# SECTION 1: DEMOGRAPHICS
# =================================================================

dataset.age        = age_at_start
dataset.sex        = patients.sex
dataset.dob        = patients.date_of_birth
dataset.date_death = patients.date_of_death
dataset.gp_practice = registration.practice_pseudo_id
dataset.stp        = registration.practice_stp
dataset.region     = registration.practice_nuts1_region_name

# =================================================================
# SECTION 2: CRD STATUS
# (has a diagnosis recorded before study start)
# =================================================================

# --- ASTHMA ---
has_asthma = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(asthma_snomed))
    .where(clinical_events.date.is_on_or_before(study_start))
    .exists_for_patient()
)
has_asthma_resolved = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(asthma_resolved_snomed))
    .where(clinical_events.date.is_on_or_before(study_start))
    .exists_for_patient()
)
dataset.asthma = has_asthma & ~has_asthma_resolved

# --- COPD ---
has_copd = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(copd_snomed))
    .where(clinical_events.date.is_on_or_before(study_start))
    .exists_for_patient()
)
has_copd_resolved = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(copd_resolved_snomed))
    .where(clinical_events.date.is_on_or_before(study_start))
    .exists_for_patient()
)
dataset.copd = has_copd & ~has_copd_resolved

# --- ILD ---
dataset.ild = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(ild_snomed))
    .where(clinical_events.date.is_on_or_before(study_start))
    .exists_for_patient()
)

# --- BRONCHIECTASIS ---
# NOTE: using local CSV ~ no opencodelists version yet
# handled directly here until formal codelist created
bronchiectasis_snomed_codes = [
    "12295008",    # Bronchiectasis
    "195984007",   # Recurrent bronchiectasis
    "195985008",   # Post-infective bronchiectasis
    "23022004",    # Tuberculous bronchiectasis
    "77593006",    # Congenital bronchiectasis
]
dataset.bronchiectasis = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(bronchiectasis_snomed_codes))
    .where(clinical_events.date.is_on_or_before(study_start))
    .exists_for_patient()
)

# --- ANY CRD ---
dataset.any_crd = (
    dataset.asthma
    | dataset.copd
    | dataset.ild
    | dataset.bronchiectasis
)

# =================================================================
# SECTION 3: PRIMARY OUTCOMES
# (ARI hospital admission ~ any time in study period)
# =================================================================

# --- PNEUMONIA ---
pneumonia_admissions = (
    apcs
    .where(apcs.primary_diagnosis.is_in(pneumonia_icd10))
    .where(apcs.admission_date.is_on_or_between(study_start, study_end))
)
dataset.pneumonia_admission       = pneumonia_admissions.exists_for_patient()
dataset.pneumonia_admission_date  = (
    pneumonia_admissions
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)
dataset.pneumonia_admission_count = pneumonia_admissions.count_for_patient()

# --- COVID-19 ---
covid_admissions = (
    apcs
    .where(apcs.primary_diagnosis.is_in(covid_icd10))
    .where(apcs.admission_date.is_on_or_between(study_start, study_end))
)
dataset.covid_admission       = covid_admissions.exists_for_patient()
dataset.covid_admission_date  = (
    covid_admissions
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)
dataset.covid_admission_count = covid_admissions.count_for_patient()

# --- INFLUENZA ---
# using local ICD-10 codes directly ~ no formal codelist yet
influenza_icd10_codes = [
    "J09", "J090", "J091", "J092", "J098",
    "J10", "J100", "J101", "J108",
    "J11", "J110", "J111", "J118",
]
influenza_admissions = (
    apcs
    .where(apcs.primary_diagnosis.is_in(influenza_icd10_codes))
    .where(apcs.admission_date.is_on_or_between(study_start, study_end))
)
dataset.influenza_admission       = influenza_admissions.exists_for_patient()
dataset.influenza_admission_date  = (
    influenza_admissions
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)
dataset.influenza_admission_count = influenza_admissions.count_for_patient()

# --- RSV ---
rsv_icd10_codes = [
    "J121",   # RSV pneumonia
    "J205",   # Acute bronchitis due to RSV
    "J210",   # Acute bronchiolitis due to RSV
    "B974",   # RSV as cause of disease elsewhere
]
rsv_admissions = (
    apcs
    .where(apcs.primary_diagnosis.is_in(rsv_icd10_codes))
    .where(apcs.admission_date.is_on_or_between(study_start, study_end))
)
dataset.rsv_admission       = rsv_admissions.exists_for_patient()
dataset.rsv_admission_date  = (
    rsv_admissions
    .sort_by(apcs.admission_date)
    .first_for_patient()
    .admission_date
)
dataset.rsv_admission_count = rsv_admissions.count_for_patient()

# --- ANY ARI (broad ~ sensitivity analysis) ---
ari_broad_admissions = (
    apcs
    .where(apcs.primary_diagnosis.is_in(ari_broad_icd10))
    .where(apcs.admission_date.is_on_or_between(study_start, study_end))
)
dataset.ari_broad_admission       = ari_broad_admissions.exists_for_patient()
dataset.ari_broad_admission_count = ari_broad_admissions.count_for_patient()

# =================================================================
# SECTION 4: COVID PERIOD FLAG
# =================================================================

dataset.covid_period = (
    patients.date_of_birth.is_not_null()   # placeholder ~ always true
    # real period flag assigned in R analysis script
    # based on admission_date falling in each period
)