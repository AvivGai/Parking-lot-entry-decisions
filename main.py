import requests
import json
from datetime import datetime
import sqlite3
import sys


def ocr_space_file(filename, overlay=False, api_key='1f5bb985eb88957', language='eng'):
    """ OCR.space API request with local file.
        Python3.5 - not tested on 2.7
    :param filename: Your file path & name.
    :param overlay: Is OCR.space overlay required in your response.
                    Defaults to False.
    :param api_key: OCR.space API key.
                    Defaults to 'helloworld'.
    :param language: Language code to be used in OCR.
                    List of available language codes can be found on https://ocr.space/OCRAPI
                    Defaults to 'en'.
    :return: Result in JSON format.
    """

    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               }
    with open(filename, 'rb') as f:
        r = requests.post('https://api.ocr.space/parse/image',
                          files={filename: f},
                          data=payload,
                          )
    return r.content.decode()


# create SQL table called "decisions" (if not already exists)
# with the following columns: number, decision,  reason, time
def create_table(cursor):
    cursor.execute('CREATE TABLE IF NOT EXISTS decisions (number INTEGER, decision TEXT, reason TEXT, time DATE PRIMARY KEY)')


# extracts the plate number from the result that returned from the API
def get_plate_number(file):
    file_dict = json.loads(file)
    ParsedText = (file_dict['ParsedResults'][0]["ParsedText"])
    number = ParsedText.split("\r\n")[0]
    onlyDigits = ""
    for char in number:
        if char.isalpha() or char.isdigit():
            onlyDigits += char
    return onlyDigits


def check_if_public(number):
    twoLastDigits = number[-2:]
    if twoLastDigits == "25" or twoLastDigits == "26":
        return True
    return False


def check_if_military(number):
    for char in number:
        if char.isalpha():
            return True
    return False


def check_if_prohibited_last_two(number):
    twoLastDigits = number[-2:]
    prohibitedLastTwo = ["85", "86", "87", "88", "89", "00"]
    if len(number) == 7 and (twoLastDigits in prohibitedLastTwo):
        return True
    return False


def check_if_gas(number):
    sum = 0
    if len(number) == 7 or len(number) == 8:
        for i in range(len(number)):
            sum += int(number[i])
        if sum % 7 == 0:
            return True
    return False


# insert an entry to the SQL table called "decisions"
# with the following data: plate number, decision,  reason (if decision is YES than this is blank), time
def insert_data(cursor, number, decision, reason, timestamp, connection):
    cursor.execute("INSERT INTO decisions (number, decision, reason, time) VALUES(?, ?, ?, ?)", (number, decision, reason, timestamp))
    connection.commit()


if __name__ == "__main__":
    connection = sqlite3.connect("parking_lot.db")
    cursor = connection.cursor()
    create_table(cursor)

    for i in range(1, len(sys.argv)):
        decision = "NO"
        reason = ""
        file = ocr_space_file(filename=sys.argv[i], language='eng')
        number = get_plate_number(file)
        if check_if_public(number):
            reason = "PUBLIC TRANSPORTATION"
        elif check_if_military(number):
            reason = "MILITARY AND LAW"
        elif check_if_prohibited_last_two(number):
            reason = "LAST DIGITS"
        elif check_if_gas(number):
            reason = "GAS"
        else:
            decision = "YES"
        timestamp = datetime.now()
        insert_data(cursor, number, decision, reason, timestamp, connection)

    cursor.close()
    connection.close()
