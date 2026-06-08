from ehrql import codelist_from_csv

# --- CRD diagnosis ~ primary care (SNOMED) ---
asthma_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-ast_cod.csv",
    column="code",
)
asthma_resolved_snomed = codelist_from_csv(
    "codelists/pincer-ast_res.csv",
    column="code",
)
copd_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copd_cod.csv",
    column="code",
)
copd_resolved_snomed = codelist_from_csv(
    "codelists/nhsd-primary-care-domain-refsets-copdres_cod.csv",
    column="code",
)
ild_snomed = codelist_from_csv(
    "codelists/bristol-ild-snomed.csv",
    column="code",
)

# --- CRD diagnosis ~ hospital (ICD-10) ---
asthma_icd10 = codelist_from_csv(
    "codelists/bristol-asthma.csv",
    column="code",
)
copd_icd10 = codelist_from_csv(
    "codelists/bristol-copd.csv",
    column="code",
)
ild_icd10_narrow = codelist_from_csv(
    "codelists/bristol-pulmonary-fibrosis-interstitial-lung-disease.csv",
    column="code",
)
ild_icd10_broad = codelist_from_csv(
    "codelists/bristol-interstitial-lung-disease-icd10.csv",
    column="code",
)

# --- ARI outcomes ~ hospital (ICD-10) ---
pneumonia_icd10 = codelist_from_csv(
    "codelists/bristol-pneumonia-secondary-care.csv",
    column="code",
)
covid_icd10 = codelist_from_csv(
    "codelists/opensafely-covid-identification.csv",
    column="icd10_code",
)
ari_broad_icd10 = codelist_from_csv(
    "codelists/opensafely-acute-respiratory-illness-secondary-care.csv",
    column="code",
)
