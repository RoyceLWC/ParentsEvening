# Parents' Evening System | Made by Royce Chan [February - April 2021]

import json  # Allowing for data to be stored
from datetime import \
    datetime as dt  # Allowing for time (objects) to be manipulated; reduce clutter with an abbreviation.
import pandas as pd  # Allowing for time series / manipulation
from tabulate import tabulate  # Allowing for schedules to be displayed in a formatted table.
# import pytz Allowing for timezone flexibility (e.g. Online meetings overseas)

from uuid import uuid4


# Reading and opening the JSON files
files = ["parents.json", "schedule.json"]
parents_data = {}
schedule_data = {}
for file_index in range(2):
    try:
        with open(files[file_index], "r") as read:
            files[file_index] = json.load(read)
    except (IOError, FileNotFoundError):
        with open(files[file_index], "w") as write:
            if file_index == 0:
                files[file_index] = {'parents': []}
                json.dump(files[file_index], write, indent=4)
            else:
                # Default dates
                d_dates = ["2020-11-01", "2020-11-02", "2020-11-03"]
                schedule = {}
                slots = [str(num) for num in list(range(1, 10))]
                for x in range(3):
                    schedule[d_dates[x]] = {}
                    for slot_num in slots:
                        schedule[d_dates[x]][slot_num] = [
                            False,
                            ""
                        ]
                json.dump(schedule, write, indent=4)
                files[file_index] = schedule

parents_data = files[0]
schedule_data = files[1]

# Initialising global variables (that can later be changed if needed)
custom_start_time = "17:00"
custom_end_time = "20:00"
date_format = "%Y-%m-%d"
time_format = "%H:%M"

confirm = ['yes', 'y', 'ye']
deny = ['no', 'n', 'nah']

time_slots = pd.date_range(
    start=custom_start_time,
    end=custom_end_time,
    freq='20T'  # 20-minute intervals
).to_pydatetime().tolist()  # Convert to datetime object

joined_slots = []
# ^Later change this into a repeatable function for new custom times
for slot_index in range(len(time_slots)):
    try:
        # Group each timestamp in two's to form a time slot.
        joined_slots.append([time_slots[slot_index], time_slots[slot_index + 1]])
    except IndexError:
        continue

scheduled_days = list(schedule_data.keys())  # Get the list of days from schedule.json
days = []
objects = []  # Setup range of datetime objects in order to assign the preferred datetime object from only the
# (abbreviated) day.

for day in scheduled_days:
    # Adding both the full and abbreviated name of each day to a list.
    days.append([
        dt.strftime(dt.strptime(day, date_format), "%A"),
        dt.strftime(dt.strptime(day, date_format), "%a")
    ])
    objects.append(dt.strptime(day, date_format))


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
        account_information = f"Username: {self.user}\nID: {self.user_id}\nChild(ren): {', '.join(self.children)}"
        if not self.meeting:
            account_information += f"\n - No meeting currently scheduled"
        else:
            account_information += f"\nMeeting: {self.meeting}"
        print(account_information)

        while True:
            back = input("[Enter 'B' to go back] ")
            print("-" * 67)
            if back.lower() == "b":
                break

        main_menu(self)

    def save(self, date=None, slot_number=None):
        if slot_number is not None:  # Scheduling
            slot_number = str(slot_number)
            # Writing to schedule.json file
            schedule_data[date][slot_number][0] = True
            schedule_data[date][slot_number][1] = self.user_id

        else:  # Deletion of meeting
            # Clearing the schedule data for the entry
            date_dict = schedule_data[self.meeting.split(' > ')[0]]  # Inner dictionary of the 3-day period dictionary
            slot_number = list(date_dict.keys())[list(date_dict.values()).index([True, self.user_id])]

            self.meeting = False  # Reset attribute (after dictionary indexing)

            date_dict[slot_number][0] = self.meeting
            date_dict[slot_number][1] = ""

        with open("schedule.json", "w") as write_schedule_json:
            json.dump(schedule_data, write_schedule_json, indent=4)

        # Writing to parents.json file
        for parent in parents_data["parents"]:
            if parent["id"] == self.user_id:
                parent["meeting"] = self.meeting

        with open("parents.json", "w") as write_parents_json:
            json.dump(parents_data, write_parents_json, indent=4)


def register():
    while True:
        register_username = input("Please enter a username: ")

        if register_username == "":
            print("Invalid input. Please try again.")
            continue

        # Checking for duplicates
        unique = True
        parent_usernames = [parent['username'].lower() for parent in parents_data['parents']]

        for username in parent_usernames:
            if register_username.lower() == username:
                unique = False

        if unique:
            break
        else:
            print(f"Username '{register_username}' has already been taken. Please try again.")
            print("-" * 67)

    while True:
        register_password = input("Please enter a (strong) password: ")
        contain_num = False

        for char in register_password:
            if char.isdigit():
                contain_num = True

        # Checking username validity/password strength
        if register_password == "":
            print("Invalid input. Please try again.")
        elif len(register_password) <= 7:
            print("Your password is too short. Please try again.")
        elif not contain_num:
            print("Your password must contain at least one digit. Please try again.")
        else:
            break

    while True:
        register_children = input("Please enter the full name of your child (if you have more than one, "
                                  "please separate each of their names with commas): ")

        if register_children == "":
            print("Invalid input. Please try again.")
        elif not register_children.replace(',', '').replace(' ', '').strip().isalnum():
            print("Invalid input. Child(ren) must only contain alphanumeric characters. Please try again.")
            print('-' * 67)
        else:
            break

    # Convert and separate the children into a list
    children_list = [child.strip() for child in register_children.split(",")]

    unique_id = str(uuid4())[:8]  # Generates a unique ID (first 8 characters of a UUID)

    # Dictionary storing parent's information to be written to JSON
    parent_dict = {
        "username": register_username,
        "password": register_password,
        "id": unique_id,
        "children": children_list,
        "meeting": False
    }

    parents_data["parents"].append(parent_dict)  # Append the dictionary to the JSON data
    with open("parents.json", "w") as write_json:
        json.dump(parents_data, write_json, indent=4)

    return parent_dict  # Return the user's username (in order to be passed through functions)


def login():
    login_success = False
    while not login_success:  # Continue looping until a successful attempt

        while True:
            username_input = input("Please enter your username or parent ID "
                                   "[If you don't have an account, please enter 'R' to register]: ")
            if username_input == "":  # Presence check
                print("Field left empty, please try again")
            else:
                break

        if username_input.lower() != "r":
            while True:
                password_input = input("Please enter your password: ")
                if password_input == "":  # Presence check
                    print("Field left empty, please try again.")
                else:
                    break

            parent_list = parents_data["parents"]
            success_dict = {}

            for loop_dict in parent_list:
                if (loop_dict["username"] == username_input or loop_dict["id"] == username_input) \
                        and loop_dict["password"] == password_input:
                    login_success = True
                    success_dict = loop_dict

                    # Ensure the value carried over is the username and not the ID.
                    username_input = loop_dict["username"]

            if login_success and success_dict:
                output_parent_object = Parent(username_input, success_dict["id"], success_dict["children"],
                                              success_dict["meeting"])
                print("-" * 67)
                return output_parent_object  # Return to main_menu()
            else:
                print("The username/parent ID and/or password you've entered doesn't match a registered account. "
                      "Please try again.")
                print("-" * 67)

        else:
            output_parent_dict = register()  # Register a new user and store the returned username value
            output_parent_object = Parent(output_parent_dict["username"], output_parent_dict["id"],
                                          output_parent_dict["children"], output_parent_dict["meeting"])
            print("-" * 67)
            return output_parent_object  # Return to main_menu()


def preferences(day_objects, full, abbreviated):
    while True:
        preferred_day = input(f"Which is your preferred day [{', '.join(abbreviated)}]? ")

        # Look-up check
        preferred_day = preferred_day.title()  # Ensure it is formatted correctly
        if preferred_day in full:
            preferred_day = day_objects[full.index(preferred_day)]
            break
        elif preferred_day in abbreviated:
            preferred_day = day_objects[abbreviated.index(preferred_day)]
            break
        else:  # If the entered day isn't the 3-days (or an invalid input)
            print("Invalid day entered. Please try again.")
    print("-" * 67)

    # Creating the start and end times from the preferred_day object.
    start_time = preferred_day.replace(hour=int(custom_start_time.split(':')[0]),
                                       minute=int(custom_start_time.split(':')[1]))
    end_time = preferred_day.replace(hour=int(custom_end_time.split(':')[0]), minute=int(custom_end_time.split(':')[1]))

    print(f"On each day, the appointments will start at {start_time.strftime(time_format)} and finish at "
          f"{end_time.strftime(time_format)}; they will all last 20 minutes.")
    while True:
        print("-" * 67)
        preferred_start_time = input(f"On {preferred_day.strftime('%A')} [{preferred_day.strftime('%x')}], please enter"
                                     " the starting time of your preferred time frame the appointment falls in ["
                                     "hh:mm]: ")
        preferred_end_time = input(f"On {preferred_day.strftime('%A')} [{preferred_day.strftime('%x')}], please enter"
                                   " the ending time of your preferred time frame the appointment falls in [hh:mm]: ")

        try:
            # Convert time input to a datetime object.
            preferred_start_time = dt.strptime(preferred_day.strftime(date_format) + preferred_start_time,
                                               '%Y-%m-%d%H:%M')
            preferred_end_time = dt.strptime(preferred_day.strftime(date_format) + preferred_end_time, '%Y-%m-%d%H:%M')

            diff = preferred_end_time - preferred_start_time
            diff_minutes = diff.total_seconds() / 60

            if diff_minutes < 20:
                print("Too short of a time frame inputted. Please ensure the time frame lasts at least 20 minutes and"
                      " try again.")
                continue

            if end_time >= preferred_end_time >= preferred_start_time >= start_time:
                break
            else:
                print("Invalid time input(s); the times inputted do not fit in the time frame and/or are in the wrong"
                      " order. Please try again.")

        except ValueError:
            print("Incorrect data format(s); it should be in the following format: hh:mm --- Please try again.")

    return preferred_start_time, preferred_end_time


def selection(parent, slot_range, length, option, initial_selection, selected_date=None,
              availability_check=False, availability_list=None, full_preferred_day_list=None, existing_check=False):
    loop1 = False
    loop2 = False
    raw_slot_selection = initial_selection

    chosen_slot = []
    full_time = ""

    try:
        slot_selection = int(initial_selection)

        if option == 'a':
            raw_slot_selection = (slot_selection - 1) % len(joined_slots)  # Convert the full selection to
            # one day's worth of slots (e.g. a full range of 1-27 to 1-9 per day)

            selected_date = scheduled_days[(slot_selection - 1) // len(joined_slots)]  # Get the date in
            # which the selection lies in using floor division.

            day_dict = schedule_data[selected_date]
            availability = list(day_dict.values())[raw_slot_selection][0]  # Find the Boolean value of
            # the selected slot.
        elif option == 'b':
            raw_slot_selection = int(slot_selection) - 1
            availability = full_preferred_day_list[raw_slot_selection][0]
        else:
            # Preserving the raw index (i.e. if suggested slot has been shifted multiple times).
            # Finding the element index in the full list from the isolated and condensed list.
            if availability_check or not existing_check:  # Accommodate for the excluded '0' option
                # when no suggestions are made.
                raw_slot_selection = joined_slots.index(availability_list[slot_selection - 1])
            else:
                raw_slot_selection = joined_slots.index(availability_list[slot_selection])

            availability = full_preferred_day_list[raw_slot_selection][0]

        if slot_range[0] <= slot_selection <= length and not availability:
            # Confirming appointment selection
            chosen_slot = joined_slots[raw_slot_selection]
            full_time = f"{selected_date} > " \
                f"{chosen_slot[0].strftime(time_format)}-{chosen_slot[1].strftime(time_format)}"
            print(f"Chosen appointment time slot: {full_time}")

            while True:
                confirm_choice = input("Confirm selection [Y/N]? ").lower()

                if confirm_choice in confirm:
                    loop1 = True
                    loop2 = True
                    break
                elif confirm_choice in deny:
                    print("Restarting selection...")
                    break
                else:
                    print("Invalid input. Please try again.")
                    print("-" * 67)
        else:
            print("Invalid input; your selection is either out of range or already occupied. "
                  "Please try again.")

    except IndexError:  # Double except statements rather than a parenthesised tuple in order to
        # raise 2 separate error messages.
        print("Invalid input; your selection is out of range. Please try again.")
    except ValueError:
        print("Invalid input. Please try again.")
    print("-" * 67)

    return loop1, loop2, raw_slot_selection, selected_date, chosen_slot, full_time


def scheduling(parent_object=None):
    if parent_object.meeting:  # Restrict user's from booking more than one appointment
        print("You already have a meeting booked. Please head to the cancellation/reallocation section to re-schedule"
              " a new meeting. [Returning to menu...]")
        print("-" * 67)
        main_menu(parent_object)
    else:
        # List comprehension - 2 lists for either the full or abbreviated names of the days.
        full_days = [d[0] for d in days]
        abbreviated_days = [d[1] for d in days]

        # time_delta = dt.strptime(custom_end_time, time_format) - dt.strptime(custom_start_time, time_format)
        # appointments = time_delta.seconds // 1200 Convert into minutes and divide by 20 (-minute appointments)

        print(f"This year's parents' evening period takes place on the following days: {', '.join(full_days)}")

        while True:
            preference_choice = input("Would you like to find a meeting based on a preferred day and time frame "
                                      "[Y/N]? ").lower()  # Confirm whether or not they have a preference.

            if preference_choice in confirm:
                preference = True
                preferred_start_time, preferred_end_time = preferences(objects, full_days, abbreviated_days)
                # Call preferences() and assign the two returned values.
                break
            elif preference_choice in deny:
                preference = False
                preferred_start_time = custom_start_time
                preferred_end_time = custom_end_time
                break
            else:
                print("Invalid input. Please try again.")
                print("-" * 67)

        # Time slots

        selected_date = ""
        chosen_slot = []
        full_time = ""
        raw_slot_selection = 0

        if preference:
            existing_check, availability_check, final_check, start_value, end_value, preferred_day_list, \
                full_availability_list = \
                display_schedule(
                    has_preference=True,
                    preferred_start=preferred_start_time,
                    preferred_end=preferred_end_time
                )

            slot_range = list(range(start_value, end_value))  # Adjust to 'user-friendly' numbers
            if len(slot_range) == 0:
                slot_range = [1, 0]

            last_slot = slot_range[-1]  # Remove redundancy

            if (existing_check or (not availability_check)) and final_check:  # Single print statement (before while
                # loop).
                print("Since there are no available slots in your preferred time frame, suggested bordering slots "
                      "have been displayed.")
            else:
                last_slot += 1  # Accommodate for the excluded '0' option when no suggestions are made (outside of loop)

            slot_range = [start_value, last_slot]

            confirm_loop = False  # Allow the nested while loop to be 'broken' out of.

            while not confirm_loop:
                if final_check:
                    print(f"Which appointment slot would you like to book [{slot_range[0]}-{slot_range[-1]}]? ")

                    slot_selection = input("[If you'd like to view all time slots over the 3 days, enter 'A' / "
                                           "If you'd like to view all time slots for this day, enter 'B'] ")
                else:
                    print("Your selected preferred day has been fully booked. Displaying the full 3-day schedule...")
                    slot_selection = "a"

                print("-" * 67)

                if slot_selection.lower() == "a":
                    full_selection = False
                    display_schedule(span=3)

                    length = len(joined_slots) * 3

                    while not full_selection:
                        slot_selection = input("Which appointment slot would you like to book "
                                               f"[{start_value}-{length}]? ")

                        confirm_loop, full_selection, raw_slow_selection, selected_date, chosen_slot, full_time = \
                            selection(
                                parent_object, slot_range, length, 'a', slot_selection
                            )

                elif slot_selection.lower() == "b":
                    selected_date = preferred_start_time.strftime(date_format)
                    length = len(preferred_day_list)
                    display_schedule(
                        preferred_start=preferred_start_time,
                        preferred_end=preferred_end_time
                    )

                    day_selection = False  # Allow the full-day appointment prompt to be looped.

                    while not day_selection:
                        slot_selection = input("Which appointment slot would you like to book "
                                               f"[{start_value}-{length}]? ")

                        confirm_loop, day_selection, raw_slot_selection, selected_date, chosen_slot, full_time = \
                            selection(
                                parent_object, slot_range, length, 'b', slot_selection, selected_date,
                                full_preferred_day_list=preferred_day_list
                            )

                else:
                    selected_date = preferred_start_time.strftime(date_format)
                    length = len(preferred_day_list)

                    confirm_loop, full_selection, raw_slot_selection, selected_date, chosen_slot, full_time = selection(
                        parent_object, slot_range, length, 'none', slot_selection, selected_date, availability_check,
                        full_availability_list, preferred_day_list, existing_check
                    )

        else:  # No preference (same as if preference: 'a')
            display_schedule(span=3)

            confirm_loop = False  # Allow the nested while loop to be 'broken' out of.

            length = len(joined_slots) * 3

            while not confirm_loop:
                slot_selection = input("Which appointment slot would you like to book "
                                       f"[1-{length}]? ")

                confirm_loop, full_selection, raw_slot_selection, selected_date, chosen_slot, full_time = selection(
                    parent_object, [1, 1], length, 'a', slot_selection
                )

        # Establishing the selection (writing to parents.json and schedule.json)
        raw_slot_selection += 1  # Account for dictionary which starts at slot 1.
        parent_object.meeting = full_time  # Update meeting (instance) attribute
        parent_object.save(selected_date, raw_slot_selection)

        print(f"Your meeting has been booked [{selected_date} > "
              f"{chosen_slot[0].strftime(time_format)}-{chosen_slot[1].strftime(time_format)}].")
        print("-" * 67)
        main_menu(parent_object)


def display_schedule(span=1, parent_object=None, temporary=False,
                     has_preference=False, preferred_start=None, preferred_end=None):  # Using keyword arguments
    slot_numbers = []  # Keep track of which slot numbers are 'selected' to determine whether or not they are occupied.

    try:
        if not parent_object.meeting:
            print("You do not have a scheduled meeting to display yet! Please book an appointment first. "
                  "Returning to menu...")
            print("-" * 67)
            return  # Return back to main() which leads back to main_menu() as it is in an infinite loop (restarting).
    except AttributeError:  # No object provided
        pass

    if has_preference:  # One-day coverage (part-day)
        preferred_joined_slots = []
        slot_number = 0
        borders = [0, len(joined_slots) - 1]
        border_count = 0  # Set count variable to add to (raw indexed) borders

        fallback_slot = []  # Last-resort slot if time frame doesn't span over a full appointment time frame.
        fallback_slot_number = 0

        for outer_index in range(len(joined_slots)):
            for i in range(2):
                # Adjusting default date to preferred date
                joined_slots[outer_index][i] = joined_slots[outer_index][i].replace(
                    year=preferred_start.year,
                    month=preferred_start.month,
                    day=preferred_start.day
                )

            # Make sure each slot is strictly within the preferred time frame.
            if joined_slots[outer_index][1] <= preferred_end and joined_slots[outer_index][0] >= preferred_start:
                preferred_joined_slots.append(joined_slots[outer_index])  # Add start-end time pair (slot) to 2D list.
                slot_numbers.append(slot_number)
                if border_count == 0:
                    borders[0], borders[1] = outer_index, outer_index  # Ensure both boundaries are initialised (i.e.
                    # in the case of only one possible slot from preferred time frame).
                else:
                    borders[1] = outer_index  # Keep updating the upper boundary on each greater occurrence.
                border_count += 1

            if preferred_start <= joined_slots[outer_index][0] <= preferred_end:
                fallback_slot.append(joined_slots[outer_index])
                fallback_slot_number = slot_number

            slot_number += 1

        final_check = False  # Check to create an escape path if the whole day has been booked out.

        if len(preferred_joined_slots) == 0:
            preferred_joined_slots = fallback_slot
            slot_numbers = [fallback_slot_number]
            borders = [fallback_slot_number] * 2

        # Determine the availability of each 'preferred' slot.
        preferred_availability_list = []

        # Get the list of values from each slot key of a day
        preferred_day_list = list(schedule_data[preferred_start.strftime(date_format)].values())

        availability_check = False  # Check to see if at least 1 slot in the preferred time frame is available.
        for index in slot_numbers:
            if not preferred_day_list[index][0]:  # Take the first (Boolean) value
                preferred_availability_list.append("Available   [✓]")
                availability_check = True  # Indicate at least one slot is available
                final_check = True
            else:
                preferred_availability_list.append("Unavailable [✗]")

        # Add column headers to Tabulate table
        tabulate_availability_list = [["Start Time:", "End Time:", "Availability:"]]
        full_availability_list = []  # Secondary table with times only

        # Initialise 2D array for Tabulate + add column headers
        availability_slot_number = 0
        for slot in preferred_joined_slots:
            tabulate_availability_list.append([
                f"({availability_slot_number + 1}) {slot[0].strftime(time_format)}",
                slot[1].strftime(time_format),
                preferred_availability_list[availability_slot_number]
            ])
            full_availability_list.append([
                slot[0],
                slot[1]
            ])

            availability_slot_number += 1

        start_value = 1
        existing_check = False  # Check to see whether or not at least one previous slot is available.

        if not availability_check:  # Suggest bordering appointments that are available
            # Determining a (possible) earlier available slot.
            earlier_slot_index = borders[0] - 1  # Set index one element back

            while earlier_slot_index >= 0:
                try:
                    if not preferred_day_list[earlier_slot_index][0]:  # Check if the previous slot is available
                        tabulate_availability_list.insert(1, [  # Add list to the beginning of the list (before).
                            f"(0) ({joined_slots[earlier_slot_index][0].strftime(time_format)}",
                            joined_slots[earlier_slot_index][1].strftime(time_format),
                            "Available   [✓])"
                        ])
                        full_availability_list.insert(0, [
                            joined_slots[earlier_slot_index][0],
                            joined_slots[earlier_slot_index][1]
                        ])

                        start_value = 0  # Include 0th element inserted
                        final_check = True
                        existing_check = True
                        break
                    earlier_slot_index -= 1

                except IndexError:
                    break

            # Determining a (possible) later available slot.
            later_slot_index = borders[1] + 1  # Set index one element forward (from the full list)
            while True:
                try:
                    if not preferred_day_list[later_slot_index][0]:  # Check if the next slot is available
                        tabulate_availability_list.append([
                            f"({availability_slot_number + 1}) "
                            f"({joined_slots[later_slot_index][0].strftime(time_format)}",
                            joined_slots[later_slot_index][1].strftime(time_format),
                            "Available   [✓])"
                        ])
                        full_availability_list.append([
                            joined_slots[later_slot_index][0],
                            joined_slots[later_slot_index][1]
                        ])

                        final_check = True
                        break
                    later_slot_index += 1

                except IndexError:
                    break

        if existing_check or final_check:  # With/starting at 0
            end_value = len(tabulate_availability_list) - 1
        else:  # Without 0 (starting at 1)
            end_value = len(tabulate_availability_list)

        print("-" * 67)
        print(tabulate(tabulate_availability_list, headers="firstrow"))
        print("-" * 67)

        if len(fallback_slot) == 1:  # If preferred time frame didn't strictly span over a full appointment slot
            print("Your time frame specified did not span a full appointment slot. "
                  "Adjustments were made to include any starting times that fell in between.")

        return existing_check, availability_check, final_check, start_value, end_value, preferred_day_list, \
            full_availability_list

    else:
        temp_formatted_time = ""
        if parent_object is not None:  # If user already has a meeting scheduled
            meeting_end_time = parent_object.meeting.split('-')[-1]  # Get the end time from last split section
            meeting_date = parent_object.meeting.split(' > ')[0]
        else:
            meeting_end_time = ""
            meeting_date = ""

        full_schedule_list = []
        dates = []
        full_slot_number = 1
        # date_index = 0
        # If span == 1 > One-day coverage (full-day, no preferred time slot)
        # If span == 3 > Three-day coverage
        for d in range(span):
            if preferred_start is not None:  # Single day
                # date_objects = [date.date() for date in objects]
                # date_index = date_objects.index(preferred_start.date())
                temp_date = preferred_start
            else:
                if span == 1:  # Adjust temp_date to match the indexed date, rather than the range (d).
                    temp_date = objects[scheduled_days.index(meeting_date)]
                else:
                    temp_date = objects[d]  # Reference earlier 'objects' list of scheduled day keys.

            temp_outer_list = []  # Create a temporary 2D array to add to full_schedule_list
            for outer_index in range(len(joined_slots)):
                temp_inner_list = []  # One row (for one slot's start/end times and its availability)
                for i in range(2):  # Loop once for the starting time data, and again for the ending time data
                    # Adjusting default date to each date key to append to full list with slot times.
                    temp_formatted_date = joined_slots[outer_index][i].replace(
                        year=temp_date.year,
                        month=temp_date.month,
                        day=temp_date.day
                    )
                    temp_formatted_time = temp_formatted_date.strftime(time_format)
                    if i == 0:  # Start time
                        temp_inner_list.append(f"({full_slot_number}) {temp_formatted_time}")
                    else:
                        temp_inner_list.append(temp_formatted_time)
                full_slot_number += 1

                current_day_list = list(schedule_data[temp_date.strftime(date_format)].values())

                if parent_object is not None and meeting_end_time == temp_formatted_time:
                    temp_inner_list.append(f">Your scheduled appointment [{parent_object.children[0]}]<")
                    # +1 onto the index for twins
                else:
                    if not current_day_list[outer_index][0]:  # Take the first (Boolean) value
                        temp_inner_list.append("Available   [✓]")
                    else:
                        temp_inner_list.append("Unavailable [✗]")
                temp_outer_list.append(temp_inner_list)

            dates.append(temp_date.strftime(date_format))  # Date sub-headings

            full_schedule_list.append(temp_outer_list)

        for table_list_index in range(len(full_schedule_list)):
            whitespace = "\u0009" * 4
            if parent_object is None:
                print(f"{whitespace}{dates[table_list_index]}")
            else:
                print(f"{whitespace}{meeting_date}")

            # Add columns
            full_schedule_list[table_list_index].insert(0, ["Start Time:", "End Time:", "Availability:"])
            print(tabulate(full_schedule_list[table_list_index], headers="firstrow"))
            print("-" * 67)

    if temporary:  # Re-direct back to menu if user already has a meeting (outside scheduling function) [one-time use].
        main_menu(parent_object)


def cancellation(parent_object=None):
    if not parent_object.meeting:
        print("You do not have a scheduled meeting yet! Please book an appointment first. Returning to menu...")
        print("-" * 67)
    else:
        print("This is the full schedule including your current booked meeting (slot):")
        display_schedule(parent_object=parent_object)

        while True:  # Cancellation
            confirm_cancellation = input(
                f"Would you like to cancel your current meeting [{parent_object.meeting}] [Y/N]? "
            ).lower()

            if confirm_cancellation in confirm:
                parent_object.save()
                break
            elif confirm_cancellation in deny:
                print("Returning back to menu...")
                print("-" * 67)
                main_menu(parent_object)
            else:
                print("Invalid input. Please try again.")
                print("-" * 67)

        while True:  # Possible reallocation
            confirm_reallocation = input("Would you also like to reschedule a new meeting [Y/N]? ").lower()

            if confirm_reallocation in confirm:
                print("Your meeting has been cancelled. Proceeding to the scheduler...")
                print("-" * 67)
                reallocation(parent_object)
            elif confirm_reallocation in deny:
                print("Your meeting has been cancelled. Returning back to menu...")
                print("-" * 67)
                break
            else:
                print("Invalid input. Please try again.")
                print("-" * 67)

    main_menu(parent_object)


def reallocation(parent_object=None):
    scheduling(parent_object)


def logout():  # Flush the user's data and return to the login page.
    print("Thank you for using our service. Logging off...")
    print("-" * 67)
    main()  # Create a new instance


def close():
    print("Thank you for using our service. Shutting down...")
    exit()


def main_menu(parent):
    print(f"Hello, {parent.user}. What would you like to do?")

    menu = {  # Initiate a menu dictionary
        "1": [": View account information", parent.account],
        "2": [": Schedule a meeting", scheduling],
        "3": [": Display your schedule", display_schedule],
        "4": [": Cancel/reallocate your meeting", cancellation],
        "5": [": Log out", logout],
        "6": [": Shut down", close]
    }

    for key in sorted(menu.keys()):
        print(key + menu[key][0])  # Print each menu index and its corresponding function (description)

    while True:  # Loop until a valid index is received
        print()
        index = input("Select an index: ")
        try:
            index = int(index)  # Convert to an integer (in order to perform comparisons)
            if 6 >= index >= 1:  # Range check
                break
            else:  # If not in range (menu indices)
                print("Out of range! Please try again.")
        except ValueError:  # If the input cannot be converted to an integer
            print("Invalid index. Please try again.")

    print("-" * 67)

    ignored_indexes = [1, 5, 6]

    if index in ignored_indexes:
        menu[str(index)][1]()  # Execute the Parent method.
    elif index == 3:
        menu[str(index)][1](parent_object=parent, temporary=True)
    else:
        menu[str(index)][1](parent_object=parent)  # Execute corresponding function retaining the parent object.


def main():
    # Go to parent/teacher login section
    print("Welcome to the Parents' Evening Scheduler.")
    parent_object = login()  # Go to login page
    while True:
        main_menu(parent_object)  # Go to the main menu after a successful login; pass in the parent object.


if __name__ == "__main__":
    print("Pearson Edexcel GCSE Computer Science Programming Project [W66484A]")
    print("- The following code was written by Royce Chan - February 2021.")
    print("-" * 67)
    main()
