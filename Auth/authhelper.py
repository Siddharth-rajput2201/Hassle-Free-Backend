import re

def checkForDigit(inputString):
    return any(char.isdigit() for char in inputString)

def checkForUpper(inputString):
    return any(char.isupper() for char in inputString)

def checkForLower(inputString):
    return any(char.islower() for char in inputString)

def checkForSpecialChar(inputString):

    regex = re.compile('[@_!#$%^&*()<>?/\|}{~:]')
    if(regex.search(inputString) == None):
        return False
         
    else:
        return True

