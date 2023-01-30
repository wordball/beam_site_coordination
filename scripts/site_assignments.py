#---------------Site Leader Assignments-----------------#
from scripts.classes import *
""" 
Assume we have each site leader instance along with each potential site created.
We need to figure out which site leader goes to which site. Once this is figured out,
we can reduce the number of "potential sites" to the number of actual sites.

If we imagine each arrangement as a tree, we are simply creating branches where each branch
represents a decision made(aka assigning a person to a site). Using if-else statements, we
are able to ensure that certain conditions are met before assigning people to sites. This
reduces the amount of computation we need to do by eliminating possibilities which we know
won't work.
"""
# List of working site leader arrangements
# Will be populated with dataframes after running find_SL_arrangements
# Each dataframe represents a different permutation of people assigned to sites
working_SL_arrangements = []



""" The following "check" functions and other variables ensure that each site 
    meets the following requirements:
        1. The number of sites per location is between 1 and 3(inclusive)
        2. The number of non-site leaders who are also in staff is at most 1 per site
        3. The number of nonstaff decal members is either 2 or 3
        4. There is at least one driver per site.
"""

min_staff, max_staff = 0, 1
min_nonstaff, max_nonstaff = 2, 3
min_sites_per_location, max_sites_per_location = 1, 3

def check_num_SLs(min_SL = 1, max_SL = 4):
    above_or_equal_min = all([location.num_site_leaders() >= min_SL for location in locations.values()])
    below_or_equal_min = all([location.num_site_leaders() <= max_SL for location in locations.values()])
    return above_or_equal_min and below_or_equal_min

def check_num_staff_or_nonstaff(min_num, max_num, decal_type): #Assumes each site has a SL
    assert decal_type in ('staff', 'nonstaff'), 'Wrong string fed into decal_type argument'
    #Checks number of staff or number of nonstaff members
    if decal_type == 'staff':
        above_or_equal_min = all([site.num_nonstaff() >= min_num for site in times_to_sites.values()])
        below_or_equal_min = all([site.num_nonstaff() <= max_num for site in times_to_sites.values()])
    else:
        above_or_equal_min = all([site.num_staff() >= min_num for site in times_to_sites.values()])
        below_or_equal_min = all([site.num_staff() <= max_num for site in times_to_sites.values()])
    return above_or_equal_min and below_or_equal_min

def check_num_drivers():
    return all([site.has_driver for site in times_to_sites.values()])

def check_sites():
    correct_num_sites = check_num_SLs()
    correct_num_staff = check_num_staff_or_nonstaff(min_staff, max_staff, 'staff') 
    correct_num_nonstaff = check_num_staff_or_nonstaff(min_nonstaff, max_nonstaff, 'nonstaff')
    correct_num_drivers = check_num_drivers()
    return correct_num_sites and correct_num_drivers and correct_num_staff and correct_num_nonstaff

# Miscellaneous
from math import factorial
def calculate_total_arrangements():
    num_total_sites = len(times_to_sites.values())
    num_site_leaders = len(names_to_site_leaders.keys())
    print("Number of total sites: {}".format(num_total_sites))
    print("Number of site leaders: {}".format(num_site_leaders))
    return factorial(num_total_sites)/factorial(num_total_sites - num_site_leaders)


# Function Used to Display Arrangements in Pandas DataFrames
def initialize_df():
    columns = ['Day', 'Time', 'District', 'Site', 'Site Leader', \
        'Driver', 'Site Member 1', 'Site Member 2', 'Site Member 3', \
        'Site Member 4']
    index = [i for i in range(len(names_to_site_leaders.keys()))]
    df = pd.DataFrame(index = index, columns = columns)
    return df
    
    
def create_df():
    df = initialize_df()
    for i, sl in enumerate(names_to_site_leaders.values()):
        sl_name = sl.name
        df.loc[i, 'Site Leader'] = sl_name
        site = sl.assigned_site
        df.loc[i, 'Site'] = site.name
        df.loc[i, 'District'] = site.district
        day, time = site.time.strip().split()
        df.loc[i, 'Day'] = day
        df.loc[i, 'Time'] = time
        if site.has_driver:
            driver_name = site.get_driver_name()
            df.loc[i, 'Driver'] = driver_name
        if site.num_staff() == 2:
            non_SL_staff_name = site.get_non_SL_staff_name()
            df.loc[i, 'Site Member 1'] = non_SL_staff_name
        if site.num_nonstaff() > 1:
            nonstaff_names = site.get_nonstaff_names()
            for i in range(2, len(nonstaff_names) + 2):
                df.loc[i, 'Site Member ' + str(i)] = nonstaff_names[i-1]
    return df

# The "juicy meat" of the sandwich that are these python files...jk I wouldn't know since I'm vegetarian
# These hella basic functions find arrangements that fit site leaders' and other decal members' availabilities
# Instantation of the classes for each decal member(staff/nonstaff) and for each site is required before running these functions.
# It is also necessary to feed in lists ordered by people's availabilities(refer to function named 'order_by_availabilities')

#Count of running permutations of arrangements that are found
#This variable, along with max_SL_arrangements, is used to prevent the
#functions which find arrangements from running too long.
#Re-initialize to 0 every time you run any of the functions that use this variable
num_permutations = 0 
max_SL_arrangements = 10

def find_SL_arrangements(ordered_SL, assigned = []):
    if len(working_SL_arrangements) < max_SL_arrangements:
        if ordered_SL == []:
            if check_num_SLs(min_sites_per_location, max_sites_per_location):
                working_SL_arrangements.append(create_df())
        else:
            unassigned = [person for person in ordered_SL if person not in assigned]
            next_person = unassigned[0]
            for availability in next_person.availabilities:
                try:
                    for site in times_to_sites[availability]:
                        relevant_location = locations[site.name]
                        if not site.has_site_leader and relevant_location.num_site_leaders() + 1 <= max_sites_per_location:
                            site.add_member(next_person)
                            new_unassigned = [person for person in unassigned if person is not next_person]
                            find_SL_arrangements(new_unassigned, assigned + [next_person])
                            site.remove_member(next_person)
                except:
                    raise KeyError('Availability {} is not found in dictionary')

def find_staff_arrangements(ordered_staff, assigned = []): #refers to non-site leaders
    if ordered_staff == []:
        if check_num_staff_or_nonstaff(min_staff, max_staff, 'staff'):
            pass #FIXME
    else:
        unassigned = [person for person in ordered_staff if person not in assigned]
        next_person = unassigned[0]
        for availability in next_person.availabilities:
            try:
                for site in times_to_sites[availability]:
                    if site.num_staff() + 1 <= max_staff:
                        if next_person.drives and site.has_driver:
                            pass
                        else:
                            site.add_member(next_person)
                            new_unassigned = [person for person in unassigned if person is not next_person]
                            find_staff_arrangements(new_unassigned, assigned + [next_person])
                            site.remove_member(next_person)
            except:
                raise KeyError('Availability {} is not found in dictionary')
    
def find_nonstaff_arrangements(ordered_nonstaff, assigned = []):
    if ordered_nonstaff == []:
        if check_sites():
            pass #FIXME
    else:
        unassigned = [person for person in ordered_nonstaff if person not in assigned]
        next_person = unassigned[0]
        for availability in next_person.availabilities:
            try:
                for site in times_to_sites[availability]:
                    if site.num_nonstaff() + 1 <= max_nonstaff:
                        if next_person.drives and site.has_driver:
                            pass
                        else:
                            site.add_member(next_person)
                            new_unassigned = [person for person in unassigned if person is not next_person]
                            find_nonstaff_arrangements(new_unassigned, assigned + [next_person])
                            site.remove_member(next_person)
            except:
                raise KeyError('Availability {} is not found in dictionary')

def find_nonSL_arrangements(ordered, assigned = []):
    if ordered == []:
        if check_sites():
            pass #FIXME
    else:
        unassigned = [person for person in ordered if person not in assigned]
        next_person = unassigned[0]
        for availability in next_person.availabilities:
            try:
                for site in times_to_sites[availability]:
                    if next_person.in_staff:
                        if site.num_staff() + 1 <= max_staff:
                            if next_person.drives and site.has_driver:
                                pass
                            else:
                                site.add_member(next_person)
                                new_unassigned = [person for person in unassigned if person is not next_person]
                                find_nonSL_arrangements(new_unassigned, assigned + [next_person])
                                site.remove_member(next_person)
                    else:
                        if site.num_nonstaff() + 1 <= max_nonstaff:
                            if next_person.drives and site.has_driver:
                                pass
                            else:
                                site.add_member(next_person)
                                new_unassigned = [person for person in unassigned if person is not next_person]
                                find_nonSL_arrangements(new_unassigned, assigned + [next_person])
                                site.remove_member(next_person)
            except:
                raise KeyError('Availability {} is not found in dictionary')
