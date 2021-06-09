# DataIntegration

### Usage dataintegratieCode script:
This code is used to extract the data outof the .vcf and the .vcf.gz files. 
First it extracts the Chromosome 21, than it annotates that chromosome and lastly it extracts the first 10 missense and frame shift variants

To use the script u call it like this: <br>
First the location of the script and the location of the file. The script needs to be run in the file of the snpEFF. <br>
home/user/dataintegratieCode /home/user/1503AHX-0002_PGPC-0029-241086-M_SNP_INDEL.vcf <br>

### Semantic mapping pipeline: Pipeline.py
This pipeline is used for extracting information from participant data, retrieving corresponding concept ids and placing them into the database. <br>
A few files and changes to workdirectory aren needed to run this script. Most files are found in the metadata folder.
- Data collected from: https://personalgenomes.ca/data
- Vocabulary files collected from Athena: https://athena.ohdsi.org/ <br>
*Only the "CONCEPT.csv" and "CONCEPT_SYNONYM.csv" was used 

Temporary link for the concept files: https://we.tl/t-OM4nuxZRwD

### Manual check
This script can be manually checked between steps by running the individual components. (PDF_to_JSON.py; Semantic_Mapping_PDFData.py; Fill_database.py) <br>
These scripts will give separate output files (PDF-data.json & SemanticMapping_Results.txt). 
