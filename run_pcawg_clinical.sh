#!/bin/bash

INPUTDIR=""
OUTDIR=""
PROJECTLIST=""
DONOR_OUT="PCAWG_Donor_Completeness_ICGC20.tsv"
SPECIMEN_OUT="PCAWG_Specimen_Completeness_ICGC20.tsv"
SAMPLE_OUT="PCAWG_Sample_Completeness_ICGC20.tsv"
EXPOSURE_OUT="PCAWG_Exposure_Completeness_ICGC20.tsv"
FAMILY_OUT="PCAWG_Family_Completeness_ICGC20.tsv"
THERAPY_OUT="PCAWG_Therapy_Completeness_ICGC20.tsv"

while getopts "i:o:p:" OPTION; do
  case "$OPTION" in
    i)
      INPUTDIR=${OPTARG?}
      echo "input directory = ${INPUTDIR}";
    ;;
    p)
      PROJECTLIST=${OPTARG?}
      echo "project_list = ${PROJECTLIST}";
    ;;
    :)
      echo "Option -$OPTION requires the name of the input directory" >&2
      exit 1
      ;;
   esac
done

donor_fields=('project_code' 'project_name' 'country' 'total_donors' 'donor_id' 'study' 'donor_sex' 'donor_region_of_residence' 'donor_vital_status' 'disease_status_last_followup' 'donor_relapse_type' 'donor_age_at_diagnosis' 'donor_age_at_enrollment' 'donor_age_at_last_followup' 'donor_relapse_interval' 'donor_diagnosis_icd10' 'donor_tumour_staging_system_at_diagnosis' 'donor_tumour_stage_at_diagnosis' 'donor_survival_time' 'donor_interval_of_last_followup' 'prior_malignancy' 'cancer_type_prior_malignancy' 'cancer_history_first_degree_relative' 'donor_primary_treatment_interval')

specimen_fields=('project_code' 'project_name' 'country' 'total_specimens' 'donor_id' 'specimen_id' 'specimen_type' 'specimen_interval' 'specimen_donor_treatment_type' 'specimen_processing' 'specimen_storage' 'tumour_confirmed' 'specimen_biobank' 'specimen_available' 'tumour_histological_type' 'tumour_grading_system' 'tumour_grade' 'tumour_stage_system' 'tumour_stage' 'digital_image_of_stained_section' 'percentage_cellularity' 'level_of_cellularity')

sample_fields=('project_code' 'project_name' 'country' 'total_samples' 'analyzed_sample_id' 'specimen_id' 'analyzed_sample_interval' 'percentage_cellularity' 'level_of_cellularity' 'study')

exposure_fields=('project_code' 'project_name' 'country' 'total_pcawg_donors' 'donor_id' 'tobacco_smoking_history_indicator' 'tobacco_smoking_intensity' 'alcohol_history' 'alcohol_history_intensity')
family_fields=('project_code' 'project_name' 'country' 'total_pcawg_donors' 'donor_id' 'donor_has_relative_with_cancer_history' 'relationship_type' 'relationship_sex' 'relationship_age' 'relationship_disease_icd10' 'relationship_disease')
therapy_fields=('project_code' 'project_name' 'country' 'total_pcawg_donors' 'donor_id' 'first_therapy_start_interval' 'first_therapy_duration' 'first_therapy_type' 'first_therapy_response' 'first_therapy_therapeutic_intent' 'second_therapy_start_interval' 'second_therapy_duration' 'second_therapy_type' 'second_therapy_response' 'second_therapy_therapeutic_intent')

(IFS=$'\t'; echo "${donor_fields[*]}") > ${DONOR_OUT}
(IFS=$'\t'; echo "${specimen_fields[*]}") > ${SPECIMEN_OUT}
(IFS=$'\t'; echo "${sample_fields[*]}") > ${SAMPLE_OUT}
(IFS=$'\t'; echo "${exposure_fields[*]}") > ${EXPOSURE_OUT}
(IFS=$'\t'; echo "${family_fields[*]}") > ${FAMILY_OUT}
(IFS=$'\t'; echo "${therapy_fields[*]}") > ${THERAPY_OUT}

STDOUTFILE="pcawg_clinical.stdout";

while IFS=$'\t' read -r -a array;
do
        project=${array[0]}
        project_name=${array[1]}
        country=${array[2]}
        echo `python compute_pcawg_clinical_completeness.py -i $INPUTDIR/$project -n "${project_name}" -c "${country}" >> ${STDOUTFILE}`;
	echo "Done processing $project";
done < ${PROJECTLIST};
