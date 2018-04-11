import csv
import json

# CONSTANTS ####################################################################

URL = 'https://www.premierleague.com/transfers/january/2018'
JSON_PATH = 'jsondump/list_of_transfers.json'


# FUNCTIONS ####################################################################


def main():

    csvfile = open('jsondump/transfers-summer.csv', 'r')
    jsonfile = open('jsondump/transfers-summer.json', 'w')

    fieldnames = ("team1", "direction", "date", "role", "name", "team2", "details")
    reader = csv.DictReader(csvfile, fieldnames)
    jsonfile.write('{ "transfers": [\n')
    for row in reader:
        json.dump(row, jsonfile, ensure_ascii=False, indent=4)
        jsonfile.write(',\n')
    jsonfile.write(']}\n')

    csvfile = open('jsondump/transfers-winter.csv', 'r')
    jsonfile = open('jsondump/transfers-winter.json', 'w')

    fieldnames = ("team1", "direction", "date", "role", "name", "team2", "details")
    reader = csv.DictReader(csvfile, fieldnames)
    jsonfile.write('{ "transfers": [\n')
    for row in reader:
        json.dump(row, jsonfile, ensure_ascii=False, indent=4)
        jsonfile.write(',\n')
    jsonfile.write(']}\n')



if __name__ == "__main__":
    main()
