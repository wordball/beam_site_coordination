# Written by Aditya Murali
import pandas as pd
from classes import (names_to_site_leaders,
                     SiteLeader,
                     StaffMember,
                     DecalMember,
                     District,
                     School,
                     Site)
from pathlib import Path
from datetime import datetime, timedelta
import calendar


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
        joined_parts_by_hyphens = '-'.join(split_parts_by_hyphens)
        split_parts_by_spaces[i] = joined_parts_by_hyphens
    return ' '.join(split_parts_by_spaces)


def standardize_time(string_time):
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
    >>> standardize_day_and_time("tue3-4PM")
    'Tuesday 3PM - 4PM'
    >>> standardize_day_and_time("tuesday  3- 4 PM")
    'Tuesday 3PM - 4PM'

    Args:
        string_day_and_time (str): A string containing a day and a time range

    Returns:
        str: A standardized string representation of the day and time range
    """
    # Split the day and time using regex
    match = re.match(r'([a-zA-Z]+)\s*(.+)', string_day_and_time)

    if not match:
        raise ValueError(f"Invalid format: {string_day_and_time}")

    day_part, time_part = match.groups()

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
    check_site_map_column_names(df, True)
    return df


def read_empty_site_map(df: pd.DataFrame) -> None: # TODO
    """
    Reads an empty site map which should have the following listed:
    1. Days of the week
    2. One Hour Time Slots
    3. School Names
    4. District Names
    """
    # TODO: standardize_site_map(df)
    clean_site_map(df)

    # Get rid of empty rows
    df = df.dropna(how='all')

    # TODO: Get the District column --> create District objects
    districts = list(df['District'].value_counts().keys())
    for district_name in districts:
        new_district = District(district_name)
    # TODO: for loop --> add schools & sites --> it shouldn't matter what the site/school name is.
    pass





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



    new_col_names = ['name', 'availabilities', 'drives1', 'drives2',
             'last_tb_test', 'history', 'speaks_spanish']
    column_mappings = {}

    # Create the column name mappings
    for question in df.columns:
        if 'name' in question:
            add_to_column_mappings(question, 'name')
        if 'available' in question:
            add_to_column_mappings(question, 'availabilities')
        if 'drive' in question.lower():
            add_to_column_mappings(question, 'drives1')
        if any([word in question.lower() for word in ['gig', 'uber', 'lyft',
                                                      'zip', 'zipcar']]):
            add_to_column_mappings(question, 'drives2')
        if all([word in question.lower() for word in
                ['last', 'tb', 'tested']]):
            add_to_column_mappings(question, 'last_tb_test')
        if any([word in question.lower() for word in ['district', 'livescan',
                                                      'fingerprint']]):
            add_to_column_mappings(question, 'history')
        if 'spanish' in question.lower():
            add_to_column_mappings(question, 'speaks_spanish')

    # Raise an exception if some of the relevant columns have not been found.
    if new_col_names != []:
        raise Exception(
            "Some columns in the google response forms need to be changed. "
            "The remaining new column names to assign include the following: "
            f"{new_col_names}")

    # Rename the dataframe columns accordingly
    changed_df = df.rename(columns=column_mappings)

    # Return the dataframe but only select for the relevant columns
    return changed_df[list(column_mappings.values())]

def clean_google_form_responses(df: pd.DataFrame) -> pd.DataFrame:
    """
    Change the google form column names

    """
    df = change_google_form_response_column_names(df)


def read_google_form_responses(df: pd.DataFrame,
                               person_class): # TODO
    """
    Columns include
    'name'
    'drives1'
    'drives2'
    'last_tb_test'
    'history'
    'availabilities'
    """
    pass

    df = clean_google_form_responses(df)
    pass

#
def initialize_empty_site_map() -> pd.DataFrame:
    """
    Returns:
        pd.DataFrame: empty site map
    """
    columns = (['Site', 'School', 'District', 'Day', 'Time', 'Site Leader',
               'Driver(s)', 'Staff Member'] +
               [f'Decal Member {i}' for i in range(1, 5)])
    index = [i for i in range(len(names_to_site_leaders.keys()))]
    df = pd.DataFrame(index = index, columns = columns)
    return df


def execute(
    empty_site_map_path: Path,
    SL_availabilities_path: Path,
    staff_availabilities_path: Path,
    nonstaff_availabilities_path: Path
):
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
    read_empty_site_map(pd.read_csv(empty_site_map_path))
    read_google_form_responses(SL_availabilities_path, SiteLeader)
    read_google_form_responses(staff_availabilities_path, StaffMember)
    read_google_form_responses(nonstaff_availabilities_path, DecalMember)






# Generate site maps

# Data Processing Functions
# Some of these functions hopefully won't be used if the google forms are standardized properly
import re
def standardize_time(time): # TODO
    time = re.sub(r"11-12pm", "11:00am-12:00pm", time)
    time = re.sub(r"12-1pm", "12:00-1:00pm", time)
    time = re.sub(r"1-2pm", "1:00-2:00pm", time)
    time = re.sub(r"2-3pm", "2:00-3:00pm", time)
    time = re.sub(r"3-4pm", "3:00-4:00pm", time)
    time = re.sub(r"4-5pm", "4:00-5:00pm", time)
    time = re.sub(r"5-6pm", "5:00-6:00pm", time)
    time = re.sub(r"am", "AM", time)
    time = re.sub(r"pm", "PM", time)
    return time

#Assuming a person's availabilities are written one after another with commas as separators
#This function also accounts for people who only are available at one time(Grrrrr)
def extract_times(text, sep = ","): # TODO
    if ',' not in text:
        times = [text]
    else:
        times = text.split(sep = ',')
    times = [standardize_time(time.strip()) for time in times]
    return times