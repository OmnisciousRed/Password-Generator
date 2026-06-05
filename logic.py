import string
import secrets
import json

def GetUserPasswordSettings():
    
    lengthInput = input("[Recommended: at least 16 characters] Password Length: ")
    length: int = int(lengthInput)

    lowerLetterInput = input("Lower Letter (y/n): ")
    lowerLetter: bool = lowerLetterInput.lower() == "y"

    upperLetterInput = input("upper Letter (y/n): ")
    upperLetter: bool = upperLetterInput.lower() == "y"

    numberInput = input("Number (y/n): ")
    number: bool = numberInput.lower() == "y"

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

    print("----------------------------")
    print("-----GENERATE PASSWORD------")
    print("----------------------------")

    settingApproved = False

    length = 16
    lower = upper = number = symbol = True

    while not settingApproved:
        
        length, lower, upper, number, symbol = GetUserPasswordSettings()

        print("\n--- Your Chosen Settings ---")
        print(f"Length: {length}")
        print(f"Lowercase: {'Yes' if lower else 'No'}")
        print(f"Uppercase: {'Yes' if upper else 'No'}")
        print(f"Numbers: {'Yes' if number else 'No'}")
        print(f"Symbols: {'Yes' if symbol else 'No'}")
        print("----------------------------")

        confirmInput = input("Are you happy with these settings? (y/n): ")

        settingApproved = confirmInput.lower() == "y"

    charPool = CreatePasswordCharacterPool(lower, upper, number, symbol)
    
    password = ""
    for i in range(length):
        randomChar = secrets.choice(charPool)
        password = password + randomChar

    return password

def SaveEntry():

    with open("dateiname.txt", "w") as file:
        file.write("Hier steht dein Text")

def LoadEntries():
    return

def CreateEntry():

    password = GeneratePassword()
    title = input("Enter Title for this password (e.g. Netflix): ")
    description = input("Enter Description: ")

    entry = {
        "title": title,
        "description": description,
        "password": password
    }

    return entry
