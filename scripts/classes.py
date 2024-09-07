import pandas as pd
import re
from typing import Optional, Dict, Tuple, List


times_to_sites = {} # Maps times to a list of sites that operate at that time
ids_to_sites = {} # Maps IDs to a list of sites
names_to_schools = {}

# Classes for each person in decal
# TODO: Are these dictionaries necessary.
# TODO: If not, delete all references to these dictionaries.
names_to_site_leaders = {} # Maps names of site leaders to their instances
names_to_nonSL_staff_members = {} # Maps names of staff members who are NOT site leaders to their instances
names_to_nonstaff = {} # Maps names of nonstaff members to their instances
names_to_people = {}


# Limits for number of people in staff and nonstaff
MIN_STAFF_PER_SITE = 1
MAX_STAFF_PER_SITE = 2
MIN_NONSTAFF_PER_SITE = 3
MAX_NONSTAFF_PER_SITE = 4
MIN_PEOPLE_PER_SITE = 4
MAX_PEOPLE_PER_SITE = 5



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

    def add_to_record(self): # TODO: Is this necessary?
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

    def add_to_record(self): # TODO: Is this necessary?
        names_to_nonSL_staff_members[self.name] = self

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

    def add_to_record(self): # TODO: is this necessary
        names_to_site_leaders[self.name] = self


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
        names_to_schools[name] = new_school
        return new_school

    def remove_school(self,
                      school):
        """
        Eliminates all sites contained within the School instance's sites list.
        Eliminates the name of the site and the Site object itself from the
        names_to_schools dictionary.
        """
        for site in school.sites:
            school.remove_site(site)
        names_to_schools.pop(school.name)
        self.schools.pop(school.name)



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
        add_to_times_to_sites(time, new_site)
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
        ids_to_sites.pop(site.id)
        remove_from_times_to_sites(site.time, site)
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

    def get_num_complete_sites(self) -> int:
        """
        Gets the number of sites that are considered 'complete'.

        Refer to the documentation under the Site class to understand
        what criteria needs to be fulfilled to consider a Site instance
        'complete'.

        Returns:
            int: number of sites considered 'complete'
        """
        return len([site for site in self.sites if site.is_complete])

class Site:
    def __init__(self,
                 name: str,
                 time: str,
                 school: School):
        """
        Refers to each site that teaches at a school.

        A 'complete' site has the following characteristics:
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
        self.is_complete = False
        self.assign_site_id()


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
        # TODO: Should I write the validate_member method as a descriptor thing
        # TODO: or as a completely different method entirely?

        self.members.append(person)
        person.assigned_site = self
        self.update_booleans()

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


        # Criteria for a complete site
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

                self.is_complete = True



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
        Returns the name of the driver
        # TODO: Will this be problematic if there is more than 1 driver?
        """
        return [person for person in self.members if person.drives][0].name

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
    for school_name in names_to_schools.key():
        school = names_to_schools[school_name]
        school.remove_all_sites()


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

    def unfreeze(self) -> None:
        """
        Takes the site assignments in self.site_assignments and
        actually assigns each DecalMember instance to their respective
        Site instance.

        Note that  'DecalMember instance' also refers to
        StaffMember and SiteLeader istances.

        Raises:
            Exception: _description_
        """
        clear_all_sites()
        for site_id in self.site_assignments.keys():
            site = ids_to_sites[site_id]
            member_names = self.site_assignments[site_id]
            people = [names_to_people[name] for name in member_names]
            for person in people:
                if site.validate_member(person):
                    site.add_member(person)
                else:
                    print(f"A site arrangement was made but {person.name} "
                          "was not validated.")
                    raise Exception("Issue with the unfreeze method!")

    def __str__(self):
        for id in self.site_assignments.keys():
            site = ids_to_sites[id]
            names = self.site_assignments[id]
            print(f"Site ID #{id}: {site.name}")
            print(f"People: {names}")


def create_priority_list(people) -> List[DecalMember]:
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
    for person in people:
        pass


def create_site_arrangements(people: List[DecalMember],
                             helper_list: List[SiteArrangement]):

    working_site_arrangements = helper_list
    priority_list = create_priority_list(people)
    for person in priority_list:
        pass



    return working_site_arrangements


def add_to_times_to_sites(time: str,
                          site: Site):
    if time not in times_to_sites.keys():
        times_to_sites[time] = [site]
    else:
        times_to_sites[time].append(site)

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