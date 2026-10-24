import json
import os
import secrets
import base64
import getpass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

VAULT_FILE = Path(__file__).with_name("vault.json")
ITERATIONS = 600_000


def derive_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return base64.urlsafe_b64encode(
        kdf.derive(master_password.encode("utf-8"))
    )


def save_vault(credentials, cipher, salt):
    encrypted_data = cipher.encrypt(
        json.dumps(credentials).encode("utf-8")
    )

    data = {
        "version": 1,
        "salt": base64.b64encode(salt).decode("ascii"),
        "data": encrypted_data.decode("ascii"),
    }

    temp_file = VAULT_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(temp_file, VAULT_FILE)


def load_vault(master_password):
    if not VAULT_FILE.exists():
        salt = secrets.token_bytes(16)
        cipher = Fernet(derive_key(master_password, salt))
        save_vault([], cipher, salt)
        return [], cipher, salt

    try:
        data = json.loads(VAULT_FILE.read_text(encoding="utf-8"))

        if data.get("version") != 1:
            raise ValueError("Unsupported vault version.")

        salt = base64.b64decode(data["salt"], validate=True)
        cipher = Fernet(derive_key(master_password, salt))

        credentials = json.loads(
            cipher.decrypt(data["data"].encode("ascii")).decode("utf-8")
        )

        if not isinstance(credentials, list):
            raise ValueError("Invalid vault data.")

        for credential in credentials:
            if not all(
                key in credential
                for key in ("website", "username", "password")
            ):
                raise ValueError("Invalid credential entry.")

        return credentials, cipher, salt

    except InvalidToken:
        raise ValueError("Incorrect master password or damaged vault.")
    except (KeyError, json.JSONDecodeError, UnicodeDecodeError) as error:
        raise ValueError("Vault file is damaged or invalid.") from error


def get_nonempty_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def find_credentials(credentials, website):
    return [
        index
        for index, credential in enumerate(credentials)
        if credential["website"].casefold() == website.casefold()
    ]


def store_credentials(credentials):
    website = get_nonempty_input("Enter website URL: ")
    username = get_nonempty_input("Enter username: ")
    password = getpass.getpass("Enter password: ")

    if not password:
        print("Password cannot be empty.")
        return False

    credentials.append({
        "website": website,
        "username": username,
        "password": password,
    })

    print("Credential added successfully.")
    return True


def retrieve_credentials(credentials):
    website = get_nonempty_input("Enter website URL to retrieve: ")
    matches = find_credentials(credentials, website)

    if not matches:
        print("No credentials found for this website.")
        return

    for index in matches:
        credential = credentials[index]
        print(f"\nWebsite: {credential['website']}")
        print(f"Username: {credential['username']}")
        print(f"Password: {credential['password']}")


def see_credentials(credentials):
    if not credentials:
        print("No credentials stored.")
        return

    print("\nStored credentials:")
    for index, credential in enumerate(credentials, start=1):
        print(
            f"{index}. Website: {credential['website']} | "
            f"Username: {credential['username']}"
        )


def remove_credentials(credentials):
    website = get_nonempty_input("Enter website URL to remove: ")
    matches = find_credentials(credentials, website)

    if not matches:
        print("No credentials found for this website.")
        return False

    for index in reversed(matches):
        removed = credentials.pop(index)
        print(f"Removed account: {removed['username']}")

    return True


def update_credentials(credentials):
    website = get_nonempty_input("Enter website URL to update: ")
    matches = find_credentials(credentials, website)

    if not matches:
        print("No credentials found for this website.")
        return False

    if len(matches) > 1:
        print("Multiple accounts found:")
        for number, index in enumerate(matches, start=1):
            print(f"{number}. {credentials[index]['username']}")

        try:
            choice = int(input("Choose account number: "))
            if not 1 <= choice <= len(matches):
                print("Invalid account number.")
                return False
        except ValueError:
            print("Please enter a valid number.")
            return False

        index = matches[choice - 1]
    else:
        index = matches[0]

    new_username = input("New username (Enter to keep current): ").strip()
    new_password = getpass.getpass(
        "New password (Enter to keep current): "
    )

    if new_username:
        credentials[index]["username"] = new_username

    if new_password:
        credentials[index]["password"] = new_password

    print("Credentials updated successfully.")
    return True


def main():
    print("=== Password Manager ===")

    if VAULT_FILE.exists():
        master_password = getpass.getpass("Enter master password: ")
        if not master_password:
            print("Master password cannot be empty.")
            return
    else:
        print("Create a strong master password for your vault.")
        master_password = getpass.getpass("Create master password: ")
        confirmation = getpass.getpass("Confirm master password: ")

        if not master_password or master_password != confirmation:
            print("Passwords are empty or do not match.")
            return

    try:
        credentials, cipher, salt = load_vault(master_password)
    except (ValueError, OSError) as error:
        print(f"Could not open vault: {error}")
        return

    print("Vault unlocked.")

    while True:
        print("\n1. Store credentials")
        print("2. Retrieve credentials")
        print("3. See stored accounts")
        print("4. Remove credentials")
        print("5. Update credentials")
        print("6. Exit")

        choice = input("Enter your choice: ").strip()
        changed = False

        try:
            if choice == "1":
                changed = store_credentials(credentials)
            elif choice == "2":
                retrieve_credentials(credentials)
            elif choice == "3":
                see_credentials(credentials)
            elif choice == "4":
                changed = remove_credentials(credentials)
            elif choice == "5":
                changed = update_credentials(credentials)
            elif choice == "6":
                print("Vault locked. Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-6.")

            if changed:
                save_vault(credentials, cipher, salt)
                print("Encrypted vault saved.")

        except OSError as error:
            print(f"File operation failed: {error}")


if __name__ == "__main__":
    main()
