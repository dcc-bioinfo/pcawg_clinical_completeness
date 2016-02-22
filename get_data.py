#!/usr/bin/python
import os
import re
import gzip
import bz2


# regex to check if project is a TCGA project (the donor_ids in TCGA projects need to be handled differently)
tcga=re.compile("\w+\-US$")

# Get file(s) from DCC submission directory
def getFile(filePattern, inputDir):
   dataFile = ''
   listFiles = []
   #for file in os.listdir('.'):
   for file in os.listdir(inputDir):
      if re.match(filePattern, file):
         bz2_filePattern = ".*bz2$"
         gzip_filePattern = ".*gz$"
         if (re.match(bz2_filePattern, file)):
	   dataFile = bz2.BZ2File("%s/%s"%(inputDir,file), 'rb')
         elif (re.match(gzip_filePattern, file)):
           dataFile = gzip.open("%s/%s"%(inputDir,file), 'rb')
         else:
           dataFile = open("%s/%s"%(inputDir,file), 'r')
         listFiles.append(dataFile)
   return listFiles


# Parse PCAWG donors from pre-computed project-specific lists
def parse_pcawg_donors(project):
   pcawg_donor_file = open("donors_in_pcawg/%s_PCAWG_donors.txt"%project, 'r')
   #print "pcawg_donor_file = %s"%pcawg_donor_file.name
   pcawg_donors = {}
   pcawg_content = pcawg_donor_file.readlines()
   for line in pcawg_content:
      line = line.rstrip('\n')
      pcawg_donor = line.split("::")[1]
      if tcga.match(project):
         pcawg_donor = pcawg_donor.lower()
      pcawg_donors[pcawg_donor] = project
   return pcawg_donors

