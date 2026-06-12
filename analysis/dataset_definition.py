from ehrql import create_dataset, codelist_from_csv, get_parameter
# LINE 2: Added practice_registrations here
from ehrql.tables.tpp import patients, apcs, practice_registrations

# 1. RETRIEVE PARAMS FROM PROJECT.YAML
target_year = int(get_parameter("season_year", default=2017))

# Calculate structural window timelines
preceding_april = f"{target_year}-04-01"
winter_start    = f"{target_year}-10-01"
winter_end      = f"{target_year + 1}-03-31"

# 2. INITIALIZE THE DATASET OBJECT & DUMMY CAP
dataset = create_dataset()
dataset.configure_dummy_data(population_size=500000)

# 3. POPULATION DENOMINATOR (Registered at start of winter and alive)
# We find the practice registration that covers our winter start date
is_registered = practice_registrations.where(
    practice_registrations.start_date.is_on_or_before(winter_start)
).where(
    practice_registrations.end_date.is_after(winter_start) | practice_registrations.end_date.is_null()
).exists_for_patient()

is_alive = (patients.date_of_death > winter_start) | patients.date_of_death.is_null()

dataset.define_population(is_registered & is_alive)

# 4. BASELINE DEMOGRAPHICS
dataset.age = patients.age_on(winter_start)
dataset.sex = patients.sex
# Fixed: Pulling nhs_region by querying the patient's active practice on that date
dataset.nhs_region = practice_registrations.for_patient_on(winter_start).practice.nhs_region

# 5. CHRONIC RESPIRATORY DISEASE CODELISTS
asthma_codes = codelist_from_csv("codelists/bristol-asthma.csv", system="snomed")
copd_codes   = codelist_from_csv("codelists/bristol-copd.csv", system="snomed")
ild_codes    = codelist_from_csv("codelists/bristol-ild-snomed.csv", system="snomed")
bronch_codes = codelist_from_csv("codelists/local/bronchiectasis-snomed.csv", system="snomed")

# Tag chronic flag profiles matching background histories
dataset.has_asthma = patients.with_these_clinical_events(asthma_codes, on_or_before=winter_start).exists_for_patient()
dataset.has_copd   = patients.with_these_clinical_events(copd_codes, on_or_before=winter_start).exists_for_patient()
dataset.has_ild    = patients.with_these_clinical_events(ild_codes, on_or_before=winter_start).exists_for_patient()
dataset.has_bronch = patients.with_these_clinical_events(bronch_codes, on_or_before=winter_start).exists_for_patient()

# 6. ACUTE RESPIRATORY INFECTION OUTCOMES (Primary Admissions via APCS)
pneumonia_codes = codelist_from_csv("codelists/bristol-pneumonia-secondary-care.csv", system="icd10")
rsv_codes       = codelist_from_csv("codelists/local/rsv-icd10.csv", system="icd10")
influenza_codes = codelist_from_csv("codelists/opensafely-acute-respiratory-illness-secondary-care.csv", system="icd10")

# Pull the earliest admission date within the winter window for each condition using the apcs table
dataset.admission_pneumonia = apcs.where(
    apcs.primary_diagnosis.is_in(pneumonia_codes)
).where(
    apcs.admission_date.is_between(winter_start, winter_end)
).sort_by(apcs.admission_date).first_for_patient().admission_date

dataset.admission_rsv = apcs.where(
    apcs.primary_diagnosis.is_in(rsv_codes)
).where(
    apcs.admission_date.is_between(winter_start, winter_end)
).sort_by(apcs.admission_date).first_for_patient().admission_date

dataset.admission_influenza = apcs.where(
    apcs.primary_diagnosis.is_in(influenza_codes)
).where(
    apcs.admission_date.is_between(winter_start, winter_end)
).sort_by(apcs.admission_date).first_for_patient().admission_date

dataset.admission_covid = apcs.where(
    apcs.primary_diagnosis.is_in(influenza_codes)
).where(
    apcs.admission_date.is_between(winter_start, winter_end)
).sort_by(apcs.admission_date).first_for_patient().admission_date