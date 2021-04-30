# Parents' Evening System | Royce Chan

import json  # Allowing for data to be stored


# Reading and opening the JSON files
# Enter the JSON code here

# Initialising global variables (that can later be changed)
custom_start_time = "17:00"
custom_end_time = "20:00"
date_format = "%Y-%m-%d"
time_format = "%H:%M"


# Parent Class
class Parent:
    def __init__(self, user, user_id, children, meeting):
        self.user = user
        self.user_id = user_id
        self.children = children
        # self.date_of_births = date_of_births
        self.meeting = meeting

    # Printing a user's information based on parent object.
    def account(self):
        pass

    def selection(self):
        pass


def register():
    pass


def login(parent_object=None):
    return parent_object


def preferences():
    pass


def scheduling(parent_object=None):
    pass


def display_schedule(parent_object=None):
    pass


def cancellation(parent_object=None):
    pass


def reallocation(parent_object=None):
    pass


def timezones(parent_object=None):
    pass


def logout():  # Flush the user's data and return to the login page.
    pass


def close():
    pass


def main_menu(parent):
    print(f"Hello, {parent.user}. What would you like to do?")

    menu = {  # Initiate a menu dictionary
        "1": [": View account information", parent.account],
        "2": [": Schedule a meeting", scheduling],
        "3": [": Display your schedule", display_schedule],
        "4": [": Cancel/reallocate your meeting", cancellation],
        "5": [": Adjust timezone", timezones],
        "6": [": Log out", logout],
        "7": [": Shut down", close]
    }

    for key in sorted(menu.keys()):
        print(key + menu[key][0])  # Print each menu index and its corresponding function (description)

    while True:  # Loop until a valid index is received
        print()
        index = input("Select an index: ")
        try:
            index = int(index)  # Convert to an integer (in order to perform comparisons)
            if 7 >= index >= 1:  # Range check
                break
            else:  # If not in range (menu indices)
                print("Out of range! Please try again.")
        except ValueError:  # If the input cannot be converted to an integer
            print("Invalid index. Please try again.")

    print("-" * 67)

    ignored_indexes = [1, 6, 7]

    if index in ignored_indexes:
        menu[str(index)][1]()  # Execute the Parent method.
    elif index == 3:
        menu[str(index)][1](parent_object=parent, temporary=True)
    else:
        menu[str(index)][1](parent_object=parent)  # Execute corresponding function retaining the parent object.


def main():
    print("Pearson Edexcel GCSE Computer Science Programming Project [W66484A]")
    print("- The following code was written by Royce Chan - February 2021.")
    print("-" * 67)

    # Go to parent/teacher login section
    print("Welcome to the Parents' Evening Scheduler.")
    parent_object = login()  # Go to login page
    main_menu(parent_object)  # Go to the main menu after a successful login; pass in the parent object.


if __name__ == "__main__":
    main()
