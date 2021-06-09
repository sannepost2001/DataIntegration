# DataIntegration

### Usage dataintegratieCode script:
This code is used to extract the data outof the .vcf and the .vcf.gz files. 
First it extracts the Chromosome 21, than it annotates that chromosome and lastly it extracts the first 10 missense and frame shift variants

To use the script u call it like this: <br>
First the location of the script and the location of the file. The script needs to be run in the file of the snpEFF. <br>
home/user/dataintegratieCode /home/user/1503AHX-0002_PGPC-0029-241086-M_SNP_INDEL.vcf <br>


### Direct_data:
Opens the file generated earlier, and sends the data to tables in the database.
Every line is seen as a new person.
The content of the list will be divided based on index in the list.
First the data regarding the preson, up to 7, is send to the person table, then the condition data is send in pairs of id and source value.

### fill_person:
Recieves data and formulates a postgre sql query to store the data in the table.

### conditions:
Checks the amount of conditions stored in the table and uses that number + 1 as primary key.
Formulates a query st store the given data in the table with the primary key.
