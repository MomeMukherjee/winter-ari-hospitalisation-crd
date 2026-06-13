"""
ehrQL Dataset Definition for Winter ARI Hospitalisation Study
Study: Burden of Winter ARI Hospitalisation in England (with/without CRD)
Season: Winter 2017-18 (Oct 2017 - Mar 2018)
Purpose: Extract adults (≥18y) registered in England with:
  - Demographics (age, sex, ethnicity, IMD, region)
  - CRD flags (asthma, COPD, ILD, bronchiectasis - individual + combined)
  - ARI hospitalisations (primary + any diagnosis position)
  - Covariates (smoking, BMI, prior healthcare use)
Output: One row per patient with these features
"""

from ehrql import create_dataset
from ehrql.tables.tpp import (
    patients, 
    practice_registrations,
    clinical_events,
    apcs,
    ons_deaths
)
from datetime import date

# ============================================================================
# DEFINE STUDY PERIODS
# ============================================================================
# Window 1: Registration lookback (to ensure 12+ months registered)
registration_start = date(2016, 4, 1)      # Apr 2016 (12mo before winter)
registration_end = date(2018, 3, 31)       # Mar 2018 (end of winter season)

# Window 2: CRD lookback (to identify chronic disease history)
crd_lookback_start = date(2016, 4, 1)      # Apr 2016 onwards

# Window 3: Outcome window (ARI hospitalisations during winter)
outcome_start = date(2017, 10, 1)          # Oct 2017 (start of winter)
outcome_end = date(2018, 3, 31)            # Mar 2018 (end of winter)

# ============================================================================
# STEP 1: DEFINE COHORT (Age ≥18 on Oct 2017, registered in England)
# ============================================================================
# Patients aged ≥18 on outcome start date
adults = patients.where(
    patients.age_on(outcome_start) >= 18
)

# Patients registered in TPP for ≥12 months before winter start
# (registration window: Apr 2016 - Mar 2018)
registered_adequately = adults.filter(
    practice_registrations.for_patient().where(
        (practice_registrations.start_date <= registration_start) &
        ((practice_registrations.end_date.is_null()) | 
         (practice_registrations.end_date >= outcome_start))
    ).exists_for_patient()
)

# Patients alive at start of winter (Oct 2017)
alive_at_winter_start = registered_adequately.filter(
    (ons_deaths.date.is_null()) | (ons_deaths.date >= outcome_start)
)

# Final cohort
cohort = alive_at_winter_start

# ============================================================================
# STEP 2: EXTRACT DEMOGRAPHICS (measured at Oct 2017)
# ============================================================================
dataset = create_dataset()
dataset.configure_dummy_data(population_size=500000)  # For dummy data testing

# Age (in years at start of winter)
dataset.age = cohort.age_on(outcome_start)

# Age group (for stratification)
dataset.age_group = cohort.age_on(outcome_start).categorise_by_age_band(
    band_size=5, start_year=18
)
# Custom age groups for analysis
dataset.age_group_broad = cohort.age_on(outcome_start).case(
    when((cohort.age_on(outcome_start) >= 18) & 
         (cohort.age_on(outcome_start) < 45)).then("18-44"),
    when((cohort.age_on(outcome_start) >= 45) & 
         (cohort.age_on(outcome_start) < 65)).then("45-64"),
    when((cohort.age_on(outcome_start) >= 65) & 
         (cohort.age_on(outcome_start) < 85)).then("65-84"),
    when(cohort.age_on(outcome_start) >= 85).then("85+"),
    default="Unknown"
)

# Sex (male/female)
dataset.sex = cohort.sex

# Ethnicity (White/Non-White - per your spec)
# Note: Using primary care coded ethnicity
dataset.ethnicity = clinical_events.where(
    clinical_events.snomedct_code.is_in(ETHNICITY_CODES)
).latest_for_patient().value_as_concept

# IMD quintile (Index of Multiple Deprivation, from practice)
dataset.imd_quintile = cohort.practice.imd_quintile

# NHS Region (from GP practice)
dataset.nhs_region = cohort.practice.nhs_region

# Urban/Rural classification (from practice postcode)
dataset.urban_rural = cohort.practice.rural_urban_classification

# ============================================================================
# STEP 3: DEFINE CHRONIC RESPIRATORY DISEASE (CRD) FLAGS
# ============================================================================
# For each CRD: any clinical event in lookback (Apr 2016 onwards) OR on medications
# Dates will be extracted separately for temporal analysis

# 3.1 ASTHMA
# Primary care diagnosis codes + QOF asthma register
asthma_clinical = clinical_events.where(
    clinical_events.snomedct_code.is_in(ASTHMA_SNOMED_CODES)
).where(
    clinical_events.date >= crd_lookback_start
).exists_for_patient()

asthma_medications = clinical_events.where(
    clinical_events.bnf_code.is_in(ASTHMA_MEDICATION_BNF_CODES)
).where(
    clinical_events.date >= crd_lookback_start
).exists_for_patient()

dataset.asthma_flag = asthma_clinical | asthma_medications

# 3.2 COPD
copd_clinical = clinical_events.where(
    clinical_events.snomedct_code.is_in(COPD_SNOMED_CODES)
).where(
    clinical_events.date >= crd_lookback_start
).exists_for_patient()

copd_medications = clinical_events.where(
    clinical_events.bnf_code.is_in(COPD_MEDICATION_BNF_CODES)
).where(
    clinical_events.date >= crd_lookback_start
).exists_for_patient()

dataset.copd_flag = copd_clinical | copd_medications

# 3.3 INTERSTITIAL LUNG DISEASE (ILD)
ild_clinical = clinical_events.where(
    clinical_events.snomedct_code.is_in(ILD_SNOMED_CODES)
).where(
    clinical_events.date >= crd_lookback_start
).exists_for_patient()

dataset.ild_flag = ild_clinical

# 3.4 BRONCHIECTASIS
bronchiectasis_clinical = clinical_events.where(
    clinical_events.snomedct_code.is_in(BRONCHIECTASIS_SNOMED_CODES)
).where(
    clinical_events.date >= crd_lookback_start
).exists_for_patient()

dataset.bronchiectasis_flag = bronchiectasis_clinical

# 3.5 COMBINED CRD CATEGORIES
# Create mutually exclusive + overlapping categories for stratification
dataset.crd_none = ~(dataset.asthma_flag | dataset.copd_flag | 
                      dataset.ild_flag | dataset.bronchiectasis_flag)
# 1. Asthma Only
dataset.crd_asthma_only = (
    dataset.asthma_flag 
    & ~dataset.copd_flag 
    & ~dataset.ild_flag 
    & ~dataset.bronchiectasis_flag
)

# 2. COPD Only
dataset.crd_copd_only = (
    dataset.copd_flag 
    & ~dataset.asthma_flag 
    & ~dataset.ild_flag 
    & ~dataset.bronchiectasis_flag
)

# 3. ILD Only
dataset.crd_ild_only = (
    dataset.ild_flag 
    & ~dataset.asthma_flag 
    & ~dataset.copd_flag 
    & ~dataset.bronchiectasis_flag
)

# 4. Bronchiectasis Only
dataset.crd_bronchiectasis_only = (
    dataset.bronchiectasis_flag 
    & ~dataset.asthma_flag 
    & ~dataset.copd_flag 
    & ~dataset.ild_flag
)

# 5. Multiple Chronic Respiratory Diseases (2 or more)
dataset.crd_multiple = (
    dataset.asthma_flag 
    + dataset.copd_flag 
    + dataset.ild_flag 
    + dataset.bronchiectasis_flag
) >= 2

# ============================================================================
# STEP 4: EXTRACT ARI HOSPITALISATIONS (PRIMARY OUTCOME)
# ============================================================================
# ARI = COVID-19, Influenza, RSV, Pneumonia (any position in ICD-10 codes)

# Primary diagnosis position (position 0 in APCS)
ari_primary = apcs.where(
    apcs.admission_date.is_in_range(outcome_start, outcome_end)
).where(
    apcs.primary_diagnosis_code.is_in(ARI_ICD10_CODES)
)

dataset.ari_primary_admissions = ari_primary.count_for_patient()
dataset.ari_primary_admission_date = ari_primary.minimum_of("admission_date")

# Any diagnosis position (positions 0-19 in APCS)
ari_any = apcs.where(
    apcs.admission_date.is_in_range(outcome_start, outcome_end)
).where(
    apcs.all_diagnoses.contains_any(ARI_ICD10_CODES)
)

dataset.ari_any_admissions = ari_any.count_for_patient()
dataset.ari_any_admission_date = ari_any.minimum_of("admission_date")

# Length of stay (for primary position only)
ari_los = ari_primary.calculate(
    los = apcs.discharge_date - apcs.admission_date
).maximum_of("los")
dataset.ari_primary_los_days = ari_los

# ============================================================================
# STEP 5: EXTRACT COVARIATES
# ============================================================================

# 5.1 SMOKING STATUS (most recent before winter start)
smoking_codes = clinical_events.where(
    clinical_events.snomedct_code.is_in(SMOKING_SNOMED_CODES)
).where(
    clinical_events.date < outcome_start
).latest_for_patient()

dataset.smoking_status = smoking_codes.value_as_concept
dataset.smoking_date = smoking_codes.date

# 5.2 BMI (most recent in previous 12 months: Apr 2017 - Sep 2017)
bmi_start = date(2017, 4, 1)
bmi_end = date(2017, 9, 30)

bmi_records = clinical_events.where(
    clinical_events.snomedct_code.is_in(BMI_SNOMED_CODES)
).where(
    clinical_events.date.is_in_range(bmi_start, bmi_end)
).latest_for_patient()

dataset.bmi = bmi_records.numeric_value
dataset.bmi_date = bmi_records.date

# 5.3 VACCINATION STATUS (by winter start date: Oct 2017)
# Influenza vaccine (seasonal, typically Sep-Oct)
flu_vaccine = clinical_events.where(
    clinical_events.snomedct_code.is_in(FLU_VACCINE_SNOMED_CODES)
).where(
    clinical_events.date >= date(2017, 1, 1)  # Current season
).where(
    clinical_events.date < outcome_start
).latest_for_patient()

dataset.flu_vaccine_2017 = flu_vaccine.date.is_not_null()
dataset.flu_vaccine_date = flu_vaccine.date

# Pneumococcal vaccine (less frequent)
pneum_vaccine = clinical_events.where(
    clinical_events.snomedct_code.is_in(PNEUMOCOCCAL_VACCINE_SNOMED_CODES)
).where(
    clinical_events.date >= date(2015, 1, 1)  # Broader window
).latest_for_patient()

dataset.pneumococcal_vaccine = pneum_vaccine.date.is_not_null()
dataset.pneumococcal_vaccine_date = pneum_vaccine.date

# 5.4 CARDIOVASCULAR RISK FACTORS
# Blood pressure (most recent)
bp_systolic = clinical_events.where(
    clinical_events.snomedct_code.is_in(BP_SYSTOLIC_SNOMED_CODES)
).where(
    clinical_events.date < outcome_start
).latest_for_patient().numeric_value

bp_diastolic = clinical_events.where(
    clinical_events.snomedct_code.is_in(BP_DIASTOLIC_SNOMED_CODES)
).where(
    clinical_events.date < outcome_start
).latest_for_patient().numeric_value

dataset.systolic_bp = bp_systolic
dataset.diastolic_bp = bp_diastolic

# Cholesterol (total)
cholesterol = clinical_events.where(
    clinical_events.snomedct_code.is_in(CHOLESTEROL_SNOMED_CODES)
).where(
    clinical_events.date < outcome_start
).latest_for_patient().numeric_value

dataset.total_cholesterol = cholesterol

# 5.5 CHRONIC DISEASE MANAGEMENT INDICATORS
# Asthma annual review (in past 12 months before winter)
asthma_review_start = date(2016, 10, 1)
asthma_review = clinical_events.where(
    clinical_events.snomedct_code.is_in(ASTHMA_REVIEW_SNOMED_CODES)
).where(
    clinical_events.date >= asthma_review_start
).where(
    clinical_events.date < outcome_start
).exists_for_patient()

dataset.asthma_annual_review = asthma_review

# COPD annual review
copd_review = clinical_events.where(
    clinical_events.snomedct_code.is_in(COPD_REVIEW_SNOMED_CODES)
).where(
    clinical_events.date >= asthma_review_start
).where(
    clinical_events.date < outcome_start
).exists_for_patient()

dataset.copd_annual_review = copd_review

# 5.6 PRIOR HEALTHCARE UTILISATION (in 12 months before winter: Apr 2016 - Sep 2017)
healthcare_start = date(2016, 10, 1)
healthcare_end = date(2017, 9, 30)

# GP consultations (count)
gp_consultations = clinical_events.where(
    clinical_events.date.is_in_range(healthcare_start, healthcare_end)
).count_for_patient()

dataset.gp_consultations_12mo = gp_consultations

# Hospital admissions (count, any diagnosis)
hospital_admissions = apcs.where(
    apcs.admission_date.is_in_range(healthcare_start, healthcare_end)
).count_for_patient()

dataset.hospital_admissions_12mo = hospital_admissions

# ============================================================================
# STEP 6: OUTPUT DATASET
# ============================================================================
# Unique patient ID (handled internally by ehrQL)
dataset.patient_id = cohort.patient_id

# Output dataset with all defined variables
dataset.configure_dummy_data(population_size=500000)
