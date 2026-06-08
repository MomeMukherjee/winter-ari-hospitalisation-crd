# =================================================================
# WINTER ARI HOSPITALISATION WITH CRD STUDY
# dataset_definition.py ~ parameterised by season year
#
# Run for a single season:
#   opensafely run generate_dataset_2018
#   (or via project.yaml which passes --season-year 2018)
#
# season_year = year in which the winter ENDS
# e.g. 2018 = winter 2017/18 (Oct 2017 ~ Mar 2018)
#
# Full year extracted (Apr to Mar) ~
# winter spike identified analytically in R,
# NOT predefined here
#
# CRD lookback from Apr 1 of previous year ~
# captures diagnoses made before winter
#
# =================================================================

from ehrql import create_dataset, days, years
from ehrql import get_parameter
from ehrql.tables.tpp import (
    patients,
    practice_registrations,
    apcs,
    clinical_events,
    ons_deaths,
)
from codelists import (
    asthma_snomed,
    asthma_resolved_snomed,
    copd_snomed,
    copd_resolved_snomed,
    ild_snomed,
    asthma_icd10,
    copd_icd10,
    ild_icd10_narrow,
    ild_icd10_broad,
    pneumonia_icd10,
    covid_icd10,
    ari_broad_icd10,
)
from study_dates import get_season_dates

# =================================================================
# PARAMETERS ~ passed from project.yaml or command line
# =================================================================

season_year = int(get_parameter("season_year", default="2018"))
dates = get_season_dates(season_year)

# Unpack all dates for readability
extract_start    = dates["extract_start"]    # Apr 1 prev year
extract_end      = dates["extract_end"]      # Mar 31 season year
reg_lookback     = dates["reg_lookback"]     # 12m before extract
crd_lookback     = dates["crd_lookback"]     # Apr 1 prev year
season_start     = dates["season_start"]     # Oct 1 prev year

# =================================================================
# LOCAL CODES ~ no formal codelist yet
# =================================================================

cat > /tmp/fix_local_codes.py << 'PYEOF'
import csv

def load_local_csv(path):
    with open(path) as f:
        reader = csv.DictReader(f)
        return [row["code"] for row in reader]

# Write the replacement block
new_block = '''
# =================================================================
# LOCAL CODES ~ loaded from codelists/local/ CSVs
# No formal opencodelists.org entry yet
# Sources documented in CODELIST-INVENTORY.md
# =================================================================

import csv, os

def _load_local(filename):
    path = os.path.join("codelists", "local", filename)
    with open(path) as f:
        return [row["code"] for row in csv.DictReader(f)]

bronchiectasis_snomed_codes = _load_local("bronchiectasis-snomed.csv")
influenza_icd10_codes       = _load_local("influenza-icd10.csv")
rsv_icd10_codes             = _load_local("rsv-icd10.csv")
'''

with open("analysis/dataset_definition.py") as f:
    content = f.read()

# Find and replace the old local codes block
old_start = "# =================================================================\n# LOCAL CODES ~ no formal codelist yet"
old_end   = ']\n\n# ='

idx_start = content.find(old_start)
idx_end   = content.find("# =================================================================\n# CREATE DATASET")

if idx_start > 0 and idx_end > 0:
    content = content[:idx_start] + new_block + "\n" + content[idx_end:]
    with open("analysis/dataset_definition.py", "w") as f:
        f.write(content)
    print("Done ~ local codes now load from CSV files")
else:
    print("Pattern not found ~ edit manually")
PYEOF
python3 /tmp/fix_local_codes.py

# =================================================================
# CREATE DATASET
# =================================================================

dataset = create_dataset()

# =================================================================
# REGISTRATION ~ for this season
# =================================================================

registration = practice_registrations.for_patient_on(season_start)

has_registration = registration.exists_for_patient()

# Registered >= 12 months before extract start
registered_12m = (
    practice_registrations
    .where(
        practice_registrations.start_date.is_on_or_before(reg_lookback)
    )
    .exists_for_patient()
)

# =================================================================
# POPULATION DEFINITION
# Adults >= 18 at season start, registered >= 12m,
# alive at season start
# =================================================================

age_at_season_start = patients.age_on(season_start)

alive_at_season_start = (
    patients.date_of_death.is_after(season_start)
    | patients.date_of_death.is_null()
)

dataset.define_population(
    has_registration
    & registered_12m
    & (age_at_season_start >= 18)
    & (age_at_season_start <= 120)
    & alive_at_season_start
)

# =================================================================
# SECTION 1: DEMOGRAPHICS
# Fixed at season start
# =================================================================

dataset.season_year  = season_year
dataset.age          = age_at_season_start
dataset.sex          = patients.sex
dataset.dob          = patients.date_of_birth
dataset.date_death   = patients.date_of_death
dataset.gp_practice  = registration.practice_pseudo_id
dataset.stp          = registration.practice_stp
dataset.region       = registration.practice_nuts1_region_name

# =================================================================
# SECTION 2: CRD STATUS
# Diagnoses recorded from crd_lookback (Apr 1 prev year)
# to season start (Oct 1 prev year)
# Captures diagnoses made in run-up to winter
# =================================================================

# --- ASTHMA ---
has_asthma = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(asthma_snomed))
    .where(clinical_events.date.is_on_or_after(crd_lookback))
    .where(clinical_events.date.is_on_or_before(season_start))
    .exists_for_patient()
)
has_asthma_resolved = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(asthma_resolved_snomed))
    .where(clinical_events.date.is_on_or_before(season_start))
    .exists_for_patient()
)
dataset.asthma = has_asthma & ~has_asthma_resolved

# --- COPD ---
has_copd = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(copd_snomed))
    .where(clinical_events.date.is_on_or_after(crd_lookback))
    .where(clinical_events.date.is_on_or_before(season_start))
    .exists_for_patient()
)
has_copd_resolved = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(copd_resolved_snomed))
    .where(clinical_events.date.is_on_or_before(season_start))
    .exists_for_patient()
)
dataset.copd = has_copd & ~has_copd_resolved

# --- ILD ---
dataset.ild = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(ild_snomed))
    .where(clinical_events.date.is_on_or_after(crd_lookback))
    .where(clinical_events.date.is_on_or_before(season_start))
    .exists_for_patient()
)

# --- BRONCHIECTASIS ---
dataset.bronchiectasis = (
    clinical_events
    .where(clinical_events.snomedct_code.is_in(
        bronchiectasis_snomed_codes
    ))
    .where(clinical_events.date.is_on_or_after(crd_lookback))
    .where(clinical_events.date.is_on_or_before(season_start))
    .exists_for_patient()
)

# --- ANY CRD ---
dataset.any_crd = (
    dataset.asthma
    | dataset.copd
    | dataset.ild
    | dataset.bronchiectasis
)

# --- CRD COMBINATION (for Q1 subgroups) ---
dataset.n_crd = (
    dataset.asthma.as_int()
    + dataset.copd.as_int()
    + dataset.ild.as_int()
    + dataset.bronchiectasis.as_int()
)

# =================================================================
# SECTION 3: ARI OUTCOMES
# Full year window (extract_start to extract_end)
# Winter spike determined analytically in R
# TWO definitions per outcome:
#   _primary ~ ARI as primary (first position) diagnosis
#   _any     ~ ARI in any diagnosis position (1-20)
# PLUS: admission date for time-series; count; LOS
# =================================================================

def ari_vars(dataset, name, icd_codes):
    """
    Helper ~ creates 7 outcome variables per ARI type:
      name_primary       bool ~ primary diagnosis
      name_any           bool ~ any diagnosis position
      name_primary_date  date ~ first primary admission date
      name_any_date      date ~ first any-position admission date
      name_primary_count int  ~ count of primary admissions
      name_any_count     int  ~ count of any-position admissions
      name_los           int  ~ total length of stay (primary)
    """
    # Primary diagnosis
    primary = (
        apcs
        .where(apcs.primary_diagnosis.is_in(icd_codes))
        .where(apcs.admission_date.is_on_or_after(extract_start))
        .where(apcs.admission_date.is_on_or_before(extract_end))
    )
    # Any diagnosis position (1-20)
    any_pos = (
        apcs
        .where(
            apcs.primary_diagnosis.is_in(icd_codes)
            | apcs.secondary_diagnosis.is_in(icd_codes)
        )
        .where(apcs.admission_date.is_on_or_after(extract_start))
        .where(apcs.admission_date.is_on_or_before(extract_end))
    )

    setattr(dataset, f"{name}_primary",
        primary.exists_for_patient())
    setattr(dataset, f"{name}_any",
        any_pos.exists_for_patient())
    setattr(dataset, f"{name}_primary_date",
        primary.sort_by(apcs.admission_date)
               .first_for_patient().admission_date)
    setattr(dataset, f"{name}_any_date",
        any_pos.sort_by(apcs.admission_date)
               .first_for_patient().admission_date)
    setattr(dataset, f"{name}_primary_count",
        primary.count_for_patient())
    setattr(dataset, f"{name}_any_count",
        any_pos.count_for_patient())
    setattr(dataset, f"{name}_los",
        primary.sum_by_patient(
            apcs.days_in_critical_care   # proxy ~ replace with LOS when available
        ))


# Apply to each ARI outcome
ari_vars(dataset, "pneumonia",  pneumonia_icd10)
ari_vars(dataset, "covid",      covid_icd10)
ari_vars(dataset, "influenza",  influenza_icd10_codes)
ari_vars(dataset, "rsv",        rsv_icd10_codes)
ari_vars(dataset, "ari_broad",  ari_broad_icd10)

# =================================================================
# SECTION 4: ARI-RELATED MORTALITY
# Death with ARI recorded ~ ONS cause of death
# Two definitions:
#   ari_death_primary  ~ ARI as underlying cause
#   ari_death_any      ~ ARI as any cause
# For sensitivity analysis
# =================================================================

all_ari_icd10 = (
    list(pneumonia_icd10)
    + list(covid_icd10)
    + influenza_icd10_codes
    + rsv_icd10_codes
)

dataset.ari_death_primary = (
    ons_deaths
    .where(ons_deaths.underlying_cause_of_death.is_in(all_ari_icd10))
    .where(ons_deaths.date.is_on_or_after(extract_start))
    .where(ons_deaths.date.is_on_or_before(extract_end))
    .exists_for_patient()
)

dataset.ari_death_date = (
    ons_deaths
    .where(ons_deaths.underlying_cause_of_death.is_in(all_ari_icd10))
    .where(ons_deaths.date.is_on_or_after(extract_start))
    .where(ons_deaths.date.is_on_or_before(extract_end))
    .sort_by(ons_deaths.date)
    .first_for_patient()
    .date
)

# =================================================================
# SECTION 5: REGISTRATION DATES
# For computing weekly denominators in R
# =================================================================

dataset.reg_start = (
    practice_registrations
    .sort_by(practice_registrations.start_date)
    .first_for_patient()
    .start_date
)

dataset.reg_end = (
    practice_registrations
    .sort_by(practice_registrations.end_date)
    .last_for_patient()
    .end_date
)
