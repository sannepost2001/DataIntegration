# Author: Harm Laurense, Johannes Schönthaler & Sanne Post
# Last changed: 08-06-2021
# Pipeline: Extracts information from participant PDF files, searches for
# corresponding concept IDs and adds it to the database.
# Notes: This script assumes the correct directories are given and all
# files necessary are provided.


from tika import parser
import json
import glob
import itertools
import psycopg2


connection = psycopg2.connect(host="145.74.104.145", dbname="postgres",
                              user="j3_g9", password="Blaat1234")


def main():
    final_json_file = extract_information()
    json_dump(final_json_file)
    participant_info, birth_info = read_json()
    catagorized_participant_data = catagorize_data(participant_info)
    vocubalary = retrieve_vocabulary()
    results, missing_results = compare_to_vocabulary(vocubalary,
                                                     catagorized_participant_data,
                                                     birth_info)
    write_results_to_txtfile(results)
    # suggestion_list(missing_results, vocubalary)
    direct_data()


def extract_information():
    """
    A list is made containing all .pdf files in the given directory.
    Information is extracted and added to json_file for every PDF file.
    :return: json file containing the participant data.
    """
    mydir = "C:/Users/Harm/PycharmProjects/Course10/Data_integratie/"
    file_list = glob.glob(mydir + "/*.pdf")
    json_file = {"Participants": {}}
    for file_name in file_list:
        json_file = file_reader(fname=file_name, json_file=json_file)
    return json_file


def file_reader(fname, json_file):
    """
    Information is extracted from a PDF file and added to a JSON file.
    :param fname: Name of current PDF file (current participant)
    :param json_file: json file containing all participant data
    :return: json file containing all participant data
    (the file keeps getting updated in every extraction)
    """
    parsed_pdf = parser.from_file(fname)
    actual_data = []
    data = parsed_pdf['content']
    temp_ls = data.split("\n")
    for item in temp_ls:
        if item != "":
            if item == "Immunizations":
                break
            actual_data.append(item)
    profile_feature = actual_data[2].split(" ")
    conditions_and_symptoms = []
    for condition in actual_data[5:]:
        # In case condition contains '9' append everything after it
        conditions_and_symptoms.append(condition.split("9")[1:])
    # combine into 1 list of items
    flat_conditions_and_symptoms = list(
        itertools.chain(*conditions_and_symptoms))
    json_file['Participants'][profile_feature[0]] = {
        "Profile": {
            "Birth_year": profile_feature[2],
            "Birth_month": profile_feature[1],
            "Sex": profile_feature[3],
            "Ethnicity": profile_feature[4]
        },
        "Conditions_or_symptoms": flat_conditions_and_symptoms
    }

    return json_file


def json_dump(final_json_file):
    """
    After every participant PDF file has been extracted, a final json
    file is made.
    :param final_json_file: Json file containing all participant data
    """
    print("Writing extracted data to json...")
    with open("PDF-data.json", "w+") as new_json:
        json.dump(final_json_file, new_json)
        print('Done, PDF-data.json ready for use')


def read_json():
    """
    Reads a json file (output of PDF_to_JSON.py) and extracts the data
    to two different lists.
    :return: 2 lists with participant data
    """

    participant_info = []
    temp_list = []
    birth_month_year = []

    try:
        with open(f'PDF-data.json', 'r') as file:
            file_info = json.load(file)

        for participants in file_info.values():
            for participant in participants:
                participant_info.append([participant])

        participant_count = -1
        for participants in file_info.values():
            for participant in participants.values():
                participant_count += 1
                for info in participant['Profile'].values():
                    temp_list.append(info)
                for info2 in participant['Conditions_or_symptoms']:
                    temp_list.append(info2)
                participant_info[participant_count].append(temp_list[2:])
                birth_month_year.append(temp_list[:2])
                temp_list = []

    except FileNotFoundError:
        print("Check if the correct files are present")

    return participant_info, birth_month_year


def catagorize_data(participant_info):
    """
    Catagorize the participant information into different smaller lists.
    :param participant_info: Output (list) from read_json()
    :return: A list containing 4 lists which contain the pdf data
    separated into: participant id, gender, race and conditions/symptoms
    """

    participants = []
    gender = []
    race = []
    condition = []

    for participant in participant_info:
        temp_list = []
        participants.append(participant[0])
        gender.append(participant[1][0])
        race.append(participant[1][1])
        for conditions in participant[1][2:]:
            temp_list.append(conditions.strip())
        condition.append(temp_list)
    catagorized_participant_data = [participants, gender, race, condition]

    return catagorized_participant_data


def retrieve_vocabulary():
    """
    The CONCEPT.csv file is read and specific data is extracted to 3
    different lists.
    :return: A list containing 3 lists with data regarding
    gender/race/conditions
    """

    vocabulary_gender = []
    vocabulary_race = []
    vocabulary_condition = []

    try:
        # 5616862 lines in CONCEPT.csv
        with open(f'CONCEPT.csv', 'r', encoding='utf8') as file:
            for line in file:
                line = line.rstrip().split("\t")
                if line[2] == "Gender":
                    vocabulary_gender.append(line)
                elif line[2] == "Race":
                    vocabulary_race.append(line)
                elif line[2] == "Condition":
                    vocabulary_condition.append(line)
    except FileNotFoundError:
        print("Check if the correct files are present")
    vocabulary = [vocabulary_gender, vocabulary_race, vocabulary_condition]

    return vocabulary


def compare_to_vocabulary(vocabulary, catagorized_participant_data,
                          birth_info):
    """
    Every catagory of participant data (gender/race/condition) is searched
    through using the previously made lists. Only standardized data is
    accepted. On a match the concept_id is extracted to a new list (
    standardized_data). If no match is found, a second search is done through the CONCEPT_SYNONYM.csv
    file. If still no match is found then the id is filled by a placeholder
    and added to a separate list (missing_items).
    :param vocabulary: List containing 3 lists with extracted data
    (race/gender/condition)
    :param catagorized_participant_data: List containing 4 lists with
    participant data, catagorized into participant_id/race/gender/conditions
    :param birth_info: List containing participants birth month/year
    :return: 2 lists: one for standardized data (data+concept_id) and
    another one for the missing data.
    """

    standarized_data = []
    missing_items = []
    print("Start comparing vocabularies")

    for i in range(len(catagorized_participant_data[0])):
        standarized_data.append([catagorized_participant_data[0][i]])
        standarized_data[i].append(birth_info[i])
        gender_concept_found = False
        race_concept_found = False

        gender = catagorized_participant_data[1][i]
        for gender_info in vocabulary[0]:
            if gender.lower() == gender_info[1].lower() and gender_info[5] \
                    == "S" or gender.lower() == gender_info[6].lower() and \
                    gender_info[5] == "S":
                standarized_data[i].append(gender_info[0])
                standarized_data[i].append(gender)
                gender_concept_found = True
        if not gender_concept_found:
            concept_id = compare_to_synonyms(gender)
            standarized_data[i].append(concept_id)
            standarized_data[i].append(gender)
            if concept_id == "not_found":
                missing_items.append(gender)

        race = catagorized_participant_data[2][i]
        for race_info in vocabulary[1]:
            if race.lower() == race_info[1].lower() and race_info[5] == "S":
                standarized_data[i].append(race_info[0])
                standarized_data[i].append(race)
                race_concept_found = True
        if not race_concept_found:
            concept_id = compare_to_synonyms(race)
            standarized_data[i].append(concept_id)
            standarized_data[i].append(race)
            if concept_id == "not_found":
                missing_items.append(race)

        for condition in catagorized_participant_data[3][i]:
            condition_concept_found = False
            for condition_info in vocabulary[2]:
                if condition.lower() == condition_info[1].lower() \
                        and condition_info[5] == "S":
                    standarized_data[i].append(condition_info[0])
                    standarized_data[i].append(condition)
                    condition_concept_found = True
            if not condition_concept_found:
                concept_id = compare_to_synonyms(condition)
                standarized_data[i].append(concept_id)
                standarized_data[i].append(condition)
                if concept_id == "not_found":
                    missing_items.append(["condition", condition])
    print("Done comparing vocabularies")
    return standarized_data, missing_items


def compare_to_synonyms(missing_item):
    """
    Searches for a match in CONCEPT_SYNONYM.csv when no match was found
    in compare_to_vocabulary(). If a match is found then the concept_id
    is extracted and returned, otherwise a placeholder is send.
    :param missing_item: Participant data
    :return: Concept id
    """
    concept_id = "not_found"
    try:
        with open(f'CONCEPT_SYNONYM.csv', 'r', encoding='utf8') as file:
            for line in file:
                line = line.rstrip().split("\t")
                if line[1].lower() == missing_item.lower():
                    concept_id = line[0]

    except FileNotFoundError:
        print("Check if the correct files are present")

    return concept_id


def write_results_to_txtfile(results):
    """
    Standardized data is written to a new text file.
    :param results: List containing all participant data+concept_ids
    """
    print("Writing results to text file...")
    with open("SemanticMapping_Results.txt", "w") as results_file:
        for participant in results:
            results_file.write(str(participant) + "\n")
    print("Done, SemanticMapping_Results.txt is ready for use")


def suggestion_list(missing_results, vocabulary):
    # This function is still incomplete
    suggestions = []
    for item in missing_results:
        if item[0] == "condition":
            for condition_info in vocabulary[2]:
                if item[1].lower() in condition_info[1].lower() and \
                        condition_info[5] == "S":
                    suggestions.append(condition_info)



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
    insert_data = """insert into condition_occurrence(condition_occurrence_id, person_id, condition_concept_id, condition_start_date,
            condition_start_datetime, condition_end_date, condition_end_datetime, condition_type_concept_id, stop_reason,
            provider_id, visit_occurrence_id, visit_detail_id, condition_source_value, condition_source_concept_id,
            condition_status_source_value, condition_status_concept_id)
            values ({},{},0,'06-24-2021','04-24-2021','04-24-2021','04-24-2021',1,1,1,1,1,'{}',{},1,1)""".format(
        condition_occurance_id, person_id, condition, condition_id)
    cursor.execute(insert_data)
    connection.commit()
    cursor.close


def direct_data():
    """extracts data from file and directs content to to the functions tht fill tables in the database
    :return: none
    """
    try:
        file = open("SemanticMapping_Results.txt", "r")
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
                if line[i].count(' not_found') == 0:
                    condition_id = line[i]
                    condition = line[i + 1]
                    conditions(person_id=person_id,condition_id=condition_id, condition=condition)
        file.close()
    except FileNotFoundError:
        print("Check if the correct files are present")


main()

