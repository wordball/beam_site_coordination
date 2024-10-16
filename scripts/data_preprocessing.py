# Written by Aditya Murali
import pandas as pd
from classes import *
from pathlib import Path
from datetime import datetime, timedelta
import calendar
import re



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

    return df


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
        day_and_time = df.loc[row, 'Day'] + ' ' + df.loc[row, 'Time']
        district.add_site(site_name, day_and_time)

    return df

def read_populated_site_map(df: pd.DataFrame) -> None:
    df = read_empty_site_map(df)

    # Exception messages to be used for later
    nonexistent_exception_msg = ("The {member_type} named {name} is on the "
                                 "site map but they did not fill out the "
                                 "google form.")
    validation_exception_msg = ("{name} has been assigned to "
                                "the {site_day} {site_name} site that "
                                "takes place from {site_time_slot}.\n"
                                "However, they are not available during this "
                                "time.")

    # Iterate through each site
    for row in df.index.tolist():
        site_name = df.loc[row, 'Site']
        site = names_to_sites[site_name]
        site_day = df.loc[row, 'Day']
        site_time_slot = df.loc[row, 'Time']

        # Check each member's name
        # See if their name exists in the dictionaries
        # Ensure that the site day/time is actually in the person's
        # availabilities
        sl_name = df.loc[row, 'Site Leader']
        if not pd.isnull(sl_name):
            if sl_name not in names_to_site_leaders.keys():
                raise Exception(nonexistent_exception_msg.format(
                    'site leader', sl_name))
            else:
                site_leader = names_to_site_leaders[sl_name]
                if site.validate_member(site_leader):
                        site.add_member(site_leader)
                else:
                    raise Exception(validation_exception_msg.format(
                        sl_name, site_day, site_name, site_time_slot))


        nonSL_staff_name = df.loc[row, 'Staff Member']
        if not pd.isnull(nonSL_staff_name):
            if nonSL_staff_name not in names_to_nonSL_staff_members.keys():
                raise Exception(nonexistent_exception_msg.format(
                    'staff member', nonSL_staff_name))
            else:
                staff_member = names_to_nonSL_staff_members[nonSL_staff_name]
                if site.validate_member(staff_member):
                    site.add_member(staff_member)
                else:
                    raise Exception(validation_exception_msg.format(
                        nonSL_staff_name, site_day, site_name, site_time_slot))


        decal_names = [df.loc[row, f'Decal Member {i}'] for i in
                       range(1, 5)]
        for decal_name in decal_names:
            if not pd.isnull(decal_name):
                if decal_name not in names_to_nonstaff.keys():
                    raise Exception(nonexistent_exception_msg.format(
                        'decal member', decal_name))
                else:
                    decal_member = names_to_nonstaff[decal_name]
                    if site.validate_member(decal_member):
                        site.add_member(decal_member)
                    else:
                        raise Exception(
                            validation_exception_msg.format(
                                decal_name, site_day, site_name,
                                site_time_slot))





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
                                                      'zip']]):
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

def extract_availabilities_from_string(availabilities: str) -> List[str]:
    availabilities = availabilities.replace('*', '')
    availabilities = convert_string_list_to_list_of_strings(availabilities)
    availabilities = [standardize_day_and_time(availability) for
                      availability in availabilities]
    return availabilities

def read_google_form_responses(df: pd.DataFrame,
                               person_class: Union[DecalMember,
                                                   StaffMember,
                                                   SiteLeader]) -> None:
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

    df = clean_google_form_responses(df)
    for row in df.index.tolist():

        # Read each attribute
        name = df.loc[row, 'name']

        availabilities = df.loc[row, 'availabilities']
        availabilities = extract_availabilities_from_string(availabilities)

        drives1 = df.loc[row, 'drives1']
        drives1 = convert_yes_no_to_bool(drives1)

        drives2 = df.loc[row, 'drives2']
        drives2 = convert_yes_no_to_bool(drives2)

        drives = drives1 or drives2

        last_tb_test = df.loc[row, 'last_tb_test']
        last_tb_test = convert_last_tb_test_to_int_years(last_tb_test)

        history = df.loc[row, 'history']
        history = convert_string_list_to_list_of_strings(history)

        speaks_spanish = df.loc[row, 'speaks_spanish']
        speaks_spanish - convert_yes_no_to_bool(speaks_spanish)
        new_person = person_class(name, availabilities, drives,
                                  last_tb_test=last_tb_test,
                                  history=history,
                                  speaks_spanish=speaks_spanish)

def convert_string_list_to_list_of_strings(string_list:str) -> List[str]:
    lst = string_list.split(', ')
    return lst

def convert_yes_no_to_bool(yes_or_no: str) -> bool:
    lowercase_no_spaces = yes_or_no.lower().strip()
    if lowercase_no_spaces == 'yes':
        return True
    elif lowercase_no_spaces == 'no':
        return False
    else:
        raise Exception("Expecting a yes/no as input. "
                        f"Got something else: {yes_or_no}")

def convert_last_tb_test_to_int_years(last_tb_test: str) -> int:
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
        create_site_arrangements(names_to_people.values(), mode))
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

