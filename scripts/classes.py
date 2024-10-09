import pandas as pd
import re
from typing import Optional, Dict, Tuple, List, Union, Literal
from data_preprocessing import initialize_empty_site_map
import time
from typeguard import typechecked


# TODO: Updates 8/10/2024
# TODO: Block Diagram
# TODO: FREEZING + DATA PREPROCESSING
# TODO: Testing the code
# TODO: UI


# TODO: Try to find a way to log when you reach the end of the branch & then
# TODO: log the branch


times_to_sites = {} # Maps times to a list of sites that operate at that time
ids_to_sites = {} # Maps IDs to a list of sites
names_to_schools = {}
names_to_districts = {}

# Classes for each person in decal
# TODO: Are these dictionaries necessary?
# TODO: If not, delete all references to these dictionaries.
names_to_site_leaders = {}
names_to_nonSL_staff_members = {}
names_to_nonstaff = {}
names_to_people = {}


# Limits for number of people in staff and nonstaff
MIN_STAFF_PER_SITE = 1
MAX_STAFF_PER_SITE = 2
MIN_NONSTAFF_PER_SITE = 3
MAX_NONSTAFF_PER_SITE = 4
MIN_PEOPLE_PER_SITE = 4
MAX_PEOPLE_PER_SITE = 5



@typechecked
class DecalMember:
    def __init__(self,
                 name: str,
                 can_drive: bool,
                 availabilities: List[str] = []):
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
        self.add_to_record()

    def add_to_record(self):
        names_to_people[self.name] = self
        names_to_nonstaff[self.name] = self


    def add_availability(self,
                         availability: str):
        """
        Adds an availability to the list of availabilities.
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
        Gets a list of sites where the person would be able to be added to the
        site.

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

@typechecked
class StaffMember(DecalMember):
    def __init__(self,
                 name: str,
                 can_drive: bool,
                 availabilities: List[str] = []):
        """
        Represents each person who is a part of staff.

        Args:
            name (str): name of the staff member
            can_drive (bool): boolean representing whether the staff member
                              can drive
            availabilities (List[str]): the list of times during which the
                                        staff member is available
        """
        super().__init__(name, can_drive, availabilities)
        self.in_staff = True

    def add_to_record(self):
        names_to_people[self.name] = self
        names_to_nonSL_staff_members[self.name] = self

@typechecked
class SiteLeader(StaffMember):
    def __init__(self,
                 name: str,
                 can_drive: bool,
                 availabilities: List[str] = []):
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
        super().__init__(name, can_drive, availabilities)
        self.in_staff = True
        self.leads_site = True

    def add_to_record(self):
        names_to_people[self.name] = self
        names_to_site_leaders[self.name] = self

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
        self.schools = {}
        self.add_to_record()

    def add_to_record(self):
        names_to_districts[self.name] = self

    def remove_from_record(self):
        names_to_districts.pop(self.name)

    def add_school(self,
                   name:str):
        """
        Args:
            name (str): Name of the school.

        Returns:
            new_school (School): new School instance
        """
        new_school = School(name, self)
        self.schools[name] = new_school
        return new_school

    def remove_school(self,
                      school):
        """
        Eliminates all sites contained within the School instance's sites list.
        Eliminates the name of the site and the Site object itself from the
        names_to_schools dictionary.
        """
        school.remove_all_sites()
        school.remove_from_record()
        self.schools.pop(school.name)

    def remove_all_schools(self):
        """
        Removes all schools
        """
        for school in self.schools:
            self.remove_school(school)


@typechecked
class School:
    def __init__(self,
                 name:str,
                 district:District):
        """
        Represents each school that BEAM teaches at. Note that the schools
        belongto certain districts. Each school may be assigned 1 or more
        sites. Examples of schools include Malcolm X Elementary, Washington
        Elementary, etc.

        Args:
            name (str): Name of the school
            district (District): the district that the school belongs to
        """

        self.name = name
        self.sites = []
        self.district = district
        self.add_to_record()

    def add_site(self,
                 name: str,
                 time: str):
        """
        Adds a site to the list of sites belonging to a School instance.

        Returns:
            new_site (Site): new Site instance
        """

        # TODO: Decide whether site_name will be used or not.
        # TODO: Ensure that the Site class definition accounts for the
        # TODO: presence or lack of a Site name
        new_site = Site(name, time, self.district)
        self.sites.append(new_site)
        return new_site

    def add_to_record(self):
        names_to_schools[self.name] = self

    def remove_from_record(self):
        names_to_schools.pop(self.name)

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
        for site in self.sites:
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

@typechecked
class Site:
    def __init__(self,
                 name: str,
                 time: str,
                 school: School):
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
            school (School): the school at which the site takes place

        """
        self.name = name #location name - aka Harding NOT Harding C
        self.time = time
        self.school = school
        self.members = []
        self.has_site_leader = False
        self.has_driver = False
        self.is_full = False
        self.assign_site_id()
        self.add_to_record()

    def add_to_record(self):
        add_to_times_to_sites(self.time, self)

    def remove_from_record(self):
        ids_to_sites.pop(self.id)
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
        # TODO: Should I write the validate_person method as a descriptor thing
        # TODO: or as a completely different method entirely?

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
        assert self.time in person.availabilities, (
            f"Just double-checked {person.name}'s availabilities. "
            f"Their availabilities don't match the site {self.name}"
        )
        # Situation 1
        if self.has_site_leader and person.leads_site:
            return False

        # Situation 2
        elif self.get_num_staff() == MAX_STAFF_PER_SITE and person.in_staff:
            return False

        # Situations 3 and 4
        elif self.get_num_people() == MAX_PEOPLE_PER_SITE:
            return False

        # Situation 5
        elif (self.get_num_people() == MAX_PEOPLE_PER_SITE-1 and
              not self.has_driver and not person.drives):
            return False

        else:
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


        # Criteria for a full site
        if (self.has_site_leader and
            self.has_driver):

            num_staff = self.get_num_staff()
            num_nonstaff = self.get_num_nonstaff()
            num_people = num_staff + num_nonstaff
            if (num_staff >= MIN_STAFF_PER_SITE and
                num_staff <= MAX_STAFF_PER_SITE and
                num_nonstaff >= MIN_NONSTAFF_PER_SITE and
                num_nonstaff <= MAX_NONSTAFF_PER_SITE and
                num_people >= MIN_PEOPLE_PER_SITE and
                num_people <= MAX_PEOPLE_PER_SITE):

                self.is_full = True

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

    def get_driver_name(self) -> str:
        """
        Returns the name of the driver.
        imo, the SiteLeader/StaffMember should ideally be the primary driver
        with the decal members being backup drivers.
        # TODO: Will this be problematic if there is more than 1 driver?
        """
        sl_name = self.get_SL_name()
        sl = names_to_site_leaders[sl_name]
        driver_found = False

        if sl.drives:
            return sl_name

        if self.get_num_staff() == 2:
            non_SL_staff_name = self.get_non_SL_staff_name()
            non_SL = names_to_nonSL_staff_members[non_SL_staff_name]
            if non_SL.drives:
                return non_SL_staff_name
            else:
                pass

        if not driver_found:
            nonstaff_names = self.get_nonstaff_names()
            nonstaff = [names_to_nonstaff[name] for name in nonstaff_names]
            return [person for person in nonstaff if person.drives][0]

    def get_non_SL_staff_name(self) -> str:
        """
        Gets the name of the staff member in the site who is NOT the site
        leader.

        of course, not every site has two staff members (including the SL).
        As a result, it is imperative that the method get_num_staff is checked
        first before using the get_non_SL_staff_name method.
        """
        return [person for person in self.members
                if person.in_staff and not person.leads_site][0]

    def get_nonstaff_names(self) -> List[str]:
        """
        Returns the list of names referring to people within the site
        who are part of decal but not in staff.
        """
        return [member.name for member in self.members if not member.in_staff]

    def get_member_names(self) -> List[str]:
        """
        Returns:
            List[str]: list of the names of each member in self.members
        """
        if self.get_num_staff() == 2:
            return [self.get_SL_name(),
                    self.get_non_SL_staff_name()] + self.get_nonstaff_names()
        elif self.get_num_staff() == 1:
            return [self.get_SL_name()] + self.get_nonstaff_names()
        else:
            return self.get_nonstaff_names()

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
        return self


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
                 empty_site_map: Optional[pd.DataFrame] = None,
                 save_path: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        Takes the site assignments in self.site_assignments and
        actually assigns each DecalMember instance to their respective
        Site instance.

        Note that  'DecalMember instance' also refers to
        StaffMember and SiteLeader istances.

        Args:
            save_path (Optional[str]): if path is None --> returns None
                if path is not None --> populate_site_map is called

        Raises:
            Exception: Given an issue with the unfreeze method or if
                       either the save apth or the site map is None/not None
                       but not both.

        Returns:
            None
        """
        assert check_all_sites_are_clear(), (
            "Unfreezing cannot take place until all sites are clear")

        if (save_path is None and empty_site_map is not None or
            save_path is not None and empty_site_map is None):
            raise Exception("Both the save path and the site map need to be "
                            "None or not None.")

        for site_id in self.site_assignments.keys():
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

        if save_path is not None:
            self.populate_site_map(empty_site_map,
                                   save_path)

    def populate_site_map(self,
                          site_map: pd.DataFrame,
                          save_path: str) -> pd.DataFrame:
        """
        Populates an empty site map with times arranged in order of day
        and time.

        Args:
            save_path (str): Excel file path to save populated site map

        Returns:
            pd.DataFrame: _description_
        """
        assert ".xlsx" in save_path, (
            "The path to save the file is not an Excel file")

        index = 0

        # Iterate through each time slot
        for site_time in times_to_sites.keys():
            sites = times_to_sites[site_time]

            # Iterate through each site
            for site in sites:

                # Get the site name
                site_name = site.name
                site_map.loc[index, 'Site'] = site_name

                # Get the school name
                school_name = site.school.name
                site_map.loc[index, 'School'] = school_name

                # Get the district name
                district_name = site.school.district.name
                site_map.loc[index, 'District'] = district_name

                # Get the day and time
                site_day, time_slot = get_day_and_time(site_time)
                site_map.loc[index, 'Day'] = site_day
                site_map.loc[index, 'Time'] = time_slot

                # Get the SL name
                sl_name = site.get_SL_name()
                site_map.loc[index, 'Site Leader'] = sl_name

                # Get the driver's/drivers' name(s)
                driver_names = site.get_driver_names()
                site_map.loc[index, 'Driver(s)'] = ', '.join(driver_names)

                # Get the staff member name
                if site.get_num_staff() == 2:
                    non_SL_staff_name = site.get_non_SL_staff_name()
                    site_map.loc[index, 'Staff Member'] = non_SL_staff_name

                # Get the decal member names
                for j, nonstaff_name in enumerate(site.get_nonstaff_names()):
                    site_map.loc[index, f'Decal Member {j+1}'] = nonstaff_name

                # Update the index
                index+=1

        # Save site map to an Excel file
        site_map.to_excel(save_path)

        return site_map


    def __str__(self):
        for id in self.site_assignments.keys():
            site = ids_to_sites[id]
            names = self.site_assignments[id]
            print(f"Site ID #{id}: {site.name}")
            print(f"People: {names}")

@typechecked
def get_day_and_time(site_time:str) -> Tuple[str, str]:
    """
    Since the site times are obtained from the empty site map,
    the site times must have been standardized prior to using this
    function.

    Args:
        site_time (str): in the format of [Day] [Time Slot]

    Returns:
        day, time_slot (Tuple[str, str])
    """
    # TODO
    pass


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
    for school in names_to_schools.values():
        school.remove_all_sites()

def eliminate_all_schools() -> None:
    """
    Eliminate all schools from any dictionary or record.

    Returns:
        None
    """
    for district in list(names_to_districts.values()):
        district.remove_all_schools()

def eliminate_all_districts() -> None:
    """
    Eliminates all districts and their schools/sites from any dictionary or
    record.

    Returns:
        None
    """
    for district in list(names_to_districts.values()):
        district.remove_all_schools()
        district.remove_from_record()






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
                    busy_threshold:int = 3) -> List[DecalMember]:
        """
        Orders the group based on the following priority:


        Priority is as follows:
            a. SiteLeaders, then staff, then decal
            b. 1-2 availabilities, drives, order by availabilities

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
            [person for person in group if person not in drives])

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

@typechecked
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

@typechecked
def check_all_sites_are_valid() -> bool:
    """
    Does not assume sites are full.

    Checks whether there are any errors with respect to the
    Site.validate_person instance method.

    Returns:
        True

    Raises:
        Exception: in lieu of a boolean return value of False
    """
    # Get a list of all the sites
    all_sites = list(ids_to_sites.values())

    # Iterate through each site
    for site in all_sites:

        # Check number of SLs
        if site.get_num_site_leaders() > 1:
            raise Exception(f"Site {site.name}[ID: {site.id}] is not valid.")
            # return False

        # Check number of non-SL staff people
        if site.get_num_staff() > MAX_STAFF_PER_SITE:
            raise Exception(f"Site {site.name}[ID: {site.id}] is not valid.")
            # return False

        # Check number of nonstaff people
        if site.get_num_nonstaff() > MAX_NONSTAFF_PER_SITE:
            raise Exception(f"Site {site.name}[ID: {site.id}] is not valid.")
            # return False

        # Check number of people
        if site.get_num_people() > MAX_PEOPLE_PER_SITE:
            raise Exception(f"Site {site.name}[ID: {site.id}] is not valid.")
            # return False

    return True

@typechecked
def check_all_sites_are_full() -> bool:
    """
    Checks that all sites are full

    Returns:
        bool: True if all sites are full, False if any sites are not full
    """
    for site in list(ids_to_sites.values()):
        if not site.is_full:
            return False
    return True

@typechecked
def create_site_arrangements(
    people: List[DecalMember],
    mode: Literal['full', 'partial']) -> List[SiteArrangement]:
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
        people (List[DecalMember]): _description_
        mode (Literal['full', 'partial']): indicates one of the two modes
            'full':    All sites must be having a driver and the appropriate
                       number of each class that results in a total of 4-5
                       people
            'partial': All sites may have less than the max number per class
                       of people

    Returns:
        List[SiteArrangement]: _description_
    """

    assert all([person.assigned_site is None for person in people])

    # Record start time
    start_time = time.time()

    # Initialize an empty list of working site arrangements
    working_site_arrangements = []

    # Create a priority list for everyone who's not been assigned
    priority_list = create_priority_list(
        [person for person in people if person.assigned_site is None])

    # Base Case(s)

    # First check that all sites are valid
    if check_all_sites_are_valid():

        # If mode is full, sites must all be full
        if mode == 'full':
            if check_all_sites_are_full():
                new_site_arrangement = SiteArrangement()
                new_site_arrangement.freeze()
                return [new_site_arrangement]
            else:
                return []
        else:
            return [new_site_arrangement]


    # Iterate through each person in the priority list
    for person in priority_list:

        # Get all the unassigned people
        all_potential_sites = person.find_potential_sites()
        priority_sites = order_potential_sites(person,
                                                all_potential_sites)

        # Iterate through each sites in order of priority
        for site in priority_sites:

            # Add the person
            site.add_member(person)

            # Recursive Case
            # Create more site arrangements
            # Add them to the list of working_site_arrangements
            working_site_arrangements += create_site_arrangements(people)

            # Remove the person from the site
            # Continue onwards to the next site in the list of priority_sites
            site.remove_member(person)

    # Record the amount of time and how many working site arrangements
    # are created
    elapsed = time.time() - start_time
    elapsed_mins = elapsed // 60
    elapsed_sec = (elapsed % 60) // 1
    print(f"Creating {len(working_site_arrangements)} site arrangements "
          f"took {elapsed_mins} minutes and {elapsed_sec} seconds.")

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