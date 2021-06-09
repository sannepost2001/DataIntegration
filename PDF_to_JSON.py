# Author: Harm Laurense
# Last changed: 08-06-2021
# Usage: This script reads all pdf files in the given directory and extracts
# specific content which is written to a new json file. This script is made
# for pdf files of participants ending on the number '9'.
# Data collected from: https://personalgenomes.ca/data
# Notes & Future improvements: Generalize script for all participants and
# change file reading from hard coded to something flexible.


from tika import parser
import json
import glob
import itertools


def main():
    final_json_file = extract_information()
    json_dump(final_json_file)


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


main()
