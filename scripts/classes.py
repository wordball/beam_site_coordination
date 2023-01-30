import pandas as pd
import re


# Classes for Locations and Sites
# Each school gets its own Location instance and multiple sites(one per time slot)

locations = {} #Maps names of the schools to each Location Instance
times_to_sites = {} #Maps times to a list of sites that operate at that time

class Location():
    def __init__(self, name, district, ideal_num_sites = None):
        self.name = name
        self.sites = []
        self.ideal_num_sites = ideal_num_sites
        self.district = district
        locations[name] = self
    def add_site(self, time):
        new_site = Site(self.name, time, self.district)
        self.sites.append(new_site)
    def num_sites(self):
        return len(self.sites)
    def num_site_leaders(self):
        return len([site for site in self.sites if site.has_site_leader])
    def num_full_sites(self): #is a site with 4 people considered full?, add a needs_more_people method()
        pass

class Site:
    def __init__(self, name, time, district):
        self.name = name #location name - aka Harding NOT Harding C
        self.time = time
        self.district = district
        self.members = [] #includes Site Leader
        self.has_site_leader = False
        self.has_driver = False
        if time in times_to_sites.keys():
            times_to_sites[time] += [self]
        else:
            times_to_sites[time] = [self]

    def add_member(self, person): #assumes that the member added is the right type
        self.members.append(person)
        person.assigned_site = self
        self.update_booleans()

    def remove_member(self, person):
        self.members.remove(person)
        person.assigned_site = None
        self.update_booleans()

    def num_staff(self):
        num_staff = len([member for member in self.members if member.in_staff])
        return num_staff

    def num_nonstaff(self):
        num_nonstaff = len([member for member in self.members if not member.in_staff])
        return num_nonstaff

    def update_booleans(self):
        self.has_site_leader = any([person for person in self.members if person.leads_site])
        self.has_driver = any([person for person in self.members if person.drives])
        
    def get_driver_name(self):
        return [person for person in self.members if person.drives][0].name

    def get_non_SL_staff_name(self):
        if self.num_staff() == 2:
            return [person for person in self.members \
                if person.in_staff and not person.leads_site][0]
    
    def get_nonstaff_names(self):
        return [member.name for member in self.members if not member.in_staff]
        
    def clear(self):
        self.members = []
        self.has_site_leader = False
        self.has_driver = False
        return self

def clear_all_sites(): #Used to "reset sites", Gets rid of all members from each site roster
    for time in times_to_sites.keys():
        times_to_sites[time] = [time.clear() for time in times_to_sites[time]]


# Classes for each person in decal
names_to_site_leaders = {} #Maps names of site leaders to their instances
names_to_staff_members = {} #Maps names of staff members who are NOT site leaders to their instances
names_to_nonstaff = {} #Maps names of nonstaff members to their instances
class DecalMember:
    def __init__(self, name, can_drive, availabilities =[]):
        self.name = name
        self.drives = can_drive
        self.in_staff = False
        self.leads_site = False
        self.availabilities = availabilities
        self.assigned_site = None
        self.add_to_record()
    def add_to_record(self):
        names_to_nonstaff[self.name] = self
    def add_availabilities(self, availabilities):
        assert type(availabilities) is dict
        self.availabilities.update(availabilities)

class StaffMember(DecalMember):
    def __init__(self, name, can_drive, availabilities=[]):
        super().__init__(name, can_drive, availabilities)
        self.in_staff = True
    def add_to_record(self):
        names_to_staff_members[self.name] = self

class SiteLeader(StaffMember):
    def __init__(self, name, can_drive, availabilities=[]):
        super().__init__(name, can_drive, availabilities)
        self.in_staff = True
        self.leads_site = True
    def add_to_record(self):
        names_to_site_leaders[self.name] = self


# Data Processing Functions
# Some of these functions hopefully won't be used if the google forms are standardized properly
import re
def standardize_time(time):
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
def extract_times(text, sep = ","):
    if ',' not in text:
        times = [text]
    else:
        times = text.split(sep = ',')
    times = [standardize_time(time.strip()) for time in times]
    return times

#Orders a list of decal people by how busy they are (most busy to least busy)
def order_by_availabilities(lst_of_people):
    ordered = sorted(lst_of_people, key = lambda x: len(x.availabilities))
    return ordered


