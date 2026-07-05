# This is a simple script to collect user credentials for a website.
while True:
    credential = []

    print("Welcome to the Password Manager Script!")
    print("if you want to store your credentials Type 'store'")
    print("if you want to retrieve your credentials Type 'retrieve'")
    print("if you want to see all your credentials Type 'see'")
    print("if you want to delete your credentials Type 'remove'")
    print("if you want to update your credentials Type 'update'")
    print("if you want to exit the program Type 'exit'")
    
    manager = input("Enter your choice: ")

    if manager.lower() == "store":
        
        number_of_credentials = int(input("How many credentials do you want to store? "))
        for i in range(number_of_credentials):
            print(f"Storing credential {i + 1}:")
            website = input("Enter the website URL:").lower()
            username = input("Enter Your Username :").lower()
            password = input("Enter Your Password :")

            credential.append({
                "website": website,
                "username": username,
                "password": password
            })
        print("Do you want to store your credentials in a file? (yes/no)")
        store_in_file = input("Enter your choice: ")
        if store_in_file.lower() == "yes":
            with open("passwords.txt", "a+") as file:
                for cred in credential:
                    file.write(f"Website: {cred['website']}, Username: {cred['username']}, Password: {cred['password']}\n")
        print("Credentials stored successfully!")

    elif manager.lower() == "retrieve":
            print("if you want to retrieve your credentials Type 'retrieve'")
            manager = input("Enter your choice: ")
            if manager.lower() == "retrieve":
                website_to_retrieve = input("Enter the website URL to retrieve credentials:").lower()
                with open("passwords.txt", "r") as file:
                    found = False
                    for line in file:
                        if website_to_retrieve == password["website"]:
                            print(f"Credentials for {website_to_retrieve}:")
                            print(line)
                            found = True
                            break
                    if not found:
                        print("No credentials found for the specified website.")

    elif manager.lower() == "see":
        with open("passwords.txt", "r") as file:
            print("All stored credentials:")
            for line in file:
                print(line.strip())

    elif manager.lower() == "remove":
        website_to_remove = input("Enter the website URL to remove credentials:").lower()
        with open("passwords.txt", "r") as file:
            lines = file.readlines()
        with open("passwords.txt", "w") as file:
            found = False
            for line in lines:
                if website_to_remove not in line:
                    file.write(line)
                else:
                    found = True
            if found:
                print(f"Credentials for {website_to_remove} removed successfully.")
            else:
                print("No credentials found for the specified website.")

    elif manager.lower() == "update":
        website_to_update = input("Enter the website URL to update credentials:").lower()
        with open("passwords.txt", "r") as file:
            lines = file.readlines()
        with open("passwords.txt", "w") as file:
            found = False
            for line in lines:
                if website_to_update in line:
                    print(f"Updating credentials for {website_to_update}:")
                    new_username = input("Enter the new username:").lower()
                    new_password = input("Enter the new password:")
                    file.write(f"Website: {website_to_update}, Username: {new_username}, Password: {new_password}\n")
                    found = True
                else:
                    file.write(line)
            if found:
                print(f"Credentials for {website_to_update} updated successfully.")
            else:
                print("No credentials found for the specified website.")

    elif manager.lower() == "exit":
        print("Exiting the program. Goodbye!")
        break 
    
    else:
        print("Invalid choice. Please try again.")