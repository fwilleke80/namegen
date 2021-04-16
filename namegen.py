#!/usr/bin/python
import os
import sys
import json
import time
import random
import argparse


# Script info
SCRIPTTITLE = 'German Name Generator'
SCRIPTVERSION = '1.7'
# SCRIPT_HELP = """
# Usage:
#   namegen.py [--count=n] [--gender=female|male|random] [--name=firstname|lastname] [--stats] [--help]
#   namegen.py [-c=n] [-g=female|male|random] [-s] [--help]

# Examples:
#   namegen.py
#       Generates a random name of random gender

#   namegen.py --gender=female --count=20
#       Generates 20 random female names

#   namegen.py --count=40 --name=lastname
#       Generates 40 lastnames

# count
#     Provide a number n > 0 here and that many names will be generated

# gender
#     Specify a gender here

# firstname
#     Add this argument to only generate a firstname, without lastname and nobility titles

# lastname
#     Add this argument to only generate a lastname and maybe nobility title, without firstname

# stats
#     Display statistics about the number of possible name combinations

# help
#     Displays this help, so you propably already know this one.
# """
# Data file name
DATAFILENAME = 'namegen_data.json'


# Class that does all the name generation work
class NameGenerator:
    # Thresholds
    threshExtraFirstnameSyllable = 0.32
    threshDoubleLastName = 0.18
    threshLongerLastName = 0.3
    threshNobility = 0.3

    # Limits / Ranges
    minLastnameSyllables = 2
    maxLastnameSyllables = 4

    # Syllable lists
    firstNameSyllables = {}
    lastNameSyllables = []
    nobilityPrefixes = {}

    def load_data(self, file):
        try:
            with open(file, 'r') as jsonFile:
                jsonData = json.load(jsonFile)
                self.firstNameSyllables = jsonData['firstNameSyllables']
                self.lastNameSyllables = jsonData['lastNameSyllables']
                self.nobilityPrefixes = jsonData['nobilityPrefixes']
        except:
            print("ERROR: Couldn't find data file: " + file)
            return False
        return True

    # Compute number of possible names
    def compute_stats(self):
        # Syllables
        numberOfMaleFirstnameSyllables1 = len(self.firstNameSyllables['male'][0])
        numberOfMaleFirstnameSyllables2 = len(self.firstNameSyllables['male'][1])
        numberOfMaleFirstnameSyllables3 = len(self.firstNameSyllables['male'][2])

        numberOfFemaleFirstnameSyllables1 = len(self.firstNameSyllables['female'][0])
        numberOfFemaleFirstnameSyllables2 = len(self.firstNameSyllables['female'][1])
        numberOfFemaleFirstnameSyllables3 = len(self.firstNameSyllables['female'][2])

        numberOfLastnameSyllables = len(self.lastNameSyllables)

        # Number of possible male firstnames
        numberOfMaleFirstnames_short = len(self.firstNameSyllables['male'][0]) * len(self.firstNameSyllables['male'][2])
        numberOfMaleFirstnames_long = len(self.firstNameSyllables['male'][0]) * len(self.firstNameSyllables['male'][1]) * len(self.firstNameSyllables['male'][2])
        numberOfMaleFirstnames = numberOfMaleFirstnames_short + numberOfMaleFirstnames_long

        # Number of possible female firstnames
        numberOfFemaleFirstnames_short = len(self.firstNameSyllables['female'][0]) * len(self.firstNameSyllables['female'][2])
        numberOfFemaleFirstnames_long = len(self.firstNameSyllables['female'][0]) * len(self.firstNameSyllables['female'][1]) * len(self.firstNameSyllables['female'][2])
        numberOfFemaleFirstnames = numberOfFemaleFirstnames_short + numberOfFemaleFirstnames_long

        numberOfFirstNames = numberOfFemaleFirstnames + numberOfMaleFirstnames

        # Number of nobility titles
        numberOfFemaleNobilityTitles = len(self.nobilityPrefixes['female'])
        numberOfMaleNobilityTitles = len(self.nobilityPrefixes['male'])
        numberOfNobilityTitles = numberOfFemaleNobilityTitles + numberOfMaleNobilityTitles

        # Number of possible lastnames
        numberOfLastNames_short = len(self.lastNameSyllables) ** 2 * (numberOfNobilityTitles + 1)
        numberOfLastNames_long = len(self.lastNameSyllables) ** 3 * (numberOfNobilityTitles + 1)
        numberOfLastnames = numberOfLastNames_short + numberOfLastNames_long

        # Total number of firstname/lastname combinations
        numberOfMaleNames = numberOfMaleFirstnames * numberOfLastnames * (numberOfMaleNobilityTitles + 1)
        numberOfFemaleNames = numberOfFemaleFirstnames * numberOfLastnames * (numberOfFemaleNobilityTitles + 1)
        numberOfNames = numberOfMaleNames + numberOfFemaleNames

        # Now build dictionary
        resultStats = {
            'syllables' : {
                'male1' : numberOfMaleFirstnameSyllables1,
                'male2' : numberOfMaleFirstnameSyllables2,
                'male3' : numberOfMaleFirstnameSyllables3,
                'female1' : numberOfFemaleFirstnameSyllables1,
                'female2' : numberOfFemaleFirstnameSyllables2,
                'female3' : numberOfFemaleFirstnameSyllables3,
                'lastname' : numberOfLastnameSyllables
            },
            'firstnames' : {
                'female' : {
                    'short' : numberOfFemaleFirstnames_short,
                    'long'  : numberOfFemaleFirstnames_long,
                    'total' : numberOfFemaleFirstnames
                },
                'male'   : {
                    'short' : numberOfMaleFirstnames_short,
                    'long'  : numberOfMaleFirstnames_long,
                    'total' : numberOfMaleFirstnames
                },
                'total'  : numberOfFirstNames
            },
            'lastnames' : {
                'short' : numberOfLastNames_short,
                'long'  : numberOfLastNames_long,
                'total' : numberOfLastnames
            },
            'nobility' : {
                'female' : numberOfFemaleNobilityTitles,
                'male'   : numberOfMaleNobilityTitles,
                'total'  : numberOfNobilityTitles
            },
            'female': numberOfFemaleNames,
            'male'  : numberOfMaleNames,
            'total' : numberOfNames
        }

        return resultStats


    # Print statistics from resultStats dictionary
    def print_statistics(self, stats):
        print('Database statistics')
        print('===================')
        print('')
        print('Syllables:')
        print('----------')
        print('Male firstname 1: ' + "{:8,}".format(stats['syllables']['male1']))
        print('Male firstname 2: ' + "{:8,}".format(stats['syllables']['male2']))
        print('Male firstname 3: ' + "{:8,}".format(stats['syllables']['male3']))
        print('')
        print('Female firstname 1: ' + "{:8,}".format(stats['syllables']['female1']))
        print('Female firstname 2: ' + "{:8,}".format(stats['syllables']['female2']))
        print('Female firstname 3: ' + "{:8,}".format(stats['syllables']['female3']))
        print('')
        print('Lastname: ' + "{:8,}".format(stats['syllables']['lastname']))
        print('')
        print('Firstnames:')
        print('-----------')
        print('Female short names   : ' + "{:8,}".format(stats['firstnames']['female']['short']))
        print('Female long names    : ' + "{:8,}".format(stats['firstnames']['female']['long']))
        print('Female names in total: ' + "{:8,}".format(stats['firstnames']['female']['total']))
        print('')
        print('Male short names     : ' + "{:8,}".format(stats['firstnames']['male']['short']))
        print('Male long names      : ' + "{:8,}".format(stats['firstnames']['male']['long']))
        print('Male names in total  : ' + "{:8,}".format(stats['firstnames']['male']['total']))
        print('')
        print('Firstnames in total  : ' + "{:8,}".format(stats['firstnames']['total']))
        print('')
        print('Lastnames:')
        print('----------')
        print('Short lastnames         : ' + "{:8,}".format(stats['lastnames']['short']))
        print('Long lastnames          : ' + "{:8,}".format(stats['lastnames']['long']))
        print('Lastnames in total      : ' + "{:8,}".format(stats['lastnames']['total']))
        print('')
        print('Nobility titles:')
        print('----------------')
        print('Female nobility titles  : ' + "{:8,}".format(stats['nobility']['female']))
        print('Male nobility titles    : ' + "{:8,}".format(stats['nobility']['male']))
        print('Nobility titles in total: ' + "{:8,}".format(stats['nobility']['total']))
        print('')
        print('Total:')
        print('------------')
        print('Female name combinations  : ' + "{:15,}".format(stats['female']))
        print('Male name combinations    : ' + "{:15,}".format(stats['male']))
        print('Name combinations in total: ' + "{:15,}".format(stats['total']))


    # Generate random firstname
    def generate_firstname(self, gender='male'):
        # Add first syllable
        newName = random.choice(self.firstNameSyllables[gender][0])

        # Add extra syllable
        if random.random() < self.threshExtraFirstnameSyllable:
            newName += random.choice(self.firstNameSyllables[gender][1])

        # Add last syllable
        newName += random.choice(self.firstNameSyllables[gender][2])

        # Return name with capitalized first letter
        return newName.title()


    # Generate random lastname
    def generate_lastname(self):
        # Determine lengh of lastname
        if random.random() < self.threshLongerLastName:
            numberOfSyllables = random.randrange(self.minLastnameSyllables, self.maxLastnameSyllables)
        else:
            numberOfSyllables = self.minLastnameSyllables

        lastSyllableIndex = -1
        newName = ''

        # Chain up syllables
        for _ in range(0, numberOfSyllables):
            newSyllableIndex = -1

            # Make sure the same syllable isn't used twice in a row
            while True:
                newSyllableIndex = random.randrange(0, len(self.lastNameSyllables) - 1)
                if newSyllableIndex != lastSyllableIndex:
                    break

            newName += self.lastNameSyllables[newSyllableIndex]
            lastSyllableIndex = newSyllableIndex

        # Return name with capitalized first letter
        return newName.title()


    # Get nobility title
    def get_nobility_prefix(self, gender='male'):
        return random.choice(self.nobilityPrefixes[gender])


    def safe_gender(self, theGender):
        # Support abbreviated genders
        if theGender == 'f':
            theGender = 'female'
        elif theGender == 'm':
            theGender = 'male'
        elif theGender == 'r':
            theGender = 'random'

        # Detect unsupported gender
        if theGender not in list(self.firstNameSyllables) and theGender != 'random':
            print('ERROR: Gender "' + theGender + '" not implemented yet. Sorry about that. Using random gender instead.')
            print('Supported genders: ' + str(list(self.firstNameSyllables)) + '.')
            print('')
            theGender = 'random'

        # If random gender desired, pick an available one
        if theGender == 'random':
            theGender = random.choice(list(self.firstNameSyllables))

        return theGender


    def generate(self, theGender, nameGenerateMode=0):
        # Detect unsupported gender
        theGender = self.safe_gender(theGender)

        # Full name
        if nameGenerateMode == 0:
            firstName = self.generate_firstname(theGender)
            lastName = self.generate_lastname()

            # Double lastname?
            if random.random() < self.threshDoubleLastName:
                lastName += '-' + self.generate_lastname()

            # Nobility?
            if random.random() < self.threshNobility:
                lastName = self.get_nobility_prefix(theGender) + ' ' + lastName

            return firstName + ' ' + lastName

        # Firstname only
        if nameGenerateMode == 1:
            return self.generate_firstname(theGender)

        # Lastname only
        if nameGenerateMode == 2:
            lastName = self.generate_lastname()

            # Double lastname?
            if random.random() < self.threshDoubleLastName:
                lastName += '-' + self.generate_lastname()

            # Nobility?
            if random.random() < self.threshNobility:
                lastName = self.get_nobility_prefix(theGender) + ' ' + lastName

            return lastName


# Return module name
def get_name():
    return SCRIPTTITLE + ' ' + SCRIPTVERSION


# Perform Encryption test
def run(args):
    # Welcome
    print(get_name() + "\n")

    # Create new NameGenerator object
    nameGen = NameGenerator()

    dataFile = os.path.join(os.path.dirname(os.path.realpath(__file__)), DATAFILENAME)
    if nameGen.load_data(dataFile) == False:
        sys.exit()

    # Seed random generator
    random.seed(time.time())

    # Parse args
    nameGenerateMode = 0

    if args["stats"]:
        nameGen.print_statistics(nameGen.compute_stats())
    else:
        nameGender = args["gender"]
        nameCount = args["count"]
        nameGenerateMode = 0 if args["firstlastname"] is None else (2 if args["firstlastname"].upper() == "LASTNAME" else 1)

        # Generate name(s)
        for i in range(nameCount):
            print(((('%s' % (i + 1)).rjust(2) + ". ") if nameCount > 1 else '') + nameGen.generate(nameGender, nameGenerateMode))
    print('')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--gender", dest="gender", type=str, default="random", metavar="GENDER", help="Desired gender: 'male', 'female, 'random'")
    parser.add_argument("-c", "--count", dest="count", type=int, default=1, metavar="COUNT", help="How many names do you want?")
    parser.add_argument("-n", "--name", dest="firstlastname", type=str, default=None, metavar="FIRSTLASTNAME", help="Want only first or last names? Type 'firstname' or 'lastname'")
    parser.add_argument("-s", "--stats", dest="stats", action="store_true", help="Display statistics")
    args = parser.parse_args()

    run(args.__dict__)


if __name__ == "__main__":
    main()