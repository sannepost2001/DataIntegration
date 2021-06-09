# Author: Harm Laurense
# Last changed: 08-06-2021
# Usage: This script is used to retrieve the concept ids for corresponding
# participant data. This script should be run after the PDF-data.json is
# obtained by running PDF_to_JSON.py. This script requires the CONCEPT.csv
# and CONCEPT_SYNONYM.csv to be downloaded from Athena beforehand.
# Notes & Future improvements: The "suggestion_list" function is still a work
# in progress and is therefore turned off. For downloading the vocabularies an
# account was made at https://athena.ohdsi.org/. Only the "CONCEPT.csv" and
# "CONCEPT_SYNONYM.csv" was used (these are actually .tsv files).


import json


def main():
    participant_info, birth_info = read_json()
    catagorized_participant_data = catagorize_data(participant_info)
    vocubalary = retrieve_vocabulary()
    results, missing_results = compare_to_vocabulary(vocubalary, catagorized_participant_data, birth_info)
    write_results_to_txtfile(results)
    # suggestion_list(missing_results, vocubalary)


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


main()
