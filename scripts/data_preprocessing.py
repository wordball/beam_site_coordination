# Written by Aditya Murali
import pandas as pd
from classes import *
from pathlib import Path
from datetime import datetime, timedelta
import calendar
import re
import numpy as np


# String Utils
def capitalize_first_letter(string: str):
    """
    Capitalizes the first letter in a string

    Args:
        string (str): input string

    Returns:
        (str): input string with the first letter capitalized
    """
    return string[0].upper() + string[1:]


def capitalize_name(name: str):
    """
    Split the name by spaces first and then by hyphens.
    Capitalize each subpart & then join everything together accordingly.

    Args:
        name (str): input name

    Returns:
        (str): name capitalized with proper spacing. Works for hyphenated
               names as well.
    """
    split_parts_by_spaces = re.split(r'\s+', name)
    for i, subpart in enumerate(split_parts_by_spaces):
        split_parts_by_hyphens = subpart.split('-')
        split_parts_by_hyphens = [capitalize_first_letter(part) for part in
                                  split_parts_by_hyphens]
        joined_parts_by_hyphens = '-'.join(split_parts_by_hyphens)
        split_parts_by_spaces[i] = joined_parts_by_hyphens
    return ' '.join(split_parts_by_spaces)


def standardize_time(string_time: str) -> str:
    """
    Written by Perplexity cuz I was too lazy.

    Standardizes strings representing times into the format
    ##:## [AM/PM] - ##:## [AM/PM]

    Examples:
    >>> standardize_time("11-12")
    "11AM - 12PM"
    >>> standardize_time("11:30-12:30 PM")
    "11:30AM - 12:30PM"
    >>> standardize_time("11:30  AM -12:30")
    "11:30AM - 12:30PM"
    >>> standardize_time("2:30   -    3:30")
    "2:30PM - 3:30PM"

    Limitations: Works only for times from 7:00 AM - 6:00 PM

    Args:
        string_time (str): A string representing a time range

    Returns:
        str: A standardized string representation of the time range
    """
    # Remove all whitespace
    string_time = re.sub(r'\s+', '', string_time)

    # Split the input into start and end times
    start, end = re.split(r'-', string_time)

    def parse_time(t):
        match = re.match(r'(\d{1,2})(?::(\d{2}))?([APap][Mm])?', t)
        if not match:
            raise ValueError(f"Invalid time format: {t}")

        hours, minutes, ampm = match.groups()
        hours = int(hours)
        minutes = int(minutes) if minutes else 0

        # Determine AM/PM if not specified
        if not ampm:
            ampm = 'AM' if 7 <= hours <= 11 else 'PM'
        else:
            ampm = ampm.upper()

        # Adjust hours for PM
        if ampm == 'PM' and hours < 12:
            hours += 12
        elif ampm == 'AM' and hours == 12:
            hours = 0

        return datetime(2000, 1, 1, hours, minutes), ampm

    # Parse start and end times
    start_time, start_ampm = parse_time(start)
    end_time, end_ampm = parse_time(end)

    # Adjust end time if it's earlier than start time (assuming it's the next day)
    if end_time <= start_time:
        end_time += timedelta(days=1)

    # Format the output
    start_str = start_time.strftime("%I:%M%p" if start_time.minute else "%I%p").lstrip('0')
    end_str = end_time.strftime("%I:%M%p" if end_time.minute else "%I%p").lstrip('0')

    return f"{start_str} - {end_str}"



def standardize_day(string_day: str) -> str:
    """
    Written by Perplexity cuz I was too lazy.

    Standardizes the names of the days.
    >>> standardize_day("Mon")
    'Monday'

    >>> standardize_day("tuesday")
    'Tuesday'

    >>> standardize_day("tuSedya")
    'Tuesday'

    Args:
        string_day (str): A string representing a day of the week

    Returns:
        str: Standardized name of the day of the week
    """
    # Eliminate leading and trailing whitespace
    string_day = string_day.strip()

    # List of full day names
    days = list(calendar.day_name)

    # Convert input to lowercase for case-insensitive matching
    input_day = string_day.lower()

    # Try to match the input with full day names
    for day in days:
        if input_day == day.lower():
            return day

    # If no match found, try to match with abbreviated day names
    for i, day in enumerate(calendar.day_abbr):
        if input_day.startswith(day.lower()):
            return days[i]

    # If still no match, use fuzzy matching
    for day in days:
        if len(set(input_day) & set(day.lower())) / len(input_day) > 0.5:
            return day

    # If no match found, raise an exception
    raise ValueError(f"Unable to standardize day: {string_day}")



def standardize_day_and_time(string_day_and_time: str) -> str:
    """
    Written by Perplexity cuz I was too lazy.
    Standardizes a string containing both a day and a time range.

    Examples:
    >>> standardize_day_and_time("Tuesday 3-4 PM")
    'Tuesday 3PM - 4PM'
    >>>
    'Tuesday 3PM - 4PM'
    >>> standardize_day_and_time(" tuesday  3- 4 PM ")
    'Tuesday 3PM - 4PM'

    Args:
        string_day_and_time (str): A string containing a day and a time range

    Returns:
        str: A standardized string representation of the day and time range
    """
    day_part, time_part = get_day_and_time(string_day_and_time)

    # Standardize the day
    standard_day = standardize_day(day_part)

    # Standardize the time
    standard_time = standardize_time(time_part)

    return f"{standard_day} {standard_time}"


# Step 1: Read Empty Site Map
def check_site_map_column_names(df: pd.DataFrame,
                                empty: bool):
    """
    Checks the column names of the site map.
    If the site map is empty, it's expected that the df has
    Day, Time, District, Site, Site Leader as columns.
    """
    if empty:
        if not (set(['Day', 'Time', 'District', 'Site']).issubset(
            set(df.columns))):
            raise Exception("Ensure that the site map column names are "
                            "spelled out as follows:\nDay\nTime\n"
                            "District\nSite")


def clean_site_map(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the site map.
    1. Gets rid of leading/trailing spaces.
    2.

    Args:
        df (pd.DataFrame): _description_

    Returns:
        pd.DataFrame: _description_
    """

    check_site_map_column_names(df, True)

    # Get rid of empty rows
    df = df.dropna(how='all')

    # Eliminate leading and trailing spaces
    for row in df.index.tolist():
        for col in df.columns:
            if type(df.loc[row, col]) == str:
                df.loc[row, col] = df.loc[row, col].strip()
    df = df.dropna(subset=['Site', 'District', 'Day', 'Time'], how='all')

    return df

def helpful_basic_function(mode: Literal['partial', 'full']) -> str:
    """
    0. Checks for exceptions
    1. Prints out list of people in order of how busy they are (most to least)
    2. Prints out list of drivers in order of how busy they are (most to least)
    """
    global PRINT_EXCEPTIONS_AS_USER_WARNINGS

    # Print everything - don't use exceptions
    prev_value = PRINT_EXCEPTIONS_AS_USER_WARNINGS
    PRINT_EXCEPTIONS_AS_USER_WARNINGS = True

    # Step 0
    check_for_edge_cases(mode)

    # Step 1: Print all names
    sls_ordered = order_by_availabilities(list(names_to_site_leaders.values()))
    non_SL_staff_ordered = (
        order_by_availabilities(list(names_to_nonSL_staff_members.values())))
    nonstaff_ordered = (
        order_by_availabilities(list(names_to_nonstaff.values())))
    titles_to_list = {
        'Site Leaders': sls_ordered,
        'Non-SL staff members': non_SL_staff_ordered,
        'Nonstaff members': nonstaff_ordered
    }

    for role_name, ordered_people in titles_to_list.items():
        ordered_names = [person.name for person in ordered_people]
        num_people = len(ordered_names)
        print(f"{num_people} {role_name} Ordered By Ascending Number of "
          "Availabilities (aka busiest to least busy people):\n"
          f"{', '.join(ordered_names)}\n")

    # Step 2: Print Driver Names
    titles_to_list = {
        'Site Leaders': sls_ordered,
        'Non-SL staff members': non_SL_staff_ordered,
        'Nonstaff members': nonstaff_ordered
    }
    all_drivers = [person for person in names_to_people.values() if
                   person.drives]
    titles_to_class = {
        'Site Leaders': SiteLeader,
        'Non-SL staff members': StaffMember,
        'Nonstaff members': DecalMember
    }
    for role_name, role in titles_to_class.items():
        relevant_drivers = [person for person in all_drivers if
                            type(person) == role]
        ordered_drivers = order_by_availabilities(relevant_drivers)
        ordered_names = [person.name for person in ordered_drivers]
        num_people = len(ordered_names)

        print(f"{num_people} DRIVERS: {role_name} Ordered By Ascending Number "
              f"of Availabilities (aka busiest to least busy people):\n"
              f"{', '.join(ordered_names)}\n")


    # Reassignment of the global variable
    PRINT_EXCEPTIONS_AS_USER_WARNINGS = prev_value



def read_empty_site_map(df: pd.DataFrame) -> pd.DataFrame:
    """
    Reads an empty site map which should have the following listed:
    1. Days of the week
    2. One Hour Time Slots
    3. School Names
    4. District Names
    """
    # TODO: standardize_site_map(df)
    df = clean_site_map(df)

    # Get the District column --> create District objects
    districts = list(df['District'].value_counts().keys())
    for district_name in districts:
        add_district(district_name)

    # For Loop: Create Site objects
    for row in df.index.tolist():
        district = names_to_districts[df.loc[row, 'District']]
        site_name = df.loc[row, 'Site']
        df.loc[row, 'Day'] = standardize_day(df.loc[row, 'Day'])
        df.loc[row, 'Time'] = standardize_time(df.loc[row, 'Time'])
        day_and_time = df.loc[row, 'Day'] + ' ' + df.loc[row, 'Time']
        district.add_site(site_name, day_and_time)

    return df

def read_populated_site_map(df: pd.DataFrame) -> None:
    if (times_to_sites == {} and names_to_sites == {} and
        names_to_districts == {} and ids_to_sites == {}):
        df = read_empty_site_map(df)

    # Exception messages to be used for later
    nonexistent_exception_msg = ("The {} named {} is on the "
                                 "site map but they did not fill out the "
                                 "google form.")
    validation_exception_msg = ("{} has been assigned to "
                                "the {} {} site that "
                                "takes place from {}.\n"
                                "However, they are not available during this "
                                "time.")
    nondriver_exception_msg = ("{} is put under the 'Driver(s)' column "
                               "for the {} {} site that "
                                "takes place from {}.\n"
                                "However, according to the google form "
                                "they filled out, they actually can't drive.")
    driver_exception_msg = ("{} is NOT put under the 'Driver(s)' column "
                            "for the {} {} site that "
                            "takes place from {}.\n"
                            "However, according to the google form "
                            "they filled out, they actually CAN drive.")
    wrong_number_of_mentors_exception_msg = ("There are {} mentors "
                                              "in the {} "
                                              "{} site that takes "
                                              "place from {}.\n"
                                              "But, the 'Number of 'Mentors' "
                                              "column says that there are "
                                              "{} mentors.")

    # Iterate through each site
    for row in df.index.tolist():
        site_name = df.loc[row, 'Site']
        site = names_to_sites[site_name]
        site_day = df.loc[row, 'Day']
        site_time_slot = df.loc[row, 'Time']

        # Check each member's name.
        # See if their name exists in the dictionaries
        # Ensure that the site day/time is in the person's availabilities

        # SiteLeader
        sl_name = df.loc[row, 'Site Leader']
        if not pd.isnull(sl_name):
            if sl_name not in names_to_site_leaders.keys():
                raise Exception(nonexistent_exception_msg.format(
                    'site leader', sl_name))
            else:
                site_leader = names_to_site_leaders[sl_name]
                if site.validate_person(site_leader):
                        site.add_member(site_leader)
                else:
                    raise Exception(validation_exception_msg.format(
                        sl_name, site_day, site_name, site_time_slot))

        # StaffMember
        nonSL_staff_name = df.loc[row, 'Staff Member']
        if not pd.isnull(nonSL_staff_name):
            if nonSL_staff_name not in names_to_nonSL_staff_members.keys():
                raise Exception(nonexistent_exception_msg.format(
                    'staff member', nonSL_staff_name))
            else:
                staff_member = names_to_nonSL_staff_members[nonSL_staff_name]
                if site.validate_person(staff_member):
                    site.add_member(staff_member)
                else:
                    raise Exception(validation_exception_msg.format(
                        nonSL_staff_name, site_day, site_name, site_time_slot))


        # DecalMember
        decal_names = [df.loc[row, f'Decal Member {i}'] for i in
                       range(1, 5)]
        for decal_name in decal_names:
            if not pd.isnull(decal_name):
                if decal_name not in names_to_nonstaff.keys():
                    raise Exception(nonexistent_exception_msg.format(
                        'decal member', decal_name))
                else:
                    decal_member = names_to_nonstaff[decal_name]
                    if site.validate_person(decal_member):
                        site.add_member(decal_member)
                    else:
                        raise Exception(
                            validation_exception_msg.format(
                                decal_name, site_day, site_name,
                                site_time_slot))

        # Check for names in the 'Driver(s)' column that represent people
        # who actually CANNOT drive.
        pandas_driver_value = df.loc[row, 'Driver(s)']
        if not pd.isnull(pandas_driver_value):
            apparent_driver_names = _convert_string_list_to_list_of_strings(
                pandas_driver_value)
            for name in apparent_driver_names:
                if name not in names_to_people.keys():
                    raise Exception(nonexistent_exception_msg.format(
                                    name, site_day, site_name,
                                    site_time_slot))
                else:
                    person = names_to_people[name]
                    if not person.drives:
                        raise Exception(nondriver_exception_msg.format(
                            name, site_day, site_name, site_time_slot))

            # Ensure that there is no one else who should be added to the
            # 'Driver(s)' column
            site_driver_names = site.get_driver_names()
            for actual_driver_name in site_driver_names:
                if actual_driver_name not in apparent_driver_names:
                    raise Exception(driver_exception_msg.format(
                        actual_driver_name, site_day, site_name, site_time_slot))

        # Ensure that the 'Number of Mentors' column is accurate
        num_mentors = site.get_num_people()
        apparent_num_mentors = int(df.loc[row, 'Number of Mentors'])
        if num_mentors != apparent_num_mentors:
            raise Exception(wrong_number_of_mentors_exception_msg.format(
                num_mentors, site_day, site_name, site_time_slot,
                apparent_num_mentors))







def check_google_form_response_column_names(df: pd.DataFrame):
    if set(df.columns).issubset(
        set(['name', 'availabilities', 'drives1',
             'drives2', 'last_tb_test', 'history', 'speaks_spanish'])):
        raise Exception("Issue with the google form response columns!!")


def change_google_form_response_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Changes & standardizes the column names of the google form responses
    for easier access

    Args:
        df (pd.DataFrame): dataframe containing google form responses

    Raises:
        Exception: in the case that the relevant columns have not been found
        #FIXME: If we don't need the extraneous columns to be caught,
                then remove them from the exception.

    Returns:
        pd.DataFrame: dataframe with standardized column names
    """

    def add_to_column_mappings(old_col_name:str,
                                new_col_name:str) -> None:
        """
        Function to map old column names to new column names

        Args:
            old_col_name (str)
            new_col_name (str)
        """
        if new_col_name in new_col_names:
            column_mappings[old_col_name] = new_col_name
            new_col_names.remove(new_col_name)

    df.columns = df.columns.str.lower()
    essential_new_col_names = ['name', 'availabilities', 'drives1', 'drives2']
    optional_new_col_names = ['last_tb_test', 'history', 'speaks_spanish']
    new_col_names = essential_new_col_names + optional_new_col_names
    column_mappings = {}

    # Create the column name mappings
    for question in df.columns:
        question = question.lower()
        if 'unnamed' not in question and 'name' in question:
            add_to_column_mappings(question, 'name')
        if 'available' in question:
            add_to_column_mappings(question, 'availabilities')
        if 'drive' in question and 'car' in question:
            if 'drives1' in new_col_names:
                add_to_column_mappings(question, 'drives1')
            else:
                add_to_column_mappings(question, 'drives2')
        if all([word in question for word in
                ['last', 'tb', 'tested']]):
            add_to_column_mappings(question, 'last_tb_test')
        if any([word in question for word in ['district', 'livescan',
                                                        'fingerprint']]):
            add_to_column_mappings(question, 'history')
        if 'spanish' in question:
            add_to_column_mappings(question, 'speaks_spanish')

    # Raise an exception if some of the relevant columns have not been found.
    essential_unassigned_new_col_names = [name for name in new_col_names if
                                            name in essential_new_col_names]
    if essential_unassigned_new_col_names:
        # print(f"Df columns: {df.columns}")
        # print(f"Column Mappings: {column_mappings}")
        raise Exception(
            "Some columns in the google response forms need to be changed. "
            "The remaining new (essential) column names to assign include the "
            f"following: {essential_unassigned_new_col_names}.")
    # print("Column Mappings:")
    # for key, value in column_mappings.items():
    #     print(f"{key} --> '{value}'")

    # Rename the dataframe columns accordingly
    df.rename(columns=column_mappings, inplace=True)
    # print("Renamed Column Names: ", ', '.join(list(df.columns)))

    # Return the dataframe but only select for the relevant columns
    return df

def extract_day_from_day_and_time(day_and_time):
    return day_and_time.split()[0]

def extract_time_from_day_and_time_as_int_minutes(day_and_time: str,
                                                  mode: Literal['start',
                                                                'end']) -> int:
    assert mode in ['start', 'end'], f"Wrong mode: {mode}"
    day_and_time_split = day_and_time.split()
    if mode == 'start':
        start_or_end_time = day_and_time_split[1]
    else:
        start_or_end_time = day_and_time_split[3]

    if 'AM' in start_or_end_time:
        no_suffix = start_or_end_time.split('AM')[0]
        if ":" in no_suffix:
            hours, minutes = [int(value) for value in no_suffix.split(":")]
        else:
            hours, minutes = int(no_suffix), 0
        return hours*60 + minutes

    elif 'PM' in start_or_end_time:
        no_suffix = start_or_end_time.split('PM')[0]
        if ":" in no_suffix:
            hours, minutes = [int(value) for value in no_suffix.split(":")]
        else:
            hours, minutes = int(no_suffix), 0
        if hours != 12:
            hours = hours + 12
        return hours*60 + minutes
    else:
        raise Exception("The following time slot (includes day and time) is "
                        "not standardized since there is no 'AM'/'PM' "
                        f"mentioned.\nTime Slot: {start_or_end_time}")

# Any times on the google form response dataframe that don't exist need to be changed to their appropriate time
# If there are not enough people on the site map who are available during a particular time,
def find_all_closest_time_matches(all_time_slots: List[str],
                                  site_map_times: List[str],
                                  tolerance: int):

    def get_closest_time_matches(time1):
        """Find all site times within tolerance of a given availability."""
        matches = []
        for site_time in site_map_times:
            if extract_day_from_day_and_time(time1) in site_time:
                time_diff = obtain_time_difference_between_time_slots(
                    time1, site_time)
                if abs(time_diff) <= tolerance:
                    matches.append((site_time, time_diff))

        # Prioritize times based on their time difference to the original(key)
        # Prioritize later times instead of earlier times given the same time
        # difference
        return sorted(matches, key=lambda x: (abs(x[1]), -1*x[1]))

    options = {} # maps all time slots from google form + site map times to closest site map times
    final_mappings = {} # final mappings from time slots (site map/google form) to the closest site map times

    for time_slot in all_time_slots:
        matches = get_closest_time_matches(time_slot)

        if matches:
            options[time_slot] = matches
            final_mappings[time_slot] = matches[0][0]  # Closest time

        else:
            print(f"No close matches for '{time_slot}' within {tolerance} minutes.")
            raise Exception(f"No matching site map times for: {time_slot}")

#     # Debugging: Display mappings
    # print("Options:")
    # for key, value in options.items():
    #     print(f"{key} --> {value}")
    # print("Final Mappings:")
    # for key, value in final_mappings.items():
    #     print(f"{key} --> {value}")

    return options

@DeprecationWarning
def check_google_form_for_time_mismatches(
        df: pd.DataFrame,
        tolerance: int) -> dict:
    """
    Assesses time slots listed in the Google Form responses and maps them to
    valid site map times based on a given tolerance.

    Args:
        df (pd.DataFrame): DataFrame containing Google Form responses.
            Requires a column named 'availabilities' with time strings.
        tolerance (int): Maximum allowed difference in minutes to consider
            a match.

    Returns:
        dict: Mappings of Google Form times to closest valid site map times.
    """

    def get_closest_time_matches(time1):
        """Find all site times within tolerance of a given availability."""
        matches = []
        for site_time in list(times_to_sites.keys()):
            if extract_day_from_day_and_time(time1) in site_time:
                time_diff = obtain_time_difference_between_time_slots(
                    time1, site_time)
                if abs(time_diff) <= tolerance:
                    matches.append((site_time, time_diff))

        # Prioritize times based on their time difference to the original(key)
        # Prioritize later times instead of earlier times given the same time
        # difference
        return sorted(matches, key=lambda x: (abs(x[1]), -1*x[1]))

    # Extract unique Google Form time slots
    all_availabilities = [
        time for row in df['availabilities']
        for time in extract_availabilities_from_string(row)]
    availabilities_list = list(set(all_availabilities))

    # Map Google Form times to site map times
    options_google_form_to_site_map = {}
    final_mappings = {}

    for availability in availabilities_list:
        matches = get_closest_time_matches(availability, times_to_sites.keys(),
                                           tolerance)

        if matches:
            options_google_form_to_site_map[availability] = matches
            final_mappings[availability] = matches[0][0]  # Closest time
        else:
            print(f"No close matches for '{availability}' within {tolerance} minutes.")
            raise Exception(f"No matching site map times for: {availability}")

    # Debugging: Display mappings
    print("Options:")
    for key, value in options_google_form_to_site_map.items():
        print(f"{key} --> {value}")
    print("Final Mappings:")
    for key, value in final_mappings.items():
        print(f"{key} --> {value}")

    return final_mappings

def fix_google_form_availabilities(
    google_form_df,
    person_class: Union[DecalMember, StaffMember, SiteLeader],
    tolerance: int) -> dict:
    """
    1. Identifies google form times that are not found in the site map
       and matches them to the closest site map times given a tolerance
    2. Identify site map times not matched to Google Form times and allocate
    additional availabilities based on teacher overlaps and a tolerance.

    Args:
        site_map_times (List): List of site map times.
        tolerance (int): Time difference in minutes to consider overlaps.

    Returns:
        dict: Updated schedule with additional availabilities allocated.
    """

    # Get google form availabilities
    google_form_availabilities_list = [
        time_slot for row in google_form_df['availabilities']
        for time_slot in extract_availabilities_from_string(row)]
    google_form_availabilities_list = list(set(
        google_form_availabilities_list))

    # Get site times
    site_map_times = [time_slot for time_slot in list(times_to_sites.keys())]

    """
    Aggregate times to map. Ensure no repeated times listed but preserve
    ordering. First is google form, then site map
    We do this to avoid rewriting the for loop since we want all the
    google form times to be consistent with the site map before
    we detect any site map times not found in the google forms.
    """

    times_to_map = list(dict.fromkeys(google_form_availabilities_list +
                                      site_map_times))

    # Get the closest time matches
    closest_time_matches = find_all_closest_time_matches(
        times_to_map, site_map_times, tolerance)

    times_which_needed_adjustment = {}
    # Iterate through the google form
    for time1 in times_to_map:
        potential_time_matches = [match[0] for match in
                                  closest_time_matches[time1]]
        # print(f"Potential time matches: {potential_time_matches}")

        """Replace any times that are only found in the google form
        but not in the site map with the closest match.
        Otherwise, if there aren't enough people available during a particular
        site time (e.g. let's say it wasn't included in the google form),
        we need to add the closest match."""
        if time1 in google_form_availabilities_list:
            closest_match = potential_time_matches[0]
            if time1 != closest_match:
                print(f"{time1} is not provided as a site map time but is on "
                      "the google form. We will replace it with "
                      f"'{closest_match}'.")
                for index in google_form_df.index.tolist():
                    google_form_df.loc[index, 'availabilities'] = (
                        google_form_df.loc[index, 'availabilities'].replace(
                            time1, closest_match))



        elif time1 in site_map_times: # but not in google_form_availabilites_list
            closest_match = True
            num_people_available = 0
            num_people_needed = count_number_of_people_required(time1,
                                                                person_class)

            while (num_people_available < num_people_needed and
                   len(potential_time_matches) > 0):

                if closest_match == True:
                    times_which_needed_adjustment[time1] = {}

                # Get the closest match and print
                closest_match = potential_time_matches.pop(0)

                # Find all the rows with the closest match and add time1
                # to the availabilities column
                available_df = google_form_df.loc[google_form_df[
                    'availabilities'].str.contains(closest_match)]

                # Create a list to store names of people who are put
                # may be potentially conscripted for time1
                names = []
                for index in available_df.index.tolist():
                    name = google_form_df.loc[index, 'name']

                    current_availabilities = (
                        google_form_df.loc[index, 'availabilities'])
                    if closest_match in current_availabilities:
                        google_form_df.loc[index, 'availabilities'] = (
                            ', '.join([current_availabilities, time1]))

                        # Add name to list of names
                        names.append(name)
                    else:
                        pass

                num_people_available = len(google_form_df.loc[google_form_df[
                    'availabilities'].str.contains(time1)])

                # Ignore first while loop since closest_match equals time1
                if closest_match != time1:
                    times_which_needed_adjustment[time1][closest_match] = names


            if (num_people_available <
                count_number_of_people_required(time1, person_class)):
                raise Exception("We have exhausted all possible alternatives "
                                f"with a tolerance of {tolerance} and we "
                                "still don't have enough people available "
                                f"on {time1}.")

    for time_slot in times_which_needed_adjustment:
        print(f"Time Slot which Needed More People: {time_slot}")
        dictionary = times_which_needed_adjustment[time_slot]
        for alt_time in dictionary.keys():
            print(f"Those who signed up for the {alt_time} slot will now "
                    f"be signed up for the {time_slot} slot")
            print(f"'Conscripted' Names: {dictionary[alt_time]}")
    print('-'*25)
    return google_form_df

def obtain_time_difference_between_time_slots(
    time_slot1: str,
    time_slot2: str):
    time_slot1_start_time = (
        extract_time_from_day_and_time_as_int_minutes(
            time_slot1, 'start'))
    time_slot1_end_time = (
        extract_time_from_day_and_time_as_int_minutes(
            time_slot1, 'end'))

    time_slot2_start_time = (
        extract_time_from_day_and_time_as_int_minutes(
            time_slot2, 'start'))
    time_slot2_end_time = (
        extract_time_from_day_and_time_as_int_minutes(
            time_slot2, 'end'))

    # Find the time shift difference in the time slots
    start_difference = (time_slot2_start_time - time_slot1_start_time)
    end_difference = (time_slot2_end_time - time_slot1_end_time)

    # Since each site lasts an hour, the start_difference must
    # match the end_difference.
    if start_difference != end_difference:
        raise Exception("There is a problem with either the "
                        "time provided by the person or the "
                        "site time.\nMember Time: "
                        f"{time_slot1}\nSite "
                        f"Time: {time_slot2}")
    return start_difference















def clean_google_form_responses(df: pd.DataFrame,
                                person_class,
                                time_tolerance: int) -> pd.DataFrame:
    """
    1. Change the google form column names
    2. Update the availabilities given a time tolerance.
    3. Update all names given a roster.
        - Can be done by highlighting the names on the spreadsheet and then putting
        - those on an isolated spreadsheet.

    """
    # Step 1
    df = change_google_form_response_column_names(df)

    # Step 2
    # updated_availabilities = check_google_form_for_time_mismatches(df, time_tolerance)
    # for index in df.index.tolist():
    #     for key, value in updated_availabilities.items():
    #         df.loc[index, 'availabilities'] = df.loc[index,
    #                                                  'availabilities'].replace(
    #                                                      key, value)


    # Step 2 Alternative

    df = standardize_times_in_df(df)
    df = fix_google_form_availabilities(df, person_class, time_tolerance)


    return df

def extract_availabilities_from_string(availabilities: str) -> List[str]:
    availabilities = availabilities.replace('*', '')
    availabilities = _convert_string_list_to_list_of_strings(availabilities)
    availabilities = [standardize_day_and_time(availability) for
                      availability in availabilities]
    if availabilities == []:
        raise Exception("No availabilities provided!")
    return availabilities

def _handle_message_for_bad_data(row,
                                 person_class: Union[DecalMember,
                                                      StaffMember,
                                                      SiteLeader],
                                 insert_string_with_column_name: str,
                                 continue_with_bad_data: bool,
                                 alternative: str):

    person_class_to_string = {DecalMember: "decal member",
                              StaffMember: "non-SL staff member",
                              SiteLeader: "site leader"}
    string = person_class_to_string[person_class]
    error_string_message = (f"Row {row} of the {string} responses "
                            f"spreadsheet has bad data in "
                            f"{insert_string_with_column_name} column(s).")

    if continue_with_bad_data:
        print(error_string_message)
        print(f"We will assume a value of '{alternative}' for this column "
              "instead.")
    else:
        raise Exception(error_string_message)

def standardize_time_entries_in_dataframe(string_time: str):
    times_list_of_strings = extract_availabilities_from_string(string_time)
    string_list_of_times = ', '.join(times_list_of_strings)
    return string_list_of_times

def standardize_times_in_df(df: pd.DataFrame):
    df['availabilities'] = df.apply(lambda row: standardize_time_entries_in_dataframe(row['availabilities']), axis=1)
    return df


def read_google_form_responses(df: pd.DataFrame,
                               person_class: Union[DecalMember,
                                                   StaffMember,
                                                   SiteLeader],
                               time_tolerance: int,
                               continue_with_bad_data: bool) -> None:
    """
    name: string
    availabilities: time slots separated by comma. Some times have asterisks
                    as well to indicate extended travel time.
    drives1 = Yes/No --> True/False
    drives2 = Yes/No --> True/False
    last_tb_test = str --> extract the number of years
    history = district names separated by comma
    speaks_spanish = Yes/No --> True/False
    """
    df = clean_google_form_responses(df, person_class, time_tolerance)

    indices = df.index.tolist()
    for row in indices:

        #FIXME: YOUR DATA MIGHT BE CORRUPTED!
        name = df.loc[row, 'name']
        if pd.isnull(name):
            _handle_message_for_bad_data(row, person_class,
                                         "the 'name'", continue_with_bad_data,
                                         'No Name')
            if continue_with_bad_data:
                name = 'No Name'


        try:
            availabilities = df.loc[row, 'availabilities']
            availabilities = _convert_string_list_to_list_of_strings(
                availabilities)

        except:
            _handle_message_for_bad_data(row, person_class,
                                         "the 'availabilities'",
                                         continue_with_bad_data, "")

            # Skip this person if they don't provide availabilities
            if continue_with_bad_data:
                print(f"We are not assigning {name} to a site because they "
                      "did not provide any availabilities. Please tell them "
                      "to fill out the google form again.")
                continue


        try:
            drives1 = df.loc[row, 'drives1']
            drives1 = _convert_yes_no_to_bool(drives1)
        except:
            _handle_message_for_bad_data(row, person_class,
                                         "one of the driving",
                                         continue_with_bad_data,
                                         "No")
            drives1 = False


        try:
            drives2 = df.loc[row, 'drives2']
            drives2 = _convert_yes_no_to_bool(drives2)
        except:
            _handle_message_for_bad_data(row, person_class,
                                         "one of the driving",
                                         continue_with_bad_data,
                                         "No")
            drives2 = False
        drives = drives1 or drives2


        # Handle optional columns
        kwargs = {}
        if 'last_tb_test' in df.columns:
            try:
                last_tb_test = _convert_last_tb_test_to_int_years(
                    df.loc[row, 'last_tb_test'])
                kwargs['last_tb_test'] = last_tb_test
            except:
                _handle_message_for_bad_data(row, person_class,
                                             "the 'last tb test'",
                                             continue_with_bad_data,
                                             "never")

        if 'history' in df.columns:
            try:
                history = _convert_string_list_to_list_of_strings(
                    df.loc[row, 'history'])
                kwargs['history'] = history
            except:
                _handle_message_for_bad_data(row, person_class,
                                             "the 'past districts'",
                                             continue_with_bad_data,
                                             "n/a")

        if 'speaks_spanish' in df.columns:
            try:
                speaks_spanish = _convert_yes_no_to_bool(
                    df.loc[row, 'speaks_spanish'])
                kwargs['speaks_spanish'] = speaks_spanish
            except:
                _handle_message_for_bad_data(row, person_class,
                                             "the 'speaks spanish'",
                                             continue_with_bad_data,
                                             "No")

        new_person = person_class(name=name,
                                  availabilities=availabilities,
                                  can_drive=drives,
                                  **kwargs)
        # print(str(new_person))

    return df

def _convert_string_list_to_list_of_strings(string_list:str) -> List[str]:
    lst = string_list.split(', ')
    return lst

def _convert_yes_no_to_bool(yes_or_no: str) -> bool:
    lowercase_no_spaces = yes_or_no.lower().strip()
    if lowercase_no_spaces == 'yes':
        return True
    elif lowercase_no_spaces == 'no':
        return False
    else:
        raise Exception("Expecting a yes/no as input. "
                        f"Got something else: {yes_or_no}")

def _convert_last_tb_test_to_int_years(last_tb_test: str) -> int:
    """
    Examples:
    >>> "5+ year(s) ago" -> 5
    >>> "4 year(s) ago" --> 4
    >>> "1 year(s) ago" --> 1

    Limitations: can't handle tb tests obtained less than 1 year ago.

    Args:
        last_tb_test (str): string representing when the person got their last
                            tb test

    Returns:
        int: number of years representing last tb test
    """
    num_years = int(re.match("[0-9]", last_tb_test).group(0))
    return num_years


def execute(
    empty_site_map_path: Path,
    SL_availabilities_path: Path,
    staff_availabilities_path: Path,
    nonstaff_availabilities_path: Path,
    mode: Literal['full', 'partial']) -> SiteArrangement:
    """
    This function executes everything that needs to get done.
    Let's think it through.

    1. Site Coords will get the availabilities of site leaders, then staff,
    then decal members. This means that the site coords will need to have made
    the site leader/staff forms FIRST.

    2. Once those availabilities are obtained using the boilerplate decal
    forms, then we can worry about populating an empty site map.
        - Feed in the empty site map FIRST into the program.

    3. Create the google forms.
        - Times should all be the same ideally or at least in a standardize-able format.
        - Each google form should be editable & can only be filled out ONCE.
        - Actually in the ideal case, it would be best to ensure that emails are recorded & ensure that it is only Berkeley Emails!)
            - This can be used for cross-referencing in case people don't spell their name correctly.

    4. Feed in the google form responses
            - Standardize the times
            - Keep the names as is & note their email addresses. #TODO (add an email attribute)

    NOTE: Since this whole process will take place over multiple days, we may require the site map and the responses to be saved.
          We can see whether any information needs to be saved or not but if we need to, we can serialize the information.

    5.        -
        spot for any inconsistencies
        -
    """

    # Read the empty site map
    read_empty_site_map(pd.read_csv(empty_site_map_path))

    # Read availabilities dataframes
    paths = [SL_availabilities_path, staff_availabilities_path,
             nonstaff_availabilities_path]
    dfs = list(map(lambda x: pd.read_csv(x), paths))

    # Read each google form response
    people_classes = [SiteLeader, StaffMember, DecalMember]
    for person_class, df in dict(zip(people_classes, dfs)).values():
        read_google_form_responses(df, person_class)

    # Generate SiteArrangements
    site_arrangements = (
        create_site_arrangements(list(names_to_people.values()), mode))
    return site_arrangements[0]

def count_number_of_people_available(time_slot: str,
                                     person_class: Union[DecalMember,
                                                         StaffMember,
                                                         SiteLeader]) -> int:
    """
    Counts the number of people who belong to the DecalMember, StaffMember,
    or SiteLeader classes

    Args:
        time_slot (str): string time slot
        person_class (Union[DecalMember, StaffMember, SiteLeader]):
            the type of person you're trying to count

    Returns:
        int: number of people who belong to person_class and are available
              during a particular time_slot
    """
    people_who_are_available = determine_who_is_available(time_slot,
                                                          person_class)
    return len(people_who_are_available)

def determine_who_is_available(time_slot: str,
                               person_class: Union[DecalMember,
                                                   StaffMember,
                                                   SiteLeader]) -> List:
    """
    Determine the people who belong to the DecalMember, StaffMember,
    or SiteLeader classes

    Args:
        time_slot (str): string time slot
        person_class (Union[DecalMember, StaffMember, SiteLeader]):
            the type of person you're trying to count

    Returns:
        List: people who belong to person_class and are available
              during a particular time_slot
    """

    # Create a dictionary relating the class to the dictionary
    class_to_dictionary = {DecalMember: names_to_nonstaff,
                           StaffMember: names_to_nonSL_staff_members,
                           SiteLeader: names_to_site_leaders}

    # Determine the relevant dictionary
    for key in list(class_to_dictionary.keys()):
        if person_class == key:
            relevant_dictionary = class_to_dictionary[key]

    relevant_people = list(relevant_dictionary.values())

    # Count the number of people whose availability matches the
    # time_slot parameter
    return [person for person in relevant_people if time_slot in
            person.availabilities]

def count_number_of_people_required(time_slot: str,
                                    person_class: Union[DecalMember,
                                                        StaffMember,
                                                        SiteLeader]):
    num_sites = len(times_to_sites[time_slot])

    if person_class == SiteLeader:
        return num_sites

    elif person_class == StaffMember:

        # Using LP using v2 nonSL-staff members doesn't work without setting
        # return val to num_sites
        # num_nonstaff = count_number_of_people_available(time_slot,
        #                                                 DecalMember)
        # min_nonSL_staff = (num_sites * (MIN_PEOPLE_PER_SITE-1) -
        #                    num_nonstaff)
        # return min_nonSL_staff
        return num_sites

    else:
        # num_nonSL_staff = count_number_of_people_available(time_slot,
        #                                                    StaffMember)
        # min_nonstaff_necessary = (MIN_NONSTAFF_PER_SITE *
        #                           num_nonSL_staff +
        #                           (MIN_PEOPLE_PER_SITE-1) *
        #                           (num_sites - num_nonSL_staff))
        # return min_nonstaff_necessary
        return 3



def enough_people_available(time_slot: str,
                            person_class: Union[DecalMember,
                                                StaffMember,
                                                SiteLeader]):
    msg = ("There are not enough {} present on " + time_slot +
           "\nExpected: {}, Actual: {}")
    person_class_to_str = {SiteLeader: 'site leaders',
                           StaffMember: 'non-SL staff members',
                           DecalMember: 'nonstaff/decal members'}
    num_available = count_number_of_people_available(time_slot,
                                                     person_class)
    num_required = count_number_of_people_required(time_slot,
                                                   person_class)

    if num_available < num_required:
        formatted_message = msg.format(person_class_to_str[person_class],
                                       num_required,
                                       num_available)
        print(formatted_message)
        return False
    else:
        return True


def determine_if_every_availability_has_enough_people() -> None:

    """
    Run this function after reading all the dataframes.
    Superficially checks if there's enough people to fill each time slot.

    Raises:
        Exception: exception string explains to the user which time slots
                   need more people.
    """

    string_times = list(times_to_sites.keys())
    exception_str = ""

    # Use dictionaries to record time slots during which there are an
    # insufficient number of site leaders, other staff members, or decal
    # members available
    not_enough_people_available = {}


    # Iterate through each time slot in string_times
    for time_slot in string_times:
        issue_found = False
        time_slot_str = ""


        # number of sites which take place during the time slot
        num_sites = len(times_to_sites[time_slot])

        # people who are available during the time slot
        SLs = determine_who_is_available(time_slot, SiteLeader)
        numSLs = len(SLs)
        nonSL_staff = determine_who_is_available(time_slot, StaffMember)
        num_nonSL_staff = len(nonSL_staff)
        nonstaff = determine_who_is_available(time_slot, DecalMember)
        num_nonstaff = len(nonstaff)


        if numSLs < num_sites:
            issue_found = True
            not_enough_people_available.get(time_slot, {})['SiteLeader'] = SLs
            time_slot_str += (
                    f"We need {num_sites} site leaders but we "
                    f"only have {numSLs}: "
                    f"{not_enough_people_available[time_slot]['SiteLeader']}"
                    "\n")


        # For only 4-person sites, there are 2 configurations
        # 1 non-SL staff member + 2 decal members OR 3 decal members
        if num_nonSL_staff < num_sites:
            min_nonstaff_necessary = (MIN_NONSTAFF_PER_SITE *
                                        num_nonSL_staff +
                                        MAX_NONSTAFF_PER_SITE *
                                        (num_sites -
                                        num_nonSL_staff))
        else:
            min_nonstaff_necessary = (MIN_NONSTAFF_PER_SITE *
                                        num_sites)

        if num_nonstaff < min_nonstaff_necessary:
            issue_found = True

            dictionary = not_enough_people_available.get(time_slot, {})
            dictionary['StaffMember'] = nonSL_staff
            dictionary['DecalMember'] = nonstaff

            time_slot_str += (
                    f"We have {num_nonSL_staff} staff members who are NOT "
                    f"site leaders and {num_nonstaff} decal members. \n"
                    f"We have {3*num_sites} spots we need to fill. \n"
                    "You do the math & you'll realize we either don't have "
                    "enough available staff members(who don't lead site) or "
                    "decal members. \nNames of the staff members: "
                    f"{nonSL_staff}\nNames of the decal members: {nonstaff}.\n"
                )

        if issue_found:
            time_slot_str = (f"Time Slot: {time_slot} - {num_sites} sites.\n"
                             + time_slot_str)
        exception_str += time_slot_str

    if exception_str:
        raise Exception(exception_str)

def determine_who_chose_little_to_no_site_times() -> None:
    """
    Tells the user which people are busy prior to creating the site
    arrangements.

    Raises:
        Exception: raised when there are people who did not select an available
                   time slot.
    """
    no_availabilities = []
    busy_people = {SiteLeader: [],
                   StaffMember: [],
                   DecalMember: []}

    # Add people with no availabilities or people who are busy
    for person in names_to_people.values():
        if len(person.availabilities) == 0:
            no_availabilities.append(person)
        elif len(person.availabilities) <= BUSY_THRESHOLD:
            busy_people[type(person)].append(person)
        else:
            pass

    # Order each person in the values of busy_people by availabilities
    for person_class in [SiteLeader, StaffMember, DecalMember]:
        busy_people[person_class] = order_by_availabilities(
            busy_people[person_class])

    # Print out the names of the people who did not provide any availabilities.
    if no_availabilities:
        raise Exception("Here are the people who provided no availabilities: "
                        f"{no_availabilities}\n")

    # Go through different numbers of availabilities from 1 to BUSY_TRESHOLD+1
    for num_availabilities in range(1, BUSY_THRESHOLD+1):

        # List of site leaders, nonSL_staff, and decal members
        sls = [person for person in busy_people[SiteLeader] if
               len(person.availabilities) == num_availabilities]
        nonSL_staff = [person for person in busy_people[StaffMember] if
                       len(person.availabilities) == num_availabilities]
        nonstaff = [person for person in busy_people[DecalMember] if
                    len(person.availabilities) == num_availabilities]

        # Print the message.
        if sls + nonSL_staff + nonstaff:
            msg = (
                "Here are the following people who only provided "
                f"{num_availabilities} availabilities -->\n")

            if sls:
                msg += f"{len(sls)} site leader(s): {sls}\n"

            if nonSL_staff:
                msg += (
                    f"{len(nonSL_staff)} staff member(s) who is/are NOT site "
                    f"leader(s): {nonSL_staff}\n")

            if nonstaff:
                msg += f"{len(nonstaff)} decal members: {nonstaff}\n"

    if msg:
        print(msg)

def choose_best_name(name1: str,
                     name2: str) -> str:
    best_option = None
    if name2 == 'No Match!':
        best_option = name1
    elif name1 == str(np.nan) or name2 == str(np.nan):
        return str(np.nan)
    else:
        if len(name1.split()) > len(name2.split()):
            best_option = name1
        else:
            best_option = name2
    print(f"Options for name include '{name1}' and '{name2}'")
    capitalized_name = capitalize_name(best_option)
    print(f"Capitalized name: {capitalized_name}")
    return capitalized_name


