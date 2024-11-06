import pandas as pd
import re
from typing import Optional, Dict, Tuple, List, Union, Literal
import time
from typeguard import typechecked
import os
import logging


LOG_DIR = ("C:/Users/aditya/Desktop/my_projects/beam/site_leading"
           "/github_script/beam_site_coordination/scripts/logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG,
    filename=f"{LOG_DIR}/basic_functionality2.log",
    encoding="utf-8",
    filemode="a",
    format="{asctime} - {levelname} - {message}",
    style="{",
    datefmt="%Y-%m-%d %H:%M",
)
logging.debug("NEW EXECUTION")

# TODO: Updates 8/10/2024
# TODO: Block Diagram
# TODO: FREEZING + DATA PREPROCESSING
# TODO: Testing the code
# TODO: UI


# TODO: Try to find a way to log when you reach the end of the branch & then
# TODO: log the branch


times_to_sites = {} # Maps times to a list of sites that operate at that time
ids_to_sites = {} # Maps IDs to a list of sites
names_to_districts = {}
names_to_sites = {}

# Classes for each person in decal
# TODO: Are these dictionaries necessary?
# TODO: If not, delete all references to these dictionaries.
names_to_site_leaders = {}
names_to_nonSL_staff_members = {}
names_to_nonstaff = {}
names_to_people = {}


# Limits for number of people in staff and nonstaff
MIN_STAFF_PER_SITE = 1 # 1 site leader, no other staff members
MAX_STAFF_PER_SITE = 2 # 1 site leader and 1 other staff member
MIN_NONSTAFF_PER_SITE = 2 # 4 people; 1 SL, 1 other staff members
MAX_NONSTAFF_PER_SITE = 4 # 5 people; 1 SL, 0 other staff members
MIN_PEOPLE_PER_SITE = 4
MAX_PEOPLE_PER_SITE = 5

BUSY_THRESHOLD = 3



@typechecked
class DecalMember:
    def __init__(self,
                 name: str,
                 can_drive: bool,
                 availabilities: List[str] = [],
                 **kwargs):
        """
        Represents each person who is a part of decal but NOT staff.

        Args:
            name (str): name of the decal member
            can_drive (bool): boolean representing whether the decal member
                              can drive
            availabilities (List[str]): the list of times during which the
                                        decal member is available
        """
        self.name = name
        self.drives = can_drive
        self.in_staff = False
        self.leads_site = False
        self.availabilities = availabilities
        self.assigned_site = None
        for key in kwargs.keys():
            if key == 'history':
                self.history = kwargs[key]
            elif key == 'last_tb_test':
                self.last_tb_test = kwargs[key]
            elif key == 'speaks_spanish':
                self.speaks_spanish = kwargs[key]
            else:
                raise Exception("When creating an instance of the person "
                                f"named {name}, an incorrect attribute name "
                                f"was passed in: '{key}'")
        self.add_to_record()

    def add_to_record(self):
        """
        Adds a person to the record including to any relevant dictionaries.
        Keys are usually names. Values are the objects themselves.
        """
        names_to_people[self.name] = self
        names_to_nonstaff[self.name] = self

    def remove_from_record(self):
        names_to_people.pop(self.name)
        names_to_nonstaff.pop(self.name)
        if self.assigned_site is not None:
            self.assigned_site.remove_member(self)

    def add_availability(self,
                         availability: str):
        """
        Adds an availability to the list of availabilities.

        Args:
            availability (str):
        """
        self.availabilities.append(availability)

    def remove_availability(self,
                            availability: str):
        """
        Adds an availability to the list of availabilities.
        """
        self.availabilities.remove(availability)

    def find_potential_sites(self) -> List:
        """
        Gets a list of sites where the person can teach during the site time.

        Returns:
            List[Site]: list of sites
        """
        potential_sites = []

        # Iterate through each availability
        for availability in self.availabilities:

            # Get the list of sites that take place during that availability
            # If that availability is not on the list of sites, return an
            # empty list.
            site_list = times_to_sites.get(availability, [])
            potential_sites += site_list

        return potential_sites

    def __str__(self):
        description = (f"The decal member {self.name} has the following "
                       f"availabilities: {self.availabilities}.")
        if self.assigned_site is not None:
            description += (
                f"They are assigned to the site {self.assigned_site.name} "
                f"which takes place on {self.assigned_site.time}.")
        return description

@typechecked
class StaffMember(DecalMember):
    def __init__(self,
                 name: str,
                 can_drive: bool,
                 availabilities: List[str] = [],
                 **kwargs):
        """
        Represents each person who is a part of staff.

        Args:
            name (str): name of the staff member
            can_drive (bool): boolean representing whether the staff member
                              can drive
            availabilities (List[str]): the list of times during which the
                                        staff member is available
        """
        super().__init__(name, can_drive, availabilities, **kwargs)
        self.in_staff = True

    def add_to_record(self):
        names_to_people[self.name] = self
        names_to_nonSL_staff_members[self.name] = self

    def remove_from_record(self):
        names_to_people.pop(self.name)
        names_to_nonSL_staff_members.pop(self.name)
        if self.assigned_site is not None:
            self.assigned_site.remove_member(self)

    def __str__(self):
        standard_description = super().__str__()
        return standard_description.replace('decal member',
                                            'non-SL staff member')

@typechecked
class SiteLeader(StaffMember):
    def __init__(self,
                 name: str,
                 can_drive: bool,
                 availabilities: List[str] = [],
                 **kwargs):
        """
        Represents each person who is a part of staff and leads a site.
        Also referred to as a SL.

        Args:
            name (str): name of the SL
            can_drive (bool): boolean representing whether the SL
                              can drive
            availabilities (List[str]): the list of times during which the
                                        SL is available
        """
        super().__init__(name, can_drive, availabilities, **kwargs)
        self.in_staff = True
        self.leads_site = True

    def add_to_record(self):
        names_to_people[self.name] = self
        names_to_site_leaders[self.name] = self

    def remove_from_record(self):
        names_to_people.pop(self.name)
        names_to_site_leaders.pop(self.name)
        if self.assigned_site is not None:
            self.assigned_site.remove_member(self)

    def __str__(self):
        standard_description = super().__str__()
        return standard_description.replace('non-SL staff member',
                                            'site leader')


@typechecked
class District:
    """
    Represents school districts such as EBAYC, EBAC, Aspire, WCCUSD, etc.
    Mentors who teach at each of these districts may have to fulfill certain
    requirements. Those requirements will be hard-coded into the class.

    Args:
        name(str): Name of the district.

    """

    def __init__(self,
                 name:str):
        self.name = name
        self.sites = []
        self.add_to_record()

    def add_to_record(self):
        names_to_districts[self.name] = self

    def remove_from_record(self):
        names_to_districts.pop(self.name)

    def add_site(self,
                 name: str,
                 time: str):
        """
        Adds a site to the list of sites belonging to a District instance.

        Returns:
            new_site (Site): new Site instance
        """
        new_site = Site(name, time, self)
        self.sites.append(new_site)
        return new_site

    def remove_site(self,
                    site) -> None:
        """`
        Removes site from any sort of record or dictionary.
        Clears site of all members.
        Removes site id and site from the ids_to_sites dictionary
        Removes site time and site from the times_to_sites dictionary.
        Removes site from the self.sites list.

        Args:
            site (Site)

        Returns:
            None
        """
        site.clear()
        site.remove_from_record()
        self.sites.remove(site)

    def remove_all_sites(self):
        """
        Removes all sites
        """
        for site in self.sites[:]:
            self.remove_site(site)

    def get_num_sites(self) -> int:
        """
        Returns the number of sites.
        """
        return len(self.sites)

    def get_num_site_leaders(self) -> int:
        """
        Returns the number of sites with site leaders.
        """
        return len([site for site in self.sites if site.has_site_leader])

    def get_num_full_sites(self) -> int:
        """
        Gets the number of sites that are considered 'full'.

        Refer to the documentation under the Site class to understand
        what criteria needs to be fulfilled to consider a Site instance
        'full'.

        Returns:
            int: number of sites considered 'full'
        """
        return len([site for site in self.sites if site.is_full])


def add_district(name) -> District:
    """
    Creates a District instance

    Args:
        name (str): name of the district

    Returns:
        District: district object
    """
    new_district = District(name)
    return new_district

@typechecked
class Site:
    def __init__(self,
                 name: str,
                 time: str,
                 district: District):
        """
        Refers to each site that teaches at a school.

        A 'full' site has the following characteristics:
            - 4-5 people total, 1 of which is the Site Leader
            - 1-2 staff members including the Site Leader
            - At least 1 person who can drive per site

        Args:
            name (str): name of the site. E.g. Harding A, Harding B, etc.
                  This feature may be deleted # TODO
            time (str): the time at which this site takes place
            district (District): the district at which the site takes place

        """
        self.name = name
        self.time = time
        self.district = district
        self.members = []
        self.has_site_leader = False
        self.has_driver = False
        self.is_full = False
        self.add_to_record()

    def add_to_record(self):
        if self.name in names_to_sites.keys():
            raise Exception("There is more than one site with the same name: "
                            f"{self.name}")
        names_to_sites[self.name] = self
        add_to_times_to_sites(self.time, self)
        self.assign_site_id()

    def remove_from_record(self):
        ids_to_sites.pop(self.id)
        names_to_sites.pop(self.name)
        remove_from_times_to_sites(self.time, self)

    def assign_site_id(self):
        """
        Assigns a site id to the site. This is helpful when making
        SiteArrangement instances
        """
        self.id = len(ids_to_sites)
        ids_to_sites[self.id] = self


    def add_member(self,
                   person: DecalMember):
        """
        Adds a person to the site.
        Updates the person's assigned_site attribute
        Updates the booleans.

        Should be run in order to add a person.
        The person must be cleared before being added i.e. the site must be
        able to accomodate the person.

        Non-example: If Aditya is a site leader assigned to a site at
        Achieve Academy, then Jared shouldn't be able to be added to the site
        if he is a site leader.

        Args:
            person (DecalMember): can be an instance belonging to the
                                  DecalMember class or any of its
                                  descendant classes
        """

        if person.assigned_site is not None:
            raise Exception(f"You cannot add {person.name} to {self.name} "
                            "because they have already been added to "
                            f"{person.assigned_site.name}. You can only add "
                            "people who have not been assigned to a site yet.")
        self.members.append(person)
        person.assigned_site = self
        self.update_booleans()

    def score_person(self,
                     person:DecalMember) -> int:
        """
        Assumes that the validate_person method has been run already
        # TODO: Fix later once the script can actually generate working
        # TODO: SiteArrangement instances

        Args:
            person (DecalMember): _description_

        Returns:
            int: _description_
        """
        pass

    def validate_person(self,
                        person:DecalMember) -> bool:
        """
        Validates whether a person can or cannot join the site

        Instances when a person CANNOT join the site
        1. SL already present
        2. non_SL staff person already present
        3. 4 decal people in site --> cannot add anyone else (assuming
                                      SL is there)
        4. 3 decal people in site + 2 staff --> cannot add anyone else
        5. 4 people in site, no driver & we want to add someone who can't
           drive --> Don't add them

        Args:
            person (DecalMember): _description_
        """
        if self.time not in person.availabilities:
            print(f"Just double-checked {person.name}'s availabilities. "
                  f"Their availabilities don't match the site {self.name}")
            return False

        # Situation 1
        if self.has_site_leader and person.leads_site:
            return False

        # Situation 2
        if person.in_staff and not person.leads_site:
            if not self.has_site_leader:
                raise Exception("A SiteLeader has not been added to "
                                f"{self.name} yet. You cannot add a regular "
                                "StaffMember.")
            if self.get_num_staff() == MAX_STAFF_PER_SITE and person.in_staff:
                return False

        # Situations 3 and 4
        if self.get_num_people() == MAX_PEOPLE_PER_SITE:
            return False

        # Situation 5
        if (self.get_num_people() == MAX_PEOPLE_PER_SITE-1 and
              not self.has_driver and not person.drives):
            return False

        return True


    def remove_member(self,
                      person: DecalMember):
        """
        Removes a person from the site.
        Updates the person's assigned_site attribute
        Updates the booleans.
        """

        self.members.remove(person)
        person.assigned_site = None
        self.update_booleans()

    def get_num_staff(self) -> int:
        """
        Gets the number of people in the site who are part of staff.

        Returns:
            int
        """
        num_staff = len([
            member for member in self.members if member.in_staff])
        return num_staff

    def get_num_nonstaff(self):
        """
        Gets the number of people in the site who are NOT part of staff.

        Returns:
            int
        """
        num_nonstaff = len([
            member for member in self.members if not member.in_staff])
        return num_nonstaff

    def get_num_people(self) -> int:
        """
        Returns the number of people in the site. Should equal the same
        result as self.get_num_staff() + self.get_num_nonstaff()

        Returns:
            int: number of people in self.members
        """
        return len(self.members)

    def update_booleans(self):
        """
        Updates the self.has_site_leader and self.has_driver attributes.
        # TODO: Should this be a descriptor or something?
        """
        self.has_site_leader = any([
            person for person in self.members if person.leads_site])
        self.has_driver = any([
            person for person in self.members if person.drives])

        num_staff = self.get_num_staff()
        num_nonstaff = self.get_num_nonstaff()
        num_people = num_staff + num_nonstaff

        # self.is_full needs to be re-evaluated even if it stays the same.
        # Otherwise, the recursive process may deem a site as full when it
        # isn't due to a previous site arrangement

        self.is_full = (
            self.has_site_leader and
            self.has_driver and
            num_staff >= MIN_STAFF_PER_SITE and
            num_staff <= MAX_STAFF_PER_SITE and
            num_nonstaff >= MIN_NONSTAFF_PER_SITE and
            num_nonstaff <= MAX_NONSTAFF_PER_SITE and
            num_people >= MIN_PEOPLE_PER_SITE and
            num_people <= MAX_PEOPLE_PER_SITE)

    def get_num_drivers(self) -> int:
        """
        Gets the number of drivers in the site

        Returns:
            int: number of eligible drivers
        """
        return len([person for person in self.members if person.drives])


    def get_SL_name(self) -> str:
        """
        Assumes that the site actually has a site leader and returns the name
        of the SL.

        Returns:
            str: name of the SL assigned to the site.
        """
        return [person for person in self.members if person.leads_site][0].name

    def get_driver_names(self) -> List:
        """
        Returns the name of drivers ordered by seniority
        imo, the SiteLeader/StaffMember should ideally be the primary driver
        with the decal members being backup drivers.
        # TODO: Will this be problematic if there is more than 1 driver?
        """

        driver_names = []

        if self.has_site_leader:
            sl_name = self.get_SL_name()
            sl = names_to_site_leaders[sl_name]
            if sl.drives:
                driver_names.append(sl_name)

        if self.get_num_staff() == 2:
            non_SL_staff_name = self.get_non_SL_staff_name()
            non_SL_staff = names_to_nonSL_staff_members[non_SL_staff_name]
            if non_SL_staff.drives:
                driver_names.append(non_SL_staff_name)

        if self.get_num_nonstaff() > 0:
            nonstaff_names = self.get_nonstaff_names()
            nonstaff = [names_to_nonstaff[name] for name in nonstaff_names]
            driver_names.extend([person.name for person in nonstaff if
                                 person.drives])

        return driver_names

    def get_non_SL_staff_name(self) -> str:
        """
        Gets the name of the staff member in the site who is NOT the site
        leader.

        of course, not every site has two staff members (including the SL).
        As a result, it is imperative that the method get_num_staff is checked
        first before using the get_non_SL_staff_name method.
        """
        return [person.name for person in self.members
                if person.in_staff and not person.leads_site][0]

    def get_nonstaff_names(self) -> List[str]:
        """
        Returns the list of names referring to people within the site
        who are part of decal but not in staff.

        The list is sorted for the sake of comparing SiteArrangements
        which will end up calling this method after calling the freeze method.
        """
        return sorted(
            [member.name for member in self.members if not member.in_staff])

    def get_member_names(self) -> List[str]:
        """
        Returns:
            List[str]: list of the names of each member in self.members
        """
        member_names = []
        if self.has_site_leader:
            member_names.append(self.get_SL_name())
        if any([person for person in self.members if person.in_staff and
                not person.leads_site]):
            member_names.append(self.get_non_SL_staff_name())
        member_names.extend(self.get_nonstaff_names())
        return member_names

    def clear(self) -> None:
        """
        Sets the entire self.members list to an empty list.
        Reassigns each DecalMember's assigned_site attribute to None
        Updates booleans.
        """
        for member in self.members:
            member.assigned_site = None
        self.members = []
        self.update_booleans()


@typechecked
class SiteArrangement:
    def __init__(self):
        """
        Initializes a SiteArrangement which will store a "frozen"
        representation of each site and the people it contains.

        You can use dictionaries to relate the IDs of the sites and names of
        the people in the SiteArrangement to the Site instances and the
        DecalMember/StaffMember/SiteLeader instances, respectively.
        """
        self.site_assignments = {}

    def freeze(self) -> Dict[int, List[str]]:
        """
        Freezes the current configuration of sites and assigned people.
        Stores this information into the self.site_assignemnts dictionary
        """

        for time in times_to_sites.keys():
            sites = times_to_sites[time]
            for site in sites:
                self.site_assignments[site.id] = site.get_member_names()
        return self.site_assignments

    def unfreeze(self,
                 site_map: Optional[pd.DataFrame],
                 save_path: Optional[str],
                 eliminate: bool,
                 clear: bool) -> Optional[pd.DataFrame]:
        """
        Takes the site assignments in self.site_assignments and
        actually assigns each DecalMember instance to their respective
        Site instance.


        Note that  'DecalMember instance' also refers to
        StaffMember and SiteLeader istances.

        Args:
            save_path (Optional[str]): if path is None --> returns None
                if path is not None --> populate_site_map is called
            eliminate (bool): whether to call eliminate_everything function.
                              To be used usually if the site map is saved
                              to a path.
            clear (bool): whether to call clear_all_sites function.
                          To be used usually if the site map is saved
                          to a path.

        Raises:
            Exception: Given an issue with the unfreeze method or if
                       either the save apth or the site map is None/not None
                       but not both.

        Returns:
            None
        """
        assert check_all_sites_are_clear(), (
            "Unfreezing cannot take place until all sites are clear")

        if site_map is None:
            site_map = initialize_empty_site_map()

        for site_id in sorted(list(self.site_assignments.keys())):
            site = ids_to_sites[site_id]
            member_names = self.site_assignments[site_id]
            people = [names_to_people[name] for name in member_names]
            for person in people:
                if site.validate_person(person):
                    site.add_member(person)
                else:
                    print(f"A site arrangement was made but {person.name} "
                          "was not validated.")
                    raise Exception("Issue with the unfreeze method!")

        self.populate_site_map(site_map,
                               save_path)

        if eliminate:
            eliminate_everything()
        if clear:
            clear_all_sites()

    def populate_site_map(self,
                          site_map: pd.DataFrame,
                          save_path: Optional[str]) -> pd.DataFrame:
        """
        Populates a site map with times arranged in order of day
        and time.

        Args:
            save_path (str): Excel file path to save populated site map

        Returns:
            pd.DataFrame: _description_
        """
        if save_path is not None:
            if ".xlsx" not in save_path:
                raise Exception("The save path for the created site map "
                                f"'({save_path})' needs to be an excel file "
                                "path with the .xlsx extension")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)


        # Iterate through each time slot
        # The id will be used as the index when populating the site map
        for id, site in ids_to_sites.items():

            # Get the site name
            site_name = site.name
            site_map.loc[id, 'Site'] = site_name

            # Get the district name
            district_name = site.district.name
            site_map.loc[id, 'District'] = district_name

            # Get the day and time
            site_day, time_slot = get_day_and_time(site.time) # TODO: Ambiguous naming
            site_map.loc[id, 'Day'] = site_day
            site_map.loc[id, 'Time'] = time_slot

            # Get the SL name
            if site.has_site_leader:
                sl_name = site.get_SL_name()
                site_map.loc[id, 'Site Leader'] = sl_name

            # Get the driver's/drivers' name(s)
            if site.has_driver:
                driver_names = site.get_driver_names()
                site_map.loc[id, 'Driver(s)'] = ', '.join(driver_names)

            # Get the staff member name
            if site.get_num_staff() == 2:
                non_SL_staff_name = site.get_non_SL_staff_name()
                site_map.loc[id, 'Staff Member'] = non_SL_staff_name

            # Get the decal member names
            for j, nonstaff_name in enumerate(site.get_nonstaff_names()):
                site_map.loc[id, f'Decal Member {j+1}'] = nonstaff_name
            site_map.loc[id, 'Number of Mentors'] = len(site.members)

        # Save site map to an Excel file
        if save_path:
            if os.path.exists(save_path):
                os.remove(save_path)
            site_map.to_excel(save_path, index=False)
        return site_map


    def __str__(self):
        for id in self.site_assignments.keys():
            site = ids_to_sites[id]
            names = self.site_assignments[id]
            return (f"Site ID #{id}: {site.name}\nPeople: {names}")

@typechecked
def get_day_and_time(string_day_and_time:str) -> Tuple[str, str]:
    """
    Since the site times are obtained from the empty site map,
    the site times must have been standardized prior to using this
    function.

    Args:
        site_time (str): in the format of [Day] [Time Slot]

    Returns:
        day, time_slot (Tuple[str, str])
    """
    # Eliminate leading and trailing whitespace
    string_day_and_time = string_day_and_time.strip()

    # Split the day and time using regex
    match = re.match(r'([a-zA-Z]+)\s*(.+)', string_day_and_time)

    if not match:
        raise ValueError(f"Invalid format: {string_day_and_time}")

    day, time_slot = match.groups()
    return tuple([day, time_slot])


def clear_all_sites() -> None:
    """
    Clears all members from each site.
    Gets rid of all members from each site roster
    """
    for id in ids_to_sites.keys():
        site = ids_to_sites[id]
        site.clear()

def eliminate_all_sites() -> None:
    """
    Eliminates all sites from any dictionary or record.

    Returns:
        None
    """
    for district in names_to_districts.values():
        district.remove_all_sites()

def eliminate_all_districts() -> None:
    """
    Eliminates all districts and their sites from any dictionary or
    record.

    Returns:
        None
    """
    for district in list(names_to_districts.values()):
        district.remove_all_sites()
        district.remove_from_record()

def eliminate_all_people() -> None:
    """
    Eliminates all people and removes them from relevant dictionaries

    Raises:
        Exception: _description_

    Returns:
        None
    """
    people = list(names_to_people.values())
    for person in people:
        person.remove_from_record()

def eliminate_everything() -> None:
    eliminate_all_districts()
    eliminate_all_people()






@typechecked
def order_by_availabilities(people:List[DecalMember]) -> List[DecalMember]:
    """
    Orders people based on their availabilities

    Args:
        people (List[DecalMember]): list of DecalMembers

    Returns:
        List[DecalMember]: people ordered by increasing number of
                            availabilities
    """
    return sorted(people, key=lambda x: x.availabilities)

@typechecked
def create_priority_list(people:List[DecalMember]) -> List[DecalMember]:
    """
    Creates a list of people who are sorted based on their priority to be
    added into sites. This is done to minimize the amount of time creating
    incomplete/impossible site assignments.

    Recall that each SiteArrangement object is meant to contain site
    assignments that actually work.


    Args:
        people (_type_): _description_

    Returns:
        List[DecalMember]: _description_
    """

    @typechecked
    def order_group(group:List[DecalMember],
                    busy_threshold:int = BUSY_THRESHOLD) -> List[DecalMember]:
        """
        Orders the group based on the following priority:


        Priority is as follows:
            a. SiteLeaders, then staff, then decal
            b. 1-3 availabilities, drives, order by availabilities

        Args:
            group (List[DecalMember]): group of people belonging to one class
                e.g. site leaders only, non-SL staff people, decal people
            busy_threshold(int): refers to the max number of availabilities
                that would consider a person as 'busy' to be assigned to a
                site first. Initialized to 2
        """
        least_availabilities = order_by_availabilities(
            [person for person in group if len(
                person.availabilities) <= busy_threshold])
        remaining = [person for person in group if person not in
                 least_availabilities]

        drives = order_by_availabilities(
            [person for person in remaining if person.drives])

        remaining = order_by_availabilities(
            [person for person in remaining if person not in drives])

        return least_availabilities + drives + remaining

    sls_only = order_group(
        [person for person in people if person.leads_site])
    staff_no_SL = order_group(
        [person for person in people if person.in_staff and
         not person.leads_site])
    decal_no_staff = order_group(
        [person for person in people if not person.in_staff])

    return sls_only + staff_no_SL + decal_no_staff

@typechecked
def order_potential_sites(person: DecalMember,
                          sites: List[Site]) -> List[Site]:
    """
    If the person drives, we want all the sites without drivers to be in the
    front.

    We want the remaining sites to be ordered by number of people but
    secondarily by number of drivers.

    Order of priority for someone who drives:
    Primarily by number of drivers (INCREASING order) and secondarily by
    number of people (DECREASING order)

    Order of priority for someone who doesn't drive:
    Primarily by number of drivers (DECREASING order) and secondarily by
    number of people (INCREASING order)

    Args:
        person (DecalMember): _description_
        sites (List[Site]): _description_
    """

    if person.drives:
        return sorted(sites,
                      key = lambda site: (
                          site.get_num_drivers(),
                          MAX_PEOPLE_PER_SITE-site.get_num_people()))
    else:
        return sorted(sites,
                      key = lambda site: (
                          MAX_PEOPLE_PER_SITE-site.get_num_drivers(),
                          site.get_num_people()))

def check_all_sites_are_clear() -> bool:
    """
    Checks whether all sites are clear

    Returns:
        bool: whether sites are clear (aka no people in the members attribute
              and every person has an assigned_site attribute equal to None)
    """

    for site in ids_to_sites.values():
        if site.members != []:
            return False

    for person in names_to_people.values():
        if person.assigned_site is not None:
            return False

    return True


def check_all_sites_are_valid() -> bool:
    """
    Does not assume sites are full.

    Checks whether there are any errors with respect to the
    Site.validate_person instance method.

    Note that this should always return True.
    In the case that one of the cases is broken, then an exception will be
    raised.

    Returns:
        True

    Raises:
        Exception: in lieu of a boolean return value of False
    """
    # Get a list of all the sites
    all_sites = list(ids_to_sites.values())

    # Iterate through each site
    for site in all_sites:

        # Check number of site leaders added to the site
        site_leaders = [person for person in site.members if person.leads_site]
        if len(site_leaders) > 1:
            raise Exception("Too many site leaders added to the site\n"
                            f"Site Name: {site.name}. "
                            "Site Leaders: "
                            f"{[person.name for person in site_leaders]}")

        # Check number of non-SL staff people
        if site.get_num_staff() > MAX_STAFF_PER_SITE:
            nonSL_staff = [person.name for person in site.members if
                           person.in_staff and not person.leads_site]
            raise Exception(f"Site {site.name}[ID: {site.id}] has too many "
                            "staff people assigned. They include the "
                            f"following site leader {site.get_SL_name()} "
                            f"and other staff members {nonSL_staff}")

        # Check number of nonstaff people
        if site.get_num_nonstaff() > MAX_NONSTAFF_PER_SITE:
            raise Exception(f"Site {site.name}[ID: {site.id}] has too many "
                            f"decal members: {site.get_nonstaff_names()}")

        # Check number of people
        if site.get_num_people() > MAX_PEOPLE_PER_SITE:
            raise Exception(f"Site {site.name}[ID: {site.id}] is not valid.")
            # return False

        # Ensure each person can actually attend the site time
        for person in site.members:
            if site.time not in person.availabilities:
                raise Exception(f"{person.name} was added to {site.name} "
                                "but they can't make it.\nSite Time: "
                                f"{site.time}")

    return True

@typechecked
def check_all_sites_are_full() -> bool: #TODO: Establish whether this is truly necessary or whether this is just space being taken up within create_site_arrangements
    """
    Checks that all sites are full

    Returns:
        bool: True if all sites are full, False if any sites are not full
    """
    for site in list(ids_to_sites.values()):
        if not site.is_full:
            return False
    return True

def check_each_person_has_been_assigned() -> bool:
    """
    Checks if each person has been assigned to a site.

    Returns:
        bool
    """
    for person in list(names_to_people.values()):
        if person.assigned_site is None:
            return False
    return True


def check_if_each_person_has_more_than_one_availability() -> bool:
    no_availabilities = {'site leaders': [],
                         'non-SL staff members': [],
                         'decal members': []}

    # Add each person to the dictionary values
    for name, person in names_to_people.items():
        if len(person.availabilities) == 0:
            if type(person) == DecalMember:
                no_availabilities['decal members'].append(name)
            elif type(person) == StaffMember:
                no_availabilities['non-SL staff members'].append(name)
            else:
                no_availabilities['site leaders'].append(name)

    # Create the exception message
    exception_msg = (
        "The following people did not provide any availabilities: \n")
    for person_type, names in no_availabilities.items():
        exception_msg += f"{person_type}: {', '.join(names)}\n"

    if not sum([lst for lst in no_availabilities.values()], []) == []:
        raise Exception(exception_msg)

    return True

def check_for_optimal_number_of_people(
    mode: Literal['partial', 'full']) -> None:

    num_sites = len(names_to_sites)
    min_people_required = num_sites * MIN_PEOPLE_PER_SITE
    max_people_allowed = num_sites * MAX_PEOPLE_PER_SITE
    num_people = len(names_to_people)

    # Compare the number of people available
    num_people_message = (
        f"There are {num_sites} sites which means that there needs to be a "
        f"total of {min_people_required} to {max_people_allowed} people. "
        f"As of now, there are {num_people} people whose information was "
        "provided.")

    if num_people < min_people_required and mode == 'full':
        num_people_message = (
            "There are not enough people for each site!\n" +
            num_people_message)
        raise Exception(num_people_message)

    elif num_people > max_people_allowed:
        num_people_message = (
            "There are too many people!\n" +
            num_people_message)
        raise Exception(num_people_message)

    else:
        pass

    # Check each time in times_to_sites and perform the same comparison.
    num_people_available_msg = ""
    for day_and_time, site_list in times_to_sites.items():
        people = [person for person in names_to_people.values() if
                  day_and_time in person.availabilities]
        num_people_available = len(people)
        num_sites_during_time = len(site_list)
        min_people_required_during_time = (num_sites_during_time *
                                           MIN_PEOPLE_PER_SITE)
        max_people_allowed_during_time = (num_sites_during_time *
                                          MAX_PEOPLE_PER_SITE)

        if ((num_people_available < min_people_required_during_time and
             mode == 'full') or (num_people_available >
                                 max_people_allowed_during_time)):

            num_people_available_msg += (
                f"There are {num_sites_during_time} sites which take place on "
                f"{day_and_time}. This requires a total of "
                f"{min_people_required} to {max_people_allowed} people "
                f"available during this time. However, there are "
                f" {num_people} people who are available.\n")

    if num_people_available_msg != "":
        raise Exception(num_people_available_msg)


def check_for_optimal_number_of_SLs(mode: Literal['partial', 'full']) -> None:
    """
     Compare the number of site leaders to the number of sites
    """
    num_sites = len(names_to_sites)
    num_SLs = len(names_to_site_leaders)

    num_sl_message = (
        f"There are {num_sites} sites which means that there needs to be "
        f"exactly {num_sites} site leaders. As of now, there are "
        f"{num_SLs} site leaders whose information was provided.")

    if num_SLs < num_sites and mode == 'full':
        num_sl_message = (
            "There are not enough site leaders!\n" +
            num_sl_message)
        raise Exception(num_sl_message)

    elif num_SLs > num_sites:
        num_sl_message = (
            "There are too many site leaders!\n" +
            num_sl_message)
        raise Exception(num_sl_message)

    else:
        pass

    # Check each time in times_to_sites and perform the same comparison.
    num_SLs_available_msg = ""
    for day_and_time, site_list in times_to_sites.items():
        sls = [person for person in names_to_site_leaders.values() if
               day_and_time in person.availabilities]
        num_SLs_available = len(sls)
        num_sites_during_time = len(site_list) #num_SLs_needed = num_sites_during_time

        if ((num_SLs_available < num_sites_during_time and
             mode == 'full') or (num_SLs_available >
                                 num_sites_during_time)):
            num_SLs_available_msg += (
                f"There are {num_sites_during_time} sites which take place on "
                f"{day_and_time}. This requires exactly "
                f"{num_sites_during_time} people available during this time. "
                f"However, there are {num_SLs_available} people who are "
                "available.\n")

    if num_SLs_available_msg != "":
        raise Exception(num_SLs_available_msg)

def check_for_optimal_number_of_non_SLs(
    mode: Literal['partial', 'full']) -> None:
    """Compare the number of non site leaders to the number of sites"""

    num_sites = len(names_to_sites)
    num_non_SL = len(names_to_nonSL_staff_members) + len(names_to_nonstaff)
    min_non_SL_required = (MIN_PEOPLE_PER_SITE - 1) * num_sites
    max_non_SL_allowed = (MAX_PEOPLE_PER_SITE - 1) * num_sites

    num_nonSL_message = (
        f"There are {num_sites} sites which means that there needs to be a "
        f"total of {min_non_SL_required} to {max_non_SL_allowed} non site "
        "leaders (includes staff and nonstaff). As of now, there are "
        f"{num_non_SL} such people whose information was provided.")

    if num_non_SL < min_non_SL_required and mode == 'full':
        num_nonSL_message = (
            "There are not enough NON site leaders!\n" +
            num_nonSL_message)
        raise Exception(num_nonSL_message)

    elif num_non_SL > max_non_SL_allowed:
        num_nonSL_message = (
            "There are too many NON site leaders!\n" +
            num_nonSL_message)
        raise Exception(num_nonSL_message)

    else:
        pass

    # Check each time in times_to_sites and perform the same comparison.
    num_non_SLs_available_msg = ""
    num_non_SL_staff_available_msg = ""
    num_nonstaff_available_msg = ""

    # For people who are NOT site leaders
    for day_and_time, site_list in times_to_sites.items():

        non_SLs_staff_available = [person for person in
                                   names_to_nonSL_staff_members.values()
                                   if day_and_time in person.availabilities]
        nonstaff_available = [person for person in names_to_nonstaff.values()
                              if day_and_time in person.availabilities]
        non_SLs_available = non_SLs_staff_available + nonstaff_available

        num_non_SL_staff_available = len(non_SLs_staff_available)
        num_nonstaff_available = len(nonstaff_available)
        num_non_SLs_available = len(non_SLs_available)
        num_sites_during_time = len(site_list)

        # non-SL staff members + non-staff/decal members
        min_nonSL_required_during_time = (num_sites_during_time *
                                          (MIN_PEOPLE_PER_SITE - 1))
        max_nonSL_allowed_during_time = (num_sites_during_time *
                                         (MAX_PEOPLE_PER_SITE - 1))

        if ((num_non_SLs_available < min_nonSL_required_during_time and
             mode == 'full') or (num_non_SLs_available >
                                 max_nonSL_allowed_during_time)):
            num_non_SLs_available_msg += (
                f"There are {num_sites_during_time} sites which take place on "
                f"{day_and_time}. This requires a total of "
                f"{min_nonSL_required_during_time} to "
                f"{max_nonSL_allowed_during_time} non site leaders who are "
                f"available during this time. However, there are "
                f"{num_non_SLs_available} people who are available instead.\n")

        # non-SL staff specifically
        max_nonSL_staff_allowed_during_time = (num_sites_during_time *
                                               (MAX_STAFF_PER_SITE-1))
        if (num_non_SL_staff_available > max_nonSL_staff_allowed_during_time):
            num_non_SL_staff_available_msg += (
                "There are too many non-SL staff members who are available on "
                f"{day_and_time}.\n")
            num_non_SL_staff_available_msg += (
                f"There are {num_sites_during_time} sites which take place on "
                f"{day_and_time}. This allows a maximum of "
                f"{max_nonSL_staff_allowed_during_time} non-SL staff members "
                "who are available during this time. However, there are "
                f"{num_non_SLs_available} such people who are available.\n")



        # nonstaff/decal specifically
        min_nonstaff_required_during_time = (num_sites_during_time *
                                             MIN_NONSTAFF_PER_SITE)
        max_nonstaff_allowed_during_time = (num_sites_during_time *
                                            MAX_NONSTAFF_PER_SITE)

        if ((num_nonstaff_available < min_nonstaff_required_during_time and
            'mode' == 'full') or (num_nonstaff_available >
                                 max_nonstaff_allowed_during_time)):

            num_nonstaff_available_msg += (
                f"There are {num_sites_during_time} sites which take place on "
                f"{day_and_time}. This requires a total of "
                f"{min_nonstaff_required_during_time} to "
                f"{max_nonstaff_allowed_during_time} nonstaff/decal members "
                f"who are available during this time. However, there are "
                f"{num_nonstaff_available} such people who are available "
                "instead.\n")


    if num_non_SLs_available_msg != "":
        raise Exception(num_non_SLs_available_msg)

    if num_non_SL_staff_available_msg != "":
        raise Exception(num_non_SL_staff_available_msg)

    if num_nonstaff_available_msg != "":
        raise Exception(num_nonstaff_available_msg)



def check_for_edge_cases(mode: Literal['partial', 'full']) -> None:
    """
    Superficially checks whether there are enough decal members,
       staff members, and site leaders who are available during each time ->
       Done



    Args:
        people (_type_): _description_

    Raises:
        Exception:

    Returns:
        None
    """
    check_if_each_person_has_more_than_one_availability()
    check_for_optimal_number_of_people(mode)
    check_for_optimal_number_of_SLs(mode)
    check_for_optimal_number_of_non_SLs(mode)



@typechecked
def create_site_arrangements(
    people: List[DecalMember],
    mode: Literal['full', 'partial'],
    spaces:str="") -> List[SiteArrangement]:
    """
    Creates a list of SiteArrangement objects.

    Base Case(s)
    1. Full
        - not enough people/too many people -> []
        - just enough -> [SiteArrangement instance]
    2. Partial
        - not enough people/just enough -> [SiteArrangement instance]
        - too many people -> []

    Args:
        people (List[DecalMember]): all people involved
        mode (Literal['full', 'partial']): indicates one of the two modes
            'full':    All sites must be having a driver and the appropriate
                       number of each class that results in a total of 4-5
                       people
            'partial': All sites may have less than the max number per class
                       of people

    Returns:
        List[SiteArrangement]: _description_
    """

    check_for_edge_cases(mode)
    # Initialize an empty list of working site arrangements
    working_site_arrangements = []

    # Create a priority list for everyone who's not been assigned
    priority_list = create_priority_list(
        [person for person in people if person.assigned_site is None])

    # Base Case(s)
    # 'full' - each site is full, each person has been assigned
    # 'partial' - each person has been assigned

    # First check that all sites are valid
    try:
        check_all_sites_are_valid()

        if check_each_person_has_been_assigned():
            # If mode is full, sites must all be full
            logging.debug("-"*25)
            if mode == 'full':
                if check_all_sites_are_full():
                    new_site_arrangement = SiteArrangement()
                    new_site_arrangement.freeze()
                    print(f"Created a site arrangement.")
                    # logging.debug("Created a site arrangement")
                    # for name, site in names_to_sites.items():
                    #     logging.debug(f"{name} member(s): "
                    #                   f"{site.get_member_names()}")
                    return [new_site_arrangement]
                else:
                    return [] # do not raise an Exception here! Rmemeber the 3/5 situation
            else:
                new_site_arrangement = SiteArrangement()
                new_site_arrangement.freeze()
                # logging.debug("Created a site arrangement")
                # for name, site in names_to_sites.items():
                #     logging.debug(f"{name}'s {site.get_num_people()} "
                #                   f"member(s): {site.get_member_names()}")
                return [new_site_arrangement]

    except:
        raise Exception("There are one or more sites that are not valid!!!")


    # We will iterate through each person in the priority list BUT we do not
    # use a for loop since we don't want the order of the priority list to matter
    # Otherwise we'd get sites like A, Ak, E, M; A, Ak, M; A, Ak; ...
    next_unassigned_person = priority_list[0]

    # Get all the unassigned people
    all_potential_sites = next_unassigned_person.find_potential_sites()
    priority_sites = order_potential_sites(next_unassigned_person,
                                            all_potential_sites)

    # Iterate through the sites in order of priority
    for site in priority_sites:

        # Add the person
        if site.validate_person(next_unassigned_person):
            site.add_member(next_unassigned_person)
            # logging.debug(
            #     f"{spaces}Added {next_unassigned_person.name} to {site.name}")

            # Recursive Case
            # Create more site arrangements
            # Add them to the list of working_site_arrangements
            working_site_arrangements += create_site_arrangements(
                priority_list[1:], mode, spaces + "  ")

            # Remove the person from the site
            # Continue onwards to the next site in the list of priority_sites
            site.remove_member(next_unassigned_person)
            # logging.debug(
            #     f"{spaces}Removed {next_unassigned_person.name} from "
            #       f"{site.name}")

    # In the case that there are no people left and the sites are not valid,
    # an empty list will be returned.
    return working_site_arrangements

@typechecked
def add_to_times_to_sites(time: str,
                          site: Site):
    if time not in times_to_sites.keys():
        times_to_sites[time] = [site]
    else:
        times_to_sites[time].append(site)

@typechecked
def remove_from_times_to_sites(time: str,
                               site: Site):
    if time not in times_to_sites.keys():
        raise Exception(f"Time '{time}' is not in the "
                        "times_to_sites dictionary")
    else:
        sites = times_to_sites[time]
        if len(sites) == 1:
            times_to_sites.pop(time)
        else:
            times_to_sites[time].remove(site)



def initialize_empty_site_map() -> pd.DataFrame:
    """
    Returns:
        pd.DataFrame: empty site map
    """
    columns = (['Site', 'District', 'Day', 'Time', 'Site Leader',
               'Driver(s)', 'Staff Member'] +
               [f'Decal Member {i}' for i in range(1, 5)])
    df = pd.DataFrame(columns = columns)
    return df

def compare_two_pandas_values(val1, val2) -> bool:
    if (pd.isnull(val1) and not pd.isnull(val2) or (
        pd.isnull(val2) and not pd.isnull(val1))):
        return False
    elif pd.isnull(val1) and pd.isnull(val2):
        pass
    else:
        # TODO: FIX
        if val1 != val2:
            return False
    return True


@typechecked
def check_site_maps_are_equivalent(arg1: Union[pd.DataFrame, os.PathLike],
                                   arg2: Union[pd.DataFrame, os.PathLike]):
    assert type(arg1) == type(arg2), ("arg1 type != arg2 type\n"
                                      f"arg1 type: {type(arg1)}"
                                      f"arg2 type: {type(arg2)}")

    # Get the site map dataframe
    if type(arg1) == pd.DataFrame:
        df1, df2 = list(map(lambda x: pd.read_excel(x), [arg1, arg2]))
    else:
        df1, df2 = arg1, arg2

    # Check the values
    for row in df1.index.tolist():

        for col_name in ['Day',
                         'Time',
                         'Site Leader',
                         'Driver(s)',
                         'Staff Member',
                         'Decal Member 1',
                         'Decal Member 2',
                         'Decal Member 3',
                         'Decal Member 4',
                         'Number of Mentors']:
            val1, val2 = df1.loc[row, col_name], df2.loc[row, col_name]
            # if not compare_two_pandas_values(val1, val2):
            #     return False
            if pd.isnull(val1) and not pd.isnull(val2) or (
                pd.isnull(val2) and not pd.isnull(val1)):
                return False
            elif pd.isnull(val1) and pd.isnull(val2):
                pass
            else:
                # TODO: FIX
                if val1 != val2:
                    return False
    return True

