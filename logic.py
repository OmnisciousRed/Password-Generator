import string
import secrets

def GetUserPasswordSettings():
    
    lengthInput = input("Password Length: ")
    length: int = int(lengthInput)

    lowerLetterInput = input("Lower Letter (y/n): ")
    lowerLetter: bool = lowerLetterInput.lower() == "y"

    upperLetterInput = input("upper Letter (y/n): ")
    upperLetter: bool = upperLetterInput.lower() == "y"

    numberInput = input("Number (y/n): ")
    number: bool = upperLetterInput.lower() == "y"

    symbolInput = input("Symbol (y/n): ")
    symbol: bool = symbolInput.lower() == "y"

    return length, lowerLetter, upperLetter, number, symbol

def CreatePasswordCharacterPool(useLower: bool, useUpper: bool, useNumber: bool, useSymbol: bool):
    
    pool = ""

    if useLower:
        pool = pool + string.ascii_lowercase

    if useUpper:
        pool = pool + string.ascii_uppercase

    if useNumber:
        pool = pool + string.digits

    if useSymbol:
        pool = pool + string.punctuation
    
    return pool

def GeneratePassword():
    password = ""
    length, lower, upper, number, symbol = GetUserPasswordSettings()
    charPool = CreatePasswordCharacterPool(lower, upper, number, symbol)
    
    for i in range(length):
        randomChar = secrets.choice(charPool)
        password = password + randomChar

    return password

