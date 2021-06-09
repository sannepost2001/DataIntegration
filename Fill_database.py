import psycopg2


connection = psycopg2.connect(host="145.74.104.145", dbname="postgres",
                              user="j3_g9", password="Blaat1234")


def fill_person(person_id, gender_concept_id, year_of_birth, month_of_birth, race_concept_id,gender_source_value,
                 race_source_value):
    """ fills the person table in the database
    :param person_id: the person id in the pdf file as a string
    :param gender_concept_id: the id corresponding with the gender from the pdf file as a string
    :param year_of_birth: the year the person was born as a string
    :param month_of_birth: a string containing the month the person from the pdsf was born
    :param race_concept_id: an int containing the id corresponding to the race given in the pdf
    :param gender_source_value: a string containing the gender as described in the pdf
    :param race_source_value: a string containing the race as described in the pdf
    :return: none
    """
    cursor = connection.cursor()

    # check if person exists
    stored_conditions = "select count(*) from person where person_id={};".format(person_id)
    cursor.execute(stored_conditions)
    person_count = cursor.fetchall()
    cursor.close()
    if person_count[0][0] >0:
        return
    birth_datetime = year_of_birth + "-" + month_of_birth + '-01'

    cursor = connection.cursor()
    insert_data = """insert into person(person_id,gender_concept_id,  year_of_birth, month_of_birth, day_of_birth, birth_datetime, race_concept_id, ethnicity_concept_id, location_id, provider_id, care_site_id, person_source_value, gender_source_value, gender_source_concept_id, race_source_value, race_source_concept_id, ethnicity_source_value, ethnicity_source_concept_id)
                                VALUES({}       ,{}                ,'{}'           ,'{}'           ,  '01'        ,'{}'            , {}             , 1                   , 1          , 1          , 1           ,1                   ,'{}'               , 1                      ,'{}'              , 1                     , 1                     ,1)
                            """.format(person_id ,gender_concept_id, year_of_birth , month_of_birth,  birth_datetime,               race_concept_id,                                                                                     gender_source_value                        , race_source_value)
    print(insert_data)

    cursor.execute(insert_data)
    connection.commit()
    cursor.close



def conditions(person_id, condition, condition_id):
    """ fills the conditions table in the database
    :param person_id: the person id from the pdf in string format
    :param condition: the condition as mentioned in the pdf as string
    :param condition_id: the condition id corresponding with the described condition as int
    :return: none
    """
    cursor = connection.cursor()

    # get count for new id
    stored_conditions = "select count(*) from condition_occurrence;"
    cursor.execute(stored_conditions)
    condition_count = cursor.fetchall()
    cursor.close()
    condition_occurance_id = condition_count[0][0] + 1
    cursor = connection.cursor()
    data = "{},{},0,'04-24-2021','04-24-2021','04-24-2021','04-24-2021',1,1,1,1,1,{},1,1,1".format(
        condition_occurance_id, person_id, condition)

    insert_data = """insert into condition_occurrence(condition_occurrence_id, person_id, condition_concept_id, condition_start_date,
            condition_start_datetime, condition_end_date, condition_end_datetime, condition_type_concept_id, stop_reason,
            provider_id, visit_occurrence_id, visit_detail_id, condition_source_value, condition_source_concept_id,
            condition_status_source_value, condition_status_concept_id)
            values ({},{},0,'06-24-2021','04-24-2021','04-24-2021','04-24-2021',1,1,1,1,1,'{}',{},1,1)""".format(
        condition_occurance_id, person_id, condition, condition_id)
    print(insert_data)
    cursor.execute(insert_data)
    connection.commit()
    cursor.close
    print(condition_count)
    print("yeet")


def direct_data(file):
    """extracts data from file and directs content to to the functions tht fill tables in the database
    :param file: the file
    :return: none
    """
    for line in file:
        line = line.strip("\n")
        line = line.replace('[', '').replace(']', '')
        line = line.replace("'", "")
        line = line.split(",")
        person_id = line[0].split("-")
        person_id = person_id[1]
        year_of_birth = line[1]
        month_of_birth = line[2].strip()
        gender_concept_id = line[3]
        gender_source_value = line[4]
        race_concept_id = line[5]
        race_source_value = line[6]
        fill_person(person_id=person_id,
                    gender_concept_id=gender_concept_id,
                    year_of_birth=year_of_birth,
                    month_of_birth=month_of_birth,
                    race_concept_id=race_concept_id,
                    gender_source_value=gender_source_value,
                    race_source_value=race_source_value)
        for i in range(7,len(line),2):
            print(line)
            #print(line.count(''))
            if line[i].count(' not_found') == 0:
                print("yeet")
                condition_id = line[i]
                print('condition_id',condition_id)
                condition = line[i + 1]
                print('condition',condition)
                conditions(person_id=person_id,condition_id=condition_id, condition=condition)

def main():
    file = open("SemanticMapping_Results.txt", "r")

    direct_data(file=file)




main()
