#!/usr/bin/python
# compute_pcawg_clinical_completeness.py
# This script computes the % clinical completeness for a subset of clinical fields for PCAWG data only

import re
import json
import os
import fnmatch
import sys, getopt
import collections
from decimal import Decimal 
import parse_data
import dcc_rules

## Example: python compute_pcawg_clinical_completeness.py -i ~/submission_files/ICGC20/BOCA-UK -n "Bone Cancer" -c "United Kingdom"

try:
   opts, args = getopt.getopt(sys.argv[1:], "hi:n:c:", ["inputdir=", "project_name", "country"])
except getopt.GetoptError:
      print 'compute_pcawg_clinical_completeness.py -i <inputdir> -n <project_name> -c <country>'
      sys.exit(2)
for opt, arg in opts:
   if opt == '-h':
      print 'compute_pcawg_clinical_completeness.py -i <inputdir> -n <project_name> -c <country>'
      sys.exit()
   elif opt in ("-i", "--inputdir"):
      inputDir = arg
   elif opt in ("-n", "--project_name"):
      project_name = arg
   elif opt in ("-c", "--country"):
      country = arg


na_regex = "^(N/A|-777|-888|none)$"
project_info = {}
project = (inputDir.split("/"))[-1]
print "Processing %s (%s) - %s"%(project, project_name, country)


outDonors = open("PCAWG_Donor_Completeness_ICGC21.tsv", "a")
outSpecimens = open("PCAWG_Specimen_Completeness_ICGC21.tsv", "a")
outSamples = open("PCAWG_Sample_Completeness_ICGC21.tsv", "a")
outExposure = open("PCAWG_Exposure_Completeness_ICGC21.tsv", "a")
outFamily = open("PCAWG_Family_Completeness_ICGC21.tsv", "a")
outTherapy = open("PCAWG_Therapy_Completeness_ICGC21.tsv", "a")

pcawg_donors = {}
tcga_donor_mapping = {}
tcga=re.compile("\w+\-US$")


# arrays of PCAWG specific clinical fiels to check clinical completeness for (can add additional clinical fields if necessary)
donor_fields  = ['donor_id', 'study', 'donor_sex','donor_region_of_residence','donor_vital_status','disease_status_last_followup','donor_relapse_type','donor_age_at_diagnosis','donor_age_at_enrollment','donor_age_at_last_followup','donor_relapse_interval','donor_diagnosis_icd10','donor_tumour_staging_system_at_diagnosis','donor_tumour_stage_at_diagnosis','donor_survival_time','donor_interval_of_last_followup','prior_malignancy','cancer_type_prior_malignancy','cancer_history_first_degree_relative', 'donor_primary_treatment_interval']
specimen_fields = ['donor_id', 'specimen_id', 'specimen_type', 'specimen_interval', 'specimen_donor_treatment_type', 'specimen_processing', 'specimen_storage', 'tumour_confirmed', 'specimen_biobank','specimen_available','tumour_histological_type','tumour_grading_system','tumour_grade','tumour_stage_system','tumour_stage','digital_image_of_stained_section','percentage_cellularity','level_of_cellularity']
sample_fields = ['analyzed_sample_id','specimen_id','analyzed_sample_interval','percentage_cellularity','level_of_cellularity','study']
exposure_fields = ['donor_id', 'tobacco_smoking_history_indicator', 'tobacco_smoking_intensity', 'alcohol_history', 'alcohol_history_intensity']
family_fields = ['donor_id', 'donor_has_relative_with_cancer_history', 'relationship_type', 'relationship_sex', 'relationship_age', 'relationship_disease_icd10', 'relationship_disease']
therapy_fields = ['donor_id', 'first_therapy_start_interval', 'first_therapy_duration', 'first_therapy_type', 'first_therapy_response', 'first_therapy_therapeutic_intent', 'second_therapy_start_interval', 'second_therapy_duration', 'second_therapy_type', 'second_therapy_response', 'second_therapy_therapeutic_intent']


# Donor
# This function processes each donor file in DCC submission and computes the clinical completeness for each donor clinical field
# Returns: dicitonaries of actual and expected completion counts keyed by donor clinical field
def process_donor(donorFiles):
   total_donor_clinical = {}	# Dictionary of total number of donors that are expected to be complete for a specific field 
   donor_clinical = {}		# Dictionary of actual number of donors that are complete for a specific field	 
   donors = {}			# Dictionary of donors
   global tcga_donor_mapping	# TCGA donor mapping dictionary
   # set counts for each field to 0
   for field in donor_fields:
      total_donor_clinical[field] = 0 	# dictionary of expected number of donors for which each field is expected to be completed, keyed by donor clinical fields
      donor_clinical[field] = 0		# dictionary of actual number of donors for which each field is completed. Keyed by donor clinical fields
   for donor_file in donorFiles:
      header = 1
      file_content = donor_file.readlines()
      donor_headings = []
      for line in file_content:
         line = line.rstrip("\n")
         data = line.split("\t")
         donor_id = data[0]
         if header:
            donor_headings = data
            header = 0
            next
         else:
            # TCGA donor IDs are different from DCC donors IDs. Populate dictionary to keep track of PCAWG <-> DCC TCGA donor_id mapping
            if tcga.match(project):
               tcga_donor_mapping[donor_id] = data[16].lower()
               donor_id = data[16].lower()
            # Only compute clinical completeness if donor is a PCAWG donor
            if donor_id in pcawg_donors:
               # get actual (donor_clinical) and expected (total_donor_clinical) PCAWG donor counts for each donor clinical field
               donor_clinical, total_donor_clinical = dcc_rules.compute_donorCompleteness(donor_headings, donor_fields, donor_clinical, total_donor_clinical, data)
               donors[data[0]] = data[0]
   return donor_clinical, total_donor_clinical, donors



# Exposure
def process_donorExposure(exposureFiles):
   total_exposure_clinical = {}
   exposure_clinical = {}
   for field in exposure_fields:
      total_exposure_clinical[field] = 0	# dictionary of expected number of donors for which each field is expected to be completed. Keyed by exposure clincial fields
      exposure_clinical[field] = 0		# dictionary of actual number of donors for which each field is completed. Keyed by exposure clinical fields
   for exposure_file in exposureFiles:
      header = 1
      exposure_content = exposure_file.readlines()
      exposure_headings = []
      for line in exposure_content:
         line = line.rstrip("\n")
         data = line.split("\t")
         donor_id = data[0]
         if header:
            exposure_headings = data
            total_exposure_headings = len(exposure_headings)
            header = 0
            next
         else:
            if tcga.match(project) and (donor_id in tcga_donor_mapping):
               donor_id = tcga_donor_mapping[donor_id]
            if donor_id in pcawg_donors:
               # get actual (exposure_clinical) and expected (total_exposure_clinical) PCAWG donor counts for each exposure field
               exposure_clinical, total_exposure_clinical = dcc_rules.compute_exposureCompleteness(exposure_headings, exposure_fields, exposure_clinical, total_exposure_clinical, data)
   return exposure_clinical, total_exposure_clinical



# Therapy
def process_donorTherapy(therapyFiles):
   total_therapy_clinical = {}
   therapy_clinical = {}
   for field in therapy_fields:
      total_therapy_clinical[field] = 0	# dictionary of expected number of donors for which each field is expected to be completed. Keyed by therapy clincial fields
      therapy_clinical[field] = 0	# dictionary of actual number of donors for which each field is completed. Keyed by therapy clinical fields
   for therapy_file in therapyFiles:
      header = 1
      therapy_content = therapy_file.readlines()
      therapy_headings = []
      for line in therapy_content:
         line = line.rstrip("\n")
         data = line.split("\t")
         donor_id = data[0]
         if header:
            therapy_headings = data
            header = 0
            next
         else:
            if tcga.match(project) and (donor_id in tcga_donor_mapping):
               donor_id = tcga_donor_mapping[donor_id]
            if donor_id in pcawg_donors:
               # get actual (therapy_clinical) and expected (total_therapy_clinical) PCAWG donor counts for each therapy field
               therapy_clinical, total_therapy_clinical = dcc_rules.compute_therapyCompleteness(therapy_headings, therapy_fields, therapy_clinical, total_therapy_clinical, data)
   return therapy_clinical, total_therapy_clinical  


# Family
def process_donorFamily(familyFiles):
   total_family_clinical = {}
   family_clinical = {}
   for field in family_fields:
      total_family_clinical[field] = 0	# dictionary of expected number of donors for which each field is expected to be completed. Keyed by family clinical fields
      family_clinical[field] = 0	# dictionary of actual number of donors for which each field is completed. Keyed by family clinical fields
   checked_family_donor_ids = {}
   for family_file in familyFiles:
      header = 1
      family_content = family_file.readlines()
      family_headings = []
      for line in family_content:
         line = line.rstrip("\n")
         data = line.split("\t")
         donor_id = data[0]
         if header:
            family_headings = data
            header = 0
            next
         else:
            if tcga.match(project) and (donor_id in tcga_donor_mapping):
               donor_id = tcga_donor_mapping[donor_id]
            if donor_id in pcawg_donors and donor_id not in checked_family_donor_ids:
               checked_family_donor_ids[donor_id] = donor_id
               # get actual (family_clinical) and expected (total_family_clinical) PCAWG donor counts for each family field
               family_clinical, total_family_clinical = dcc_rules.compute_familyCompleteness(family_headings, family_fields, family_clinical, total_family_clinical, data)
   return family_clinical, total_family_clinical



# Specimen
def process_specimen(specimenFiles):
   total_specimen_clinical = {}	# dictionary of expected number of donors for which each field is expected to be completed. Keyed by specimen clincial fields
   specimen_clinical = {}	# dictionary of actual number of donors for which each field is completed. Keyed by therapy clinical fields

   specimens = {}		# dictionary of specimens (not really needed. remanents of another script...)
   specimen_to_donor = {}	# specimen to donor mapping
   total_specimen_rows = 0
   for field in specimen_fields:
      total_specimen_clinical[field] = 0
      specimen_clinical[field] = 0
   for specimen_file in specimenFiles:
      header = 1
      specimen_content = specimen_file.readlines()
      specimen_headings = []
      for line in specimen_content:
         line = line.rstrip("\n")
         data = line.split("\t")
         donor_id = data[0]
         if header:
             specimen_headings = data
             header = 0
             next
         else:
            if tcga.match(project) and (donor_id in tcga_donor_mapping):
               donor_id = tcga_donor_mapping[donor_id]
            specimen_to_donor[data[1]] = donor_id
            if donor_id in pcawg_donors:
               # get actual (specimen_clinical) and expected (total_specimen_clinical) specimen counts for each specimen field, only for specimens belonging to PCAWG donors
               specimen_clinical, total_specimen_clinical = dcc_rules.compute_specimenCompleteness(specimen_headings, specimen_fields, specimen_clinical, total_specimen_clinical, data)
               specimens[data[1]] = data[0]
               total_specimen_rows = total_specimen_rows + 1
   return specimen_clinical, total_specimen_clinical, specimens, specimen_to_donor



# Sample
def process_sample(sampleFiles, donor_clinical):
   total_sample_clinical = {}	# dictionary of expected number of donors for which each field is expected to be completed. Keyed by sample clincial fields
   sample_clinical = {}		# dictionary of actual number of donors for which each field is completed. Keyed by sample clincial fields
   checked_pcawg_donors = {}
   samples = {}
   sample_to_donor = {}
   total_sample_rows = 0
   for field in sample_fields:
      total_sample_clinical[field] = 0
      sample_clinical[field] = 0
   for sample_file in sampleFiles:
      header = 1
      sample_content = sample_file.readlines()
      sample_headings = []
      for line in sample_content:
         line = line.rstrip("\n")
         data = line.split("\t")
         if header:
            sample_headings = data
            header = 0
            next
         else:
            if specimen_to_donor[data[1]] in pcawg_donors:
               sample_to_donor[data[0]] = specimen_to_donor[data[1]]
               samples[data[0]] = data[6]
               # get actual (specimen_clinical) and expected (total_specimen_clinical) sample counts for each sample field, only for samples belonging to PCAWG donors
               sample_clinical, total_sample_clinical = dcc_rules.compute_sampleCompleteness(sample_headings, sample_fields, sample_clinical, total_sample_clinical, data)
               total_sample_rows = total_sample_rows + 1
   for sample_id in samples:
      donor_id = sample_to_donor[sample_id]
      if (donor_id in pcawg_donors) and (donor_id not in checked_pcawg_donors):
         study_field = samples[sample_id]
         if (re.search('1|PCAWG', study_field)):
            checked_pcawg_donors[donor_id] = study_field
            donor_clinical['study'] = donor_clinical['study'] + 1
   return sample_clinical, total_sample_clinical, donor_clinical, checked_pcawg_donors, samples, sample_to_donor



# function to print out totals for donor clinical data to tab-delimited file. 
# Take actual counts (clinical_counts), expected counts (total_clinical_counts), fields, total_pcawg_donors and output file)
def print_donor_totals(clinical_counts, total_clinical_counts, fields, total_pcawg_donors, outFile):
   for i, value in enumerate(fields):
      fraction_complete = 0
      pct_complete = 0
      print "Field = %s"%fields[i]
      # if field is donor_id or study, then need to divide by number of total pcawg donors)
      if (re.match('donor_id|study', fields[i])):
         fraction_complete = (clinical_counts[fields[i]]/float(total_pcawg_donors))
         pct_complete = Decimal(str(fraction_complete)).quantize(Decimal('0.001'))*100
         print "Number of time completed = %s/%s"%(donor_clinical[donor_fields[i]], total_pcawg_donors)
      else:
         if (total_clinical_counts[fields[i]] != 0):
            fraction_complete = (clinical_counts[fields[i]]/float(total_clinical_counts[fields[i]]))
            pct_complete = Decimal(str(fraction_complete)).quantize(Decimal('0.001'))*100
   	    print "Number of time completed = %s/%s"%(clinical_counts[fields[i]], total_clinical_counts[fields[i]])
         else:
            if clinical_counts['donor_id'] == 0:
               pct_complete = 0
            else:
               # if field is not expected to be completed (ie. total_clinical_counts = 0), then this field is not applicable (using 0% would be be misinterpreted as it being incomplete)
	       pct_complete = 'Not applicable'
      print "Percent complete = %s\n"%pct_complete
      outFile.write("\t%s"%(pct_complete))
   outFile.write("\n")

# function to print out totals for specimen and sample clinical data to tab-delimited file
# Take actual counts (clinical_counts), expected counts (total_clinical_counts), fieldand output file)
def print_specimen_or_sample(clinical_counts, total_clinical_counts, fields, outFile):
   for i, value in enumerate(fields):
      fraction_complete = 0
      pct_complete = 0
      if (total_clinical_counts[fields[i]] != 0):
         fraction_complete = clinical_counts[fields[i]]/float(total_clinical_counts[fields[i]])
         pct_complete = Decimal(str(fraction_complete)).quantize(Decimal('0.001'))*100
         print "Field %s"%(fields[i])
         print "Number of times completed = %s/%s"%(clinical_counts[fields[i]], total_clinical_counts[fields[i]])
         print "Percent Complete = %s\n"%pct_complete
      else:
         pct_complete = 'Not applicable'
      outFile.write("\t%s"%(pct_complete))
   outFile.write("\n")


## Main ##


# Fetch clinical files for each clinical data type
donorFiles = get_data.getFile('^donor(\.[a-zA-Z0-9]+)?\.txt(?:\.gz|\.bz2)?$', inputDir)
specimenFiles = get_data.getFile('^specimen(\.[a-zA-Z0-9]+)?\.txt(?:\.gz|\.bz2)?$', inputDir)
sampleFiles = get_data.getFile('^sample(\.[a-zA-Z0-9]+)?\.txt(?:\.gz|\.bz2)?$', inputDir)
familyFiles = get_data.getFile('^family(\.[a-zA-Z0-9]+)?\.txt(?:\.gz|\.bz2)?$', inputDir)
exposureFiles = get_data.getFile('^exposure(\.[a-zA-Z0-9]+)?\.txt(?:\.gz|\.bz2)?$', inputDir)
therapyFiles = get_data.getFile('^therapy(\.[a-zA-Z0-9]+)?\.txt(?:\.gz|\.bz2)?$', inputDir)

# Store PCAWG donors from each project (pre-computed from another script)
pcawg_donors = get_data.parse_pcawg_donors(project)
print "Total number of PCAWG donors in %s = %s"%(project, len(pcawg_donors))

# Compute clinical completeness for each clinical data type
donor_clinical, total_donor_clinical, donors = process_donor(donorFiles)
exposure_clinical, total_exposure_clinical = process_donorExposure(exposureFiles)
therapy_clinical, total_therapy_clinical = process_donorTherapy(therapyFiles) 
family_clinical, total_family_clinical = process_donorFamily(familyFiles)
specimen_clinical, total_specimen_clinical, specimens, specimen_to_donor = process_specimen(specimenFiles)
sample_clinical, total_sample_clinical, donor_clinical, checked_pcawg_donors, samples, sample_to_donor = process_sample(sampleFiles, donor_clinical)

total_pcawg_donors = len(pcawg_donors)
total_donors = len(donors)
total_specimens = len(specimens)
total_samples = len(samples)

print "total pcawg donors in %s = %s"%(project, total_pcawg_donors)
print "total donors = %s\n"%total_donors
print "total specimens = %s\n"%total_specimens
print "total samples = %s\n"%total_samples


# Print % clinical completeness for each clinical field in separate files for each clinical data type
outDonors.write("%s\t%s\t%s\t%s"%(project, project_name, country, total_pcawg_donors))
print_donor_totals(donor_clinical, total_donor_clinical, donor_fields, total_pcawg_donors, outDonors)
      
outExposure.write("%s\t%s\t%s\t%s"%(project, project_name, country, len(pcawg_donors)))
print_donor_totals(exposure_clinical, total_exposure_clinical, exposure_fields, total_pcawg_donors, outExposure)

outFamily.write("%s\t%s\t%s\t%s"%(project, project_name, country, total_pcawg_donors))
print_donor_totals(family_clinical, total_family_clinical, family_fields, total_pcawg_donors, outFamily)

outTherapy.write("%s\t%s\t%s\t%s"%(project, project_name, country, total_pcawg_donors))
print_donor_totals(therapy_clinical, total_therapy_clinical, therapy_fields, total_pcawg_donors, outTherapy)

outSpecimens.write("%s\t%s\t%s\t%s"%(project, project_name, country, total_specimens))
print_specimen_or_sample(specimen_clinical, total_specimen_clinical, specimen_fields, outSpecimens)

outSamples.write("%s\t%s\t%s\t%s"%(project, project_name, country, total_samples))
print_specimen_or_sample(sample_clinical, total_sample_clinical, sample_fields, outSamples)

