import sys
import pandas as pd # type: ignore  <-- Ignores warnings
import os
from pathlib import Path
from typing import List
import numpy as np # type: ignore
from data_preprocessing import *
from classes import *
from pulp import *
import random

ROOT = Path('C:/Users/aditya/Desktop/my_projects/beam/site_leading/github_script/beam_site_coordination/scripts')
if ROOT not in sys.path:
    sys.path.append(str(ROOT))

def get_value(x, i, j):
    value_at_index = value(x[i, j])
    if value_at_index is not None: # variable value has been determined
        return int(value_at_index)
    return value_at_index

def save_solution(x: dict[LpVariable],
                  existing_solutions: List[dict]):
    solution_dictionary = {}
    for (i, j) in x:
        solution_dictionary[(i, j)] = get_value(x, i, j)
    existing_solutions.append(solution_dictionary)


def establish_appropriate_dictioonaries_for_person_class(person_class):
    dictionary_mappings = {
        SiteLeader: names_to_site_leaders,
        StaffMember: names_to_nonSL_staff_members,
        DecalMember: names_to_nonstaff}

    names_to_specific_people = dictionary_mappings[person_class]
    ids_to_specific_people = {}
    for i, (_, person) in enumerate(names_to_specific_people.items()):
        ids_to_specific_people[i] = person
    return names_to_specific_people, ids_to_specific_people


def establish_known_values(ids_to_specific_people):
    # Creating vectors corresponding to whether a person is available during each site
    known_zeros, known_ones = [], []
    for person_id in ids_to_specific_people:
        person = ids_to_specific_people[person_id]
        assigned_site = person.assigned_site
        if assigned_site is not None:
            # print(f"{person.name} was assigned to {site.name}({site.time})")
            known_ones.append((site.id, person_id))
        else:
            for site_id in ids_to_sites:
                site = ids_to_sites[site_id]
                if not site.validate_person(person):
                    if site.time in person.availabilities:
                        # print(person.name + " | " + site.name)
                        raise Exception("AHHH")
                    known_zeros.append((site_id, person_id))
    return known_zeros, known_ones


def convert_results_to_dataframe(solutions_dictionaries: List[dict],
                                 ids_to_sites,
                                 ids_to_specific_people):
    df = pd.DataFrame(index=[site.name for site in ids_to_sites.values()],
                      columns=list(range(len(solutions_dictionaries))))
    for solution_index, dictionary in enumerate(solutions_dictionaries):
        for i in range(len(ids_to_sites)): #instead of range(rows)
            people_names = []
            site = ids_to_sites[i]
            for j in range(len(ids_to_specific_people)): #instead of range(cols)
                if dictionary[(i, j)] == 1:
                    person = ids_to_specific_people[j]
                    if not site.validate_person(person):
                        raise Exception(f"{site.name}({site.time}) cannot validate {person.name}")
                    else:
                        # print(site.name, "|", person.name, "|", site.time)
                        people_names.append(person.name)
            df.loc[site.name, solution_index] = ', '.join(people_names)
    return df

def create_save_directory(person_class) -> Path:
    save_dir = Path(os.getcwd()) / person_class.__name__
    os.makedirs(str(save_dir), exist_ok=True)
    return save_dir

def initial_read(site_map,
                 site_leaders,
                 staff_members,
                 decal_members,
                 time_tolerance):
    sm = read_empty_site_map(site_map)
    person_class = None
    people_and_dfs = dict(zip([SiteLeader, StaffMember, DecalMember],
                              [site_leaders, staff_members, decal_members]))
    for p_class, df in people_and_dfs.items():
        if df is not None:
            people_and_dfs[p_class] = read_google_form_responses(
                df, p_class, time_tolerance, True)
            person_class = p_class
    if person_class != SiteLeader:
        sm = read_populated_site_map(site_map)
    helpful_basic_function('partial')


def master_func(person_class,
                num_trials):


    prob = LpProblem("Matrix_Problem", LpMaximize)
    solutions = []
    names_to_specific_people, ids_to_specific_people = (
        establish_appropriate_dictioonaries_for_person_class(person_class))
    rows = len(ids_to_sites) # Each site
    print(f"Number of sites: {rows}")
    cols = len(names_to_specific_people) # Each person
    print(f"Number of people: {cols}")


    # Create a binary dictionary of variables identified by site and person id
    known_zeros, known_ones = establish_known_values(ids_to_specific_people)
    x = LpVariable.dicts("x",
                        [(i, j) for i in range(rows) for j in range(cols) if (i, j) not in known_zeros],
                        cat='Binary')

    # Set known zeros (aka times when people are busy)
    for i, j in known_zeros:
        x[i, j] = 0

    # Set known ones (for people who are already assigned to sites)
    for i, j in known_ones:
        x[i, j] = 1

    # For each site, you can only have a max of 1 SL/non-SL staff member
    for i in range(rows):
        if person_class != DecalMember:
            prob += lpSum(x[i, j] for j in range(cols)) <= 1
        else:
            site = ids_to_sites[i]

            current_num_people_in_site = site.get_num_people()
            min_limit = MIN_PEOPLE_PER_SITE - current_num_people_in_site
            max_limit = MAX_PEOPLE_PER_SITE - current_num_people_in_site

            prob += lpSum(x[i, j] for j in range(cols)) >= min_limit
            prob += lpSum(x[i, j] for j in range(cols)) <= max_limit

            if site.get_num_drivers() == 0:
                prob += lpSum(x[i, j] for j in range(cols) if
                              ids_to_specific_people[j].drives) >= 1

    # For each person, they must be assigned to one site
    for j in range(cols):
        prob += lpSum(x[i, j] for i in range(rows)) == 1

    # Execute
    for _ in range(num_trials):
        if solutions:
            other_sol = solutions[-1]
            prob += lpSum(x[i, j] for i in range(rows) for j in range(cols)
                        if other_sol[(i, j)] == 1) <= \
                    lpSum(x[i, j] for i in range(rows) for j in range(cols)) - 1

        prob.solve(PULP_CBC_CMD(msg=False))
        print("Status:", LpStatus[prob.status])

        # Save solutions
        if LpStatus[prob.status] != 'Infeasible':
            save_solution(x, solutions)

    if not solutions:
        raise Exception("Did not generate any solutions")
    print(f"Generated {len(solutions)} solutions!")

    solutions_dataframe = convert_results_to_dataframe(solutions,
                                                       ids_to_sites,
                                                       ids_to_specific_people)
    save_dir = create_save_directory(person_class)
    solutions_dataframe.to_excel(str(save_dir / f"solutions.xlsx"))


    generated_site_maps = []
    for solution_index in range(len(solutions_dataframe.columns)):
        all_people = []
        for site_name in solutions_dataframe.index.tolist():
            site = names_to_sites[site_name]
            df_names = solutions_dataframe.loc[site_name, solution_index]
            if df_names:
                names_list = df_names.split(', ')
                people = [names_to_specific_people[name] for name in names_list]
                for person in people:
                    if site.validate_person(person):
                        site.add_member(person)
                    else:
                        raise Exception(f"Cannot validate {person.name} for {site.name} ({site.time})")
                all_people.extend(people)


        sa = SiteArrangement()
        sa.freeze()
        new_site_map = sa.populate_site_map(
            initialize_empty_site_map(),
            # str(save_dir / f"{solution_index}.xlsx")
            None
            )
        generated_site_maps.append(new_site_map)


        for person in all_people:
            site = person.assigned_site
            site.remove_member(person)
    print("Done with master_func")
    return generated_site_maps

existing_solutions = []

