import string
import secrets
import json
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet
import base64

def GetOrCreateSalt():
    saltFilename = "secrets.salt"
    if not os.path.exists(saltFilename):
        salt = secrets.token_bytes(16)
        with open(saltFilename, "wb") as file:
            file.write(salt)
        return salt
    else:
        with open(saltFilename, "rb") as file:
            return file.read()

def DeriveKey(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000
    )

    cryptoKey = kdf.derive(password.encode())

    return base64.urlsafe_b64encode(cryptoKey)

def InitializeCipher() -> Fernet:
    print("\n-------------------------")
    print("----- LOGIN / START -----")
    print("-------------------------")

    masterPassword = input("Enter your Master Password: ")
    salt = GetOrCreateSalt()
    fernetKey = DeriveKey(masterPassword, salt)
    return Fernet(fernetKey)

# NEU: Diese Funktion prüft das Passwort ab, BEVOR irgendetwas anderes passiert
def VerifyOrCreateMasterPassword(cipherObj: Fernet):
    checkFilename = "master.check"
    
    # Fall A: Das Programm wird zum allerersten Mal gestartet
    if not os.path.exists(checkFilename):
        print("[INFO] No Master Password configuration found. Registering this password as your Master Password.")
        # Wir verschlüsseln ein festes Kontrollwort
        encryptedCheck = cipherObj.encrypt(b"APPROVED")
        with open(checkFilename, "wb") as file:
            file.write(encryptedCheck)
        return True
        
    # Fall B: Es existiert bereits ein Passwort, wir müssen es verifizieren
    with open(checkFilename, "rb") as file:
        encryptedContent = file.read()
        
    try:
        decryptedContent = cipherObj.decrypt(encryptedContent)
        if decryptedContent == b"APPROVED":
            print("\n[SUCCESS] Access Granted!")
            return True
    except Exception:
        print("\n[!] ACCESS DENIED: Wrong Master Password!")
        exit()

# Retrieves the user's password settings and returns them so that the user can customize their password
def GetUserPasswordSettings():
    
    lengthInput = input("\n[Recommended: at least 16 characters] Password Length: ")
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

# Creates and outputs the character pool based on the parameters 
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

# Generates the password randomly using the character pool
def GeneratePassword():

    print("\n----------------------------")
    print("---- GENERATE PASSWORD -----")
    print("----------------------------")

    settingApproved = False

    length = 16
    lower = upper = number = symbol = True

    while not settingApproved:
        
        length, lower, upper, number, symbol = GetUserPasswordSettings()

        print("\n---------------------------")
        print("---- Choosen Settings -----")
        print("---------------------------")
        print(f"\nLength: {length}")
        print(f"Lowercase: {'Yes' if lower else 'No'}")
        print(f"Uppercase: {'Yes' if upper else 'No'}")
        print(f"Numbers: {'Yes' if number else 'No'}")
        print(f"Symbols: {'Yes' if symbol else 'No'}")
        print("----------------------------")

        confirmSettingsInput = input("\nAre you happy with these settings? (y/n): ")

        settingApproved = confirmSettingsInput.lower() == "y"

    charPool = CreatePasswordCharacterPool(lower, upper, number, symbol)
    
    passwordApproved = False

    while not passwordApproved:
        password = ""
        for i in range(length):
            randomChar = secrets.choice(charPool)
            password = password + randomChar

        confirmPasswordInput = input(f"\nAre you happy with the password {password} ? (y/n): ")
        passwordApproved = confirmPasswordInput.lower() == "y"

    return password

# Overwrites the password.json file with the current data
def SavePasswords(entriesList, cipherObj: Fernet):

    jsonText = json.dumps(entriesList, indent=4)

    encryptedBytes = cipherObj.encrypt(jsonText.encode())
    with open("passwords.json", "wb") as file:
        file.write(encryptedBytes)

def LoadEntries(cipherObj: Fernet):

    if not os.path.exists("passwords.json"):
        return []
    
    with open("passwords.json", "rb") as file:
        encryptedContent = file.read()

    try:
        decryptedBytes = cipherObj.decrypt(encryptedContent)
        jsonText = decryptedBytes.decode()
        return json.loads(jsonText)
    except Exception:
        print("\n[!] FATAL: Corrupted password file data!")
        exit()

def CreateEntry(cipherObj: Fernet):

    print("\n-------------------------")
    print("----- GENERATE ENTRY ----")
    print("-------------------------")

    password = GeneratePassword()
    title = input("\nEnter Title for this password (e.g. Netflix): ")
    description = input("Enter Description: ")

    entry = {
        "title": title,
        "description": description,
        "password": password
    }

    return entry

def ShowExistingEntry(cipherObj: Fernet):

    print("\n-------------------------")
    print("------- SHOW ENTRY ------")
    print("-------------------------")

    entries = LoadEntries(cipherObj)

    if not entries:
        print("No entries found.")
        return True

    for index, entry in enumerate(entries, start=1):
        print(f"\n------ ENTRY [{index}] -----------")
        print(f"Title: {entry['title']}")
        print(f"Description: {entry['description']}")
        print(f"Password: {entry['password']}")
        print("-------------------------")

    return True

def EditExistingEntry(cipherObj: Fernet):

    if not ShowExistingEntry(cipherObj):
        return
    
    entries = LoadEntries(cipherObj)
    if not entries:
        return

    try:
        toEditEntry = input("\nwhich entry (Enter a number): ").strip()
        choiceIndex = int(toEditEntry) - 1

        if choiceIndex < 0 or choiceIndex >= len(entries):
            print("\n[!] invalid Number")
            return
    
    except ValueError:
        print("\n[!] Please enter a valid number")
        return
    
    editOrDelete = input("wanna edit [1] or delete [2]: ")
    match editOrDelete:
        case "1":
            selectedEntry = entries[choiceIndex]
            print(f"\nyou are currently editing: {selectedEntry['title']}")
            print("\nLeave the fields blank (press Enter) if you don't want to change them")

            newTitle = input(f"New Title: ").strip()
            if newTitle:
                selectedEntry['title'] = newTitle

            newDescription = input(f"New Description: ").strip()
            if newDescription:
                selectedEntry['description'] = newDescription

            newPassword = input(f"New Password (y/n): ").strip().lower()
            if newPassword == "y":
                password = GeneratePassword()
                selectedEntry['password'] = password

            SavePasswords(entries, cipherObj)
        
        case "2":
            deleteEntry = entries.pop(choiceIndex)
            SavePasswords(entries, cipherObj)
        case _:
            print("\n [!] Invalid selection. Please choose [1] for editing | [2] for deleting an Entry")

    print("\n[SUCCESS] Entry succesfully updated")

def HandleMenu():

    cipher = InitializeCipher()

    # KORREKTUR: Hier wird der Riegel vorgeschoben. 
    # Wenn die Verifizierung fehlschlägt, bricht das Programm sofort ab.
    VerifyOrCreateMasterPassword(cipher)

    while True:
        print("\n1. Create Password")
        print("2. Read the existing Passwords")
        print("3. Edit an existing Passwords")
        print("4. End Program")

        inputChoose = input(f"Choose (1-4): ").strip()

        match inputChoose:
            case "1":
                newEntry = CreateEntry(cipher)
                currentList = LoadEntries(cipher)
                currentList.append(newEntry)
                SavePasswords(currentList, cipher)
                print("\n[SUCCESS] Password successfully saved in 'passwords.json'")
            case "2":
                ShowExistingEntry(cipher)
                print("\n[SUCCESS] Passwords were successfully retrieved")
            case "3":
                EditExistingEntry(cipher)
            case "4":
                print("\n[SUCCESS] PROGRAM EXIT")
                break
            case _:
                print("\n [!] Invalid selection. Please choose one of the numbers listed")
