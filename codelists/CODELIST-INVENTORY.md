# Codelist Inventory
# Study: Winter ARI Hospitalisation with CRD
# Last updated: June 2026
#
# Format: Disease | Coding system | [SPECIFIC/SENSITIVE] | Source | CSV filename | Status

## CRD ~ PRIMARY CARE (SNOMED)

| Disease | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Asthma exacerbations | SNOMED | SPECIFIC | OpenCodelists ~ bristol | bristol-exacerbations-of-asthma.csv | ✅ downloaded |
| COPD exacerbations | SNOMED | SENSITIVE | OpenCodelists ~ bristol | bristol-exacerbations-of-copd.csv | ✅ downloaded |
| ILD | SNOMED | SENSITIVE | OpenCodelists ~ bristol | bristol-ild-snomed.csv | ✅ downloaded |
| Bronchiectasis | SNOMED | SPECIFIC | HDR UK Gateway PH13/26 ~ Axson & Quint 2021 | local/bronchiectasis-snomed.csv | ✅ local CSV |

## CRD ~ HOSPITAL (ICD-10)

| Disease | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Asthma | ICD-10 | SPECIFIC | OpenCodelists ~ bristol | bristol-asthma.csv | ✅ downloaded |
| COPD | ICD-10 | SPECIFIC | OpenCodelists ~ bristol | bristol-copd.csv | ✅ downloaded |
| ILD narrow (IPF only) | ICD-10 | SPECIFIC | OpenCodelists ~ bristol | bristol-pulmonary-fibrosis-interstitial-lung-disease.csv | ✅ downloaded |
| ILD broad | ICD-10 | SENSITIVE | OpenCodelists ~ bristol | bristol-interstitial-lung-disease-icd10.csv | ✅ downloaded |
| Bronchiectasis | ICD-10 | SPECIFIC | HDR UK Gateway PH13/26 ~ Axson & Quint 2021 | local/bronchiectasis-icd10.csv | ✅ local CSV |

## ARI OUTCOMES ~ HOSPITAL (ICD-10)

| Disease | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Pneumonia | ICD-10 | SPECIFIC | OpenCodelists ~ bristol | bristol-pneumonia-secondary-care.csv | ✅ downloaded |
| COVID-19 | ICD-10 | SPECIFIC | OpenCodelists ~ opensafely | opensafely-covid-identification.csv | ✅ downloaded |
| Influenza | ICD-10 | SPECIFIC | Thompson 2020 England HES; Eurosurveillance 2025 | local/influenza-icd10.csv | ✅ local CSV |
| RSV | ICD-10 | SPECIFIC | PROMISE/Nair 2024 England HES; JOGH review 2025 | local/rsv-icd10.csv | ✅ local CSV |
| ARI non-specific | ICD-10 | SENSITIVE | OpenCodelists ~ opensafely ~ Warren-Gash | opensafely-acute-respiratory-illness-secondary-care.csv | ✅ downloaded |

## ARI OUTCOMES ~ PRIMARY CARE (SNOMED)

| Disease | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Pneumonia | SNOMED | SENSITIVE | OpenCodelists ~ bristol | bristol-pneumonia-snomed.csv | ✅ downloaded |
| URTI | SNOMED | SENSITIVE | OpenCodelists ~ bristol | bristol-urti-snomed.csv | ✅ downloaded |
| RSV | SNOMED | SENSITIVE | OpenCodelists ~ opensafely ~ Quint-checked | opensafely-rsv-identification-primary-care.csv | ✅ downloaded |

## ACUTE CARDIAC EVENTS ~ HOSPITAL (ICD-10)

| Disease | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Myocardial infarction | ICD-10 | SPECIFIC | OpenCodelists ~ opensafely | opensafely-myocardial-infarction.csv | ✅ downloaded |
| Heart failure | ICD-10 | SPECIFIC | HDR UK Gateway PH530/1060 ~ Kontopantelis 2021 | local/heart-failure-icd10.csv | ✅ local CSV |
| Cardiac arrest & arrhythmia | ICD-10 | SPECIFIC | WHO ICD-10 standard codes | local/cardiac-arrest-arrhythmia-icd10.csv | ✅ local CSV |

## MODIFIABLE RISK FACTORS

| Variable | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Smoking status ~ clear | SNOMED | SPECIFIC | OpenCodelists ~ opensafely | opensafely-smoking-clear-snomed.csv | ✅ downloaded |
| Influenza vaccination | SNOMED | SPECIFIC | NHSD FLU_COD refset Jun 2025 | nhsd-primary-care-domain-refsets-flu_cod.csv | ✅ downloaded |
| COPD medications | BNF/dm+d | SENSITIVE | OpenCodelists ~ bristol | bristol-copd-medications-bnf.csv | ✅ downloaded |
| Oral corticosteroids | BNF/dm+d | SPECIFIC | OpenCodelists ~ bristol | bristol-copd-exacerbation-medications-bnf.csv | ✅ downloaded |
| BMI | numerical | ~ | TPP table in ehrQL | ~ | no codelist needed |
| Blood pressure | numerical | ~ | TPP table in ehrQL | ~ | no codelist needed |
| Cholesterol | numerical | ~ | TPP table in ehrQL | ~ | no codelist needed |
| COVID vaccination | ~ | ~ | TPP vaccination table | ~ | no codelist needed |

## GAPS ~ NEED ACTION BEFORE REAL DATA RUN

| Variable | Gap | Action needed |
|---|---|---|
| Smoking status unclear | Version hash unconfirmed | Verify at opencodelists.org/codelist/opensafely/smoking-unclear-snomed/ |
| Pneumococcal vaccination | Version unconfirmed | Verify at opencodelists.org |
| RSV vaccination | No codelist exists anywhere | Create new codelist with Quint team |
| Asthma medications | Version hash unconfirmed | Verify at opencodelists.org/codelist/bristol/asthma-medications-bnf/ |
| Influenza ICD-10 | No formal opencodelists entry | Consider submitting to opensafely org |
| RSV ICD-10 | No formal opencodelists entry | Consider submitting to opensafely org |
| Heart failure ICD-10 | No formal opencodelists entry | Consider submitting to opensafely org |
| Bronchiectasis SNOMED/ICD-10 | No bristol/ or opensafely/ entry | Submit to opencodelists with Quint endorsement |
| Annual review codes asthma/COPD | Not yet identified | Search opencodelists.org |
| Self-management plan codes | Not yet identified | Search opencodelists.org |


## DISEASE MANAGEMENT INDICATORS

| Variable | System | Specificity | Source | CSV file | Status |
|---|---|---|---|---|---|
| Asthma annual review | SNOMED | SPECIFIC | OpenCodelists opensafely ~ QOF v44 | opensafely-asthma-annual-review-qof.csv | ⏳ to download |
| COPD annual review + rescue packs | CTV3 | SENSITIVE | OpenCodelists opensafely ~ ICS research | opensafely-copd-rescue-packs-and-annual-reviews.csv | ⏳ to download ~ CTV3 only |
| ICS high dose inhalers | dm+d | SPECIFIC | OpenCodelists opensafely ~ BTS-SIGN | opensafely-high-dose-ics-inhalers.csv | ⏳ to download |
| ICS low/medium dose inhalers | dm+d | SPECIFIC | OpenCodelists opensafely ~ BTS-SIGN | opensafely-low-and-medium-dose-ics-inhalers.csv | ⏳ to download |
| COPD ICS inhalers | dm+d | SPECIFIC | NHSD COPDICSDRUG_COD refset Sep 2025 | nhs-drug-refsets-copdicsdrug_cod.csv | ⏳ to download |
| Asthma self-management plan | SNOMED | ~ | [GAP] No codelist exists | ~ | ❌ needs creating |
| COPD self-management plan | SNOMED | ~ | [GAP] No codelist exists | ~ | ❌ needs creating |
| RTI primary care proxy | SNOMED | SENSITIVE | Use bristol-urti-snomed + bristol-pneumonia-snomed combined | already downloaded | ✅ use existing |

## UPDATED GAPS LIST ~ FOR QUINT MEETING

| Gap | Priority | Notes |
|---|---|---|
| Bronchiectasis SNOMED + ICD-10 | High ~ primary outcome | Submit to opencodelists with Quint endorsement |
| Influenza ICD-10 hospital | High ~ primary outcome | Consider formal submission to opensafely org |
| RSV ICD-10 hospital | High ~ primary outcome | Consider formal submission to opensafely org |
| Heart failure ICD-10 | Medium | Consider formal submission |
| Asthma self-management plan SNOMED | Medium | Create new from SNOMED 182836005 |
| COPD self-management plan SNOMED | Medium | Create new ~ discuss scope |
| COPD annual review SNOMED | Medium | CTV3 version exists ~ SNOMED version needed |
| RSV vaccination | High ~ risk factor | New vaccine ~ no codelist anywhere |
| Pneumococcal vaccination | Medium | Verify version on opencodelists.org |
| Smoking unclear SNOMED | Low ~ sensitivity only | Verify version hash |
| Asthma medications BNF | Medium | Verify version hash |

