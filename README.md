# pcawg_clinical_completeness
# PCAWG clinical completeness scripts

#### To run: ####
 ./run_pcawg_clinical -i input_submission_directory -p list_of_projects (pcawg projects in this case)
 
Example: ./run_pcawg_clinical.sh -i /hdfs/dcc/icgc/submission/ICGC20 -p pcawg_projects.txt

#### Output ####
 Will genererate 5 tab-delimited tables (for each clinical data type) summarizing clinical completeness for each clinical field

#### Contents ####


 compute_pcawg_clinical_completeness.py:  python script to generate clinical completeness metrics for a given project
 run_pcawg_clinical.sh: wrapper bash script

 dcc_rules.py: functions defining clinical rules for each clinical data type
 get_data.py:  defines functions to fetch/parse DCC/PCAWG data

 donors_in_pcawg:  directory containing lists of PCAWG donors in each project (precomputed)
 pcawg_projects.txt:  text file listing PCAWG project details (code, project name, country)

### heatmap_rcode ###
Contains R code to generate heatmaps using output from previous script
Requires d3heatmap, RColorBrewer and shiny

#### To run ####

Pass in file name and title to generate_heatmap function. For example:
source("Heatmap_ClinicalCompleteness.R")
generate_heatmap("PCAWG_Donor_Completeness_ICGC20.tsv", "Donor Clinical Completeness for PCAWG donors in Release 20")
