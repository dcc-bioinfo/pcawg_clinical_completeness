#!/usr/bin/python
import re

# possible empty field values
na_regex = "^(N/A|-777|-888|none)$"


# Generic Clinical Completness checks 
# Check done where one field's completeness is dependent on the value of another field (dependent_field and dependent_value)
def clinical_rule(dependent_field, dependent_value, field, heading, clinical, total_clinical):
   if (re.search(dependent_value, dependent_field)):
      total_clinical[heading] += 1
      if (not(re.search(na_regex, field))):
         clinical[heading] += 1
         

# This check is similar to clinical_rule, but instead of using na_regex, it uses a field-specific regex to check if a value is required for the field
def clinical_one_field_rule(regex, value, heading, clinical, total_clinical):
   total_clinical[heading] += 1
   if (not(re.search(regex, value))):
      clinical[heading] += 1

def cellularity_rule(percentage_cellularity, level_of_cellularity):
   if ( (re.search('-777|-888', percentage_cellularity)) and (re.search('-777|-888', level_of_cellularity)) ):
      return False
   else:
      return True

### Donor Validation Clinical Completeness Rules
def compute_donorCompleteness(donor_headings, donor_fields, donor_clinical, total_donor_clinical, data):
   for i, value in enumerate(donor_headings):
      if donor_headings[i] in donor_clinical:
         # donor_survival_time is expected to be completed if donor_vital_status is deceased
         if donor_headings[i] == 'donor_survival_time':
            clinical_rule(data[3], '2|-777|-888', data[i], donor_headings[i], donor_clinical, total_donor_clinical)
         # donor_relapse_interval is expected to be completed if disease_status_last_followup is progression (codelist value 3) or relapse (codelist value 4)
         elif donor_headings[i] == 'donor_relapse_interval':
            clinical_rule(data[4], '3|4|-777|-888', data[i], donor_headings[i], donor_clinical, total_donor_clinical)
         # donor_interval_of_last_followup is expected to be completed if disease_status_last_followup is progression (codelist value 3) or relapse (codelist value 4)
         elif donor_headings[i] == 'donor_interval_of_last_followup':
            clinical_rule(data[4], '3|4|-777|-888', data[i], donor_headings[i], donor_clinical, total_donor_clinical)
         # cancer_history_first_degree_relative is considered incomplete if codelist value 3 used (unknown)
         elif donor_headings[i] == 'cancer_history_first_degree_relative':
            clinical_one_field_rule('3|-777|-888', data[i], donor_headings[i], donor_clinical, total_donor_clinical)
         # prior_malignancy is considered incomplete if codelist value 3 used (unknown)
         elif donor_headings[i] == 'prior_malignancy':
            clinical_one_field_rule('3|-777|-888', data[i], donor_headings[i], donor_clinical, total_donor_clinical)
         # for any other field, simply check if NA regex is used. If field is complete, add one to field in donor_clinical dictionary
         elif (not(re.search(na_regex, data[i]))):
            donor_clinical[donor_headings[i]]  = donor_clinical[donor_headings[i]] +  1
            total_donor_clinical[donor_headings[i]] += 1
	 else:
            total_donor_clinical[donor_headings[i]] += 1
   return donor_clinical, total_donor_clinical


### Donor Exposure Clinical Completeness Rules
def compute_exposureCompleteness(exposure_headings, exposure_fields, exposure_clinical, total_exposure_clinical, data):
   for i, value in enumerate(exposure_headings):
      if exposure_headings[i] in exposure_fields:
         # if donor has a smoking history, then the tobacco_smoking_intensity should be specified
         if exposure_headings[i] == 'tobacco_smoking_intensity':
            clinical_rule(data[4], '2|3|4|5', data[i], exposure_headings[i], exposure_clinical, total_exposure_clinical)
         # if donor has an alcohol history, then the alcohol_history_intensity should be filled in
         elif exposure_headings[i] == 'alcohol_history_intensity':
            clinical_rule(data[6], '1', data[i], exposure_headings[i], exposure_clinical, total_exposure_clinical)
         # for any other field, simply check if NA regex is used. If field is complete, add one to field in exposure_clinical dictionary
         elif (not(re.search(na_regex, data[i]))):
            exposure_clinical[exposure_headings[i]]  = exposure_clinical[exposure_headings[i]] +  1
            total_exposure_clinical[exposure_headings[i]] += 1
         else:
            total_exposure_clinical[exposure_headings[i]] += 1
   return exposure_clinical, total_exposure_clinical


### Donor Family Clinical Completness Rules
def compute_familyCompleteness(family_headings, family_fields, family_clinical, total_family_clinical, data):
   for i, value in enumerate(family_headings):
      if family_headings[i] in family_fields:
         # if donor_has_relative_with_cancer_history is 'yes' (1), then relationship_type should be completed
         if family_headings[i] == 'relationship_type':
            clinical_rule(data[1], '1', data[i], family_headings[i], family_clinical, total_family_clinical)
         # if donor_has_relative_with_cancer_history is 'yes' (1), then data submitter should provide information about the affected relative's sex, age, disease and ICD10 code.  
         if (re.search('relationship_sex|relationship_age|relationship_disease_icd10|relationship_disease', family_headings[i])):
            clinical_rule(data[2], '1|2|3|4|5', data[i], family_headings[i], family_clinical, total_family_clinical)
         # for any other field, simply check if NA regex is used. If field is complete, add one to field in family_clinical dictionary
         elif (not(re.search(na_regex, data[i]))):
            family_clinical[family_headings[i]]  = family_clinical[family_headings[i]] +  1
            total_family_clinical[family_headings[i]] += 1
         else:
            total_family_clinical[family_headings[i]] += 1
   return family_clinical, total_family_clinical


### Donor Therapy Clinical Completeness Rules
def compute_therapyCompleteness(therapy_headings, therapy_fields, therapy_clinical, total_therapy_clinical, data):
   for i, value in enumerate(therapy_headings):
      if therapy_headings[i] in therapy_fields:
         # if first_therapy is specified, the project should provide data on the response, start interval and duration of the first therapy
         if (re.search('first_therapy_response|first_therapy_start_interval|first_therapy_duration', therapy_headings[i])):
            clinical_rule(data[3], '[2|3|4|5|6|7|8|9|10|11]', data[i], therapy_headings[i], therapy_clinical, total_therapy_clinical)
         # likewise if second_therapy is specified, the project should provide clinical data on the response, start interval and duration of the second therapy
         if (re.search('second_therapy_response|second_therapy_start_interval|second_therapy_duration', therapy_headings[i])):
            clinical_rule(data[8], '[2|3|4|5|6|7|8|9|10|11]', data[i], therapy_headings[i], therapy_clinical, total_therapy_clinical)
         # for any other field, simply check if NA regex is used. If field is complete, add one to field in therapy_clinical dictionary
         elif (not(re.search(na_regex, data[i]))):
            therapy_clinical[therapy_headings[i]]  = therapy_clinical[therapy_headings[i]] +  1
            total_therapy_clinical[therapy_headings[i]] += 1
         else:
            total_therapy_clinical[therapy_headings[i]] += 1
   return therapy_clinical, total_therapy_clinical

       
            

### Specimen Clinical Completeness Rules
def compute_specimenCompleteness(specimen_headings, specimen_fields, specimen_clinical, total_specimen_clinical, data):
   for i, value in enumerate(specimen_headings):
      if specimen_headings[i] in specimen_clinical:
         # if specimen type is tumour, then  tumour related fields should be completed. These include any fields in the specimen data type that begin with "tumour_* and the specimen_donor_treatment_type field. 
         if (re.match('^tumour_|specimen_donor_treatment_type', specimen_headings[i])):
            clinical_rule(data[2], '109|110|111|112|113|114|115|116|117|118|119|120|121|122|123|124|125|126', data[i], specimen_headings[i], specimen_clinical, total_specimen_clinical)
         # Only one of the cellularity fields needs to be completed. 
         elif specimen_headings[i] == 'percentage_celluarity':
            if (cellularity_rule(data[i], data[i+1])):
               specimen_clinical[specimen_headings[i]] = specimen_clinical[specimen_headings[i]] + 1
         elif specimen_headings[i] == 'level_of_celluarity':
            if (cellularity_rule(data[i-1], data[i])):
               specimen_clinical[specimen_headings[i]] = specimen_clinical[specimen_headings[i]] + 1
         # for any other field, simply check if NA regex is used. If field is complete, add one to field in specimen_clinical dictionary
         elif (not(re.search(na_regex, data[i]))):
	    specimen_clinical[specimen_headings[i]] = specimen_clinical[specimen_headings[i]] + 1            
            total_specimen_clinical[specimen_headings[i]] += 1
         else:
           total_specimen_clinical[specimen_headings[i]] += 1
   return specimen_clinical, total_specimen_clinical


### Sample Clinical Completeness Rules
def compute_sampleCompleteness(sample_headings, sample_fields, sample_clinical, total_sample_clinical, data):
   for i, value in enumerate(sample_headings):
      # Only one of the cellularity fields needs to be completed. 
      if sample_headings[i] in sample_clinical:
         if sample_headings[i] == 'percentage_celluarity':
            if (cellularity_rule(data[i], data[i+1])):
               sample_clinical[sample_headings[i]] = sample_clinical[sample_headings[i]] + 1
         elif sample_headings[i] == 'level_of_celluarity':
            if (cellularity_rule(data[i-1], data[i])):
               sample_clinical[specimen_headings[i]] = sample_clinical[sample_headings[i]] + 1
         # for any other field, simply check if NA regex is used. If field is complete, add one to field in specimen_clinical dictionary
         elif (not(re.search(na_regex, data[i]))):
	    sample_clinical[sample_headings[i]] = sample_clinical[sample_headings[i]] + 1            
            total_sample_clinical[sample_headings[i]] += 1
         else:
            total_sample_clinical[sample_headings[i]] += 1
   return sample_clinical, total_sample_clinical



