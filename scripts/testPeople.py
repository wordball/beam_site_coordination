import unittest
from classes import *
from data_preprocessing import (extract_availabilities_from_string,
                                standardize_day_and_time)
import sys
from pathlib import Path
import os
import random



ROOT = Path('C:/Users/aditya/Desktop/my_projects/beam'
                '/site_leading/github_script/beam_site_coordination')
if not os.path.exists(str(ROOT)):
    raise Exception("The path of ROOT needs to be established first.")


@unittest.skip(reason="idk")
class TestDecalMember(unittest.TestCase):

    def test_decal_member_initialization(self):
        """
        Initialize a DecalMember.
        1. Check name attribute
        2. Check drives attribute
        3. Check availabilities attribute
        4. Check assigned_site attribute
        5. Check in_staff attribute
        6. Check leads_site attribute
        """
        member = DecalMember(name="Alice",
                             can_drive=True,
                             availabilities=["Monday", "Wednesday"])
        self.assertEqual(member.name, "Alice")
        self.assertTrue(member.drives)
        self.assertEqual(member.availabilities, ["Monday", "Wednesday"])
        self.assertIsNone(member.assigned_site)
        self.assertFalse(member.in_staff)
        self.assertFalse(member.leads_site)
        member.remove_from_record()

    def test_decal_member_add_availability(self):
        """
        Check whether adding an availability will show up in availabilities
        attribute

        """
        member = DecalMember(name="Alice", can_drive=True)
        member.add_availability("Friday")
        self.assertIn("Friday", member.availabilities)
        member.remove_from_record()

    def test_decal_member_remove_availability(self):
        """
        Check whether removing an availability will remove it from
        availabilities attribute

        """
        member = DecalMember(name="Alice",
                             can_drive=True,
                             availabilities=["Monday", "Wednesday"])
        member.remove_availability("Monday")
        self.assertNotIn("Monday", member.availabilities)
        member.remove_from_record()

@unittest.skip(reason="idk")
class TestStaffMember(unittest.TestCase):

    def test_staff_member_initialization(self):
        """
        Initialize a StaffMember.
        1. Check name attribute
        2. Check drives attribute
        3. Check availabilities attribute
        4. Check assigned_site attribute
        5. Check in_staff attribute
        6. Check leads_site attribute
        """
        staff = StaffMember(name="Bob", can_drive=False)
        self.assertEqual(staff.name, "Bob")
        self.assertFalse(staff.drives)
        self.assertListEqual(staff.availabilities, [])
        self.assertIsNone(staff.assigned_site)
        self.assertTrue(staff.in_staff)
        self.assertFalse(staff.leads_site)
        staff.remove_from_record()


@unittest.skip(reason="idk")
class TestSiteLeader(unittest.TestCase):

    def test_site_leader_initialization(self):
        """
        Initialize a SiteLeader.
        1. Check name attribute
        2. Check drives attribute
        3. Check availabilities attribute
        4. Check assigned_site attribute
        5. Check in_staff attribute
        6. Check leads_site attribute
        # TODO
        """
        sl = SiteLeader(name="Charlie", can_drive=True)
        self.assertEqual(sl.name, "Charlie")
        self.assertTrue(sl.drives)
        self.assertTrue(sl.in_staff)
        self.assertTrue(sl.leads_site)
        sl.remove_from_record()

@unittest.skip(reason="idk")
class TestDistrict(unittest.TestCase):
    def test_get_num_sites(self):
        district = District(name="BUSD")
        time_slot = standardize_day_and_time("Wednesday 9AM - 10AM")
        time_slot2 = standardize_day_and_time("Wednesday 10AM - 11AM")
        district.add_site("MX A", time=time_slot)
        district.add_site("MX B", time=time_slot2)
        self.assertEqual(district.get_num_sites(), 2)
        eliminate_all_districts()

    def test_get_num_site_leaders(self): #FIXME cna we make the time_slots as class variables
        district = District(name="BUSD")
        time_slot = standardize_day_and_time("Wednesday 9AM - 10AM")
        time_slot2 = standardize_day_and_time("Wednesday 10AM - 11AM")
        site1 = district.add_site("MX A", time=time_slot)
        site2 = district.add_site("MX B", time=time_slot2)
        sl = SiteLeader(name="Charlie", can_drive=True)
        site1.add_member(sl)
        self.assertEqual(district.get_num_site_leaders(), 1)
        eliminate_everything()

@unittest.skip("huh")
class TestSite(unittest.TestCase):

    def test_add_site(self):
        """
        Check the following:
        1. Site instance
            - name
            - time
        """
        district = District(name="WCCUSD")
        time_slot = standardize_day_and_time("Wednesday 9AM - 10AM")
        site = district.add_site(name="Harding A", time=time_slot)
        self.assertEqual(site.name, "Harding A")
        self.assertEqual(site.time, time_slot)
        self.assertEqual(site.district, district)
        eliminate_all_districts()

    def test_add_member(self):
        """
        Check member.assigned_site and site.members
        """
        district = District(name="WCCUSD")
        time_slot = standardize_day_and_time("Wednesday 10AM - 11AM")
        site = district.add_site(name="Harding A", time=time_slot)
        member = DecalMember(name="Alice", can_drive=True)
        site.add_member(member)
        self.assertIn(member, site.members)
        self.assertEqual(member.assigned_site, site)
        eliminate_everything()

    def test_clear_site(self):
        """
        Checks each assigned person's assigned_site attribute
        and the site.members list
        # TODO
        """
        pass

    def test_validate_person(self):
        district = District(name="WCCUSD")
        time_slot = standardize_day_and_time("Wednesday 10AM - 11AM")
        site = district.add_site(name="Harding A", time=time_slot)

        sl = SiteLeader(name="Charlie",
                        can_drive=True,
                        availabilities=[time_slot])
        staff = StaffMember(name="Bob",
                            can_drive=False,
                            availabilities=[time_slot])
        decal1 = DecalMember(name="Alice",
                             can_drive=True,
                             availabilities=[time_slot])
        decal2 = DecalMember(name="David",
                             can_drive=False,
                             availabilities=[time_slot])
        decal3 = DecalMember(name="Marshall Mathers",
                             can_drive=True,
                             availabilities=[time_slot])

        self.assertTrue(site.validate_person(sl))
        site.add_member(sl)
        self.assertFalse(site.validate_person(
            SiteLeader(name="Eve",
                       can_drive=True,
                       availabilities=[time_slot])))

        self.assertTrue(site.validate_person(staff))
        site.add_member(staff)
        self.assertFalse(site.validate_person(
            StaffMember(name="Frank",
                        can_drive=True,
                        availabilities=[time_slot])))

        self.assertTrue(site.validate_person(decal1))
        site.add_member(decal1)
        self.assertTrue(site.validate_person(decal2))
        site.add_member(decal2)
        self.assertTrue(site.validate_person(decal3))
        site.add_member(decal3)
        self.assertFalse(site.validate_person(
            DecalMember(name="Grace",
                        can_drive=True,
                        availabilities=[time_slot])))
        eliminate_everything()

    def test_update_booleans(self):
        district = District(name="WCCUSD")
        time_slot = standardize_day_and_time("Wednesday 10AM - 11AM")
        site = district.add_site(name="Harding A", time=time_slot)

        sl = SiteLeader(name="Charlie",
                        can_drive=True,
                        availabilities=[time_slot])
        decal = DecalMember(name="Alice",
                            can_drive=False,
                            availabilities=[time_slot])

        site.add_member(sl)
        site.update_booleans()
        self.assertTrue(site.has_site_leader)
        self.assertTrue(site.has_driver)
        self.assertFalse(site.is_full)

        site.add_member(decal)
        site.update_booleans()
        self.assertFalse(site.is_full)
        eliminate_everything()



# @unittest.skip(reason="idk")
class TestSiteArrangement(unittest.TestCase):
    def test_freeze_and_unfreeze(self):
        common_time = standardize_day_and_time("Monday 9AM - 10AM")


        district = District(name="BUSD")
        site = district.add_site(name="MX A",
                               time=common_time)

        # Create a DecalMember object
        member = DecalMember(name="Alice", can_drive=True,
                             availabilities=[common_time])
        site.add_member(member)

        # Freeze
        arrangement = SiteArrangement()
        frozen = arrangement.freeze()
        self.assertIn(site.id, frozen)
        self.assertIn(member.name, frozen[site.id])

        # Clear all sites before unfreezing
        clear_all_sites()
        self.assertIsNone(member.assigned_site)
        self.assertListEqual([], site.members)

        # Unfreeze
        arrangement.unfreeze()
        self.assertEqual(member.assigned_site, site)
        self.assertIn(member, site.members)
        eliminate_everything()

    def test_create_priority_list(self):
        """
        Create priority lists.
        1-2 availabilities, drives, 3-5 availabilities
        Scrambled decal members, staff members, and site leaders
        """
        one_availability = ["2:00 PM"]
        three_availabilities = ["2:00 PM", "3:00 PM", "4:00 PM"]
        more_than_three = three_availabilities + ["1:00 PM", "4:30 PM",
                                                  "6:30 PM"]
        way_more_than_three = more_than_three + ["8:00 PM"]
        max_availabilities = more_than_three + ["10:00 PM"]

        all_availabilities = [one_availability, three_availabilities,
                              more_than_three, way_more_than_three,
                              max_availabilities]


        sl_names = ["Aditya", "Surabhi", "Jared", "Andrew", "Kaitlyn"]
        staff_names = ["Bradley", "Sunay", "Gaby", "Akshara", "Shlok"]
        decal_names = ["Nilasha", "Sara", "Ethan", "Aaron", "Melody"]

        sls = [SiteLeader(name, False, availability) for
               name, availability in list(zip(sl_names, all_availabilities))]
        nonSL_staff = [
            StaffMember(name, False, availability) for
            name, availability in list(zip(staff_names, all_availabilities))]
        nonstaff = [
            DecalMember(name, False, availability) for
            name, availability in list(zip(decal_names, all_availabilities))]

        for ind in [1, 3]:
            sls[ind].drives = True
        for ind in [0, 2, 4]:
            nonSL_staff[ind].drives = True
        for ind in [0, 4]:
            nonstaff[ind].drives = True

        # After creating each instance, determine the expected
        # priority list order prior to shuffling
        expected_priority_SL = [sls[0], sls[1], sls[3], sls[2], sls[4]]
        expected_priority_nonSL_staff = [nonSL_staff[0], nonSL_staff[1],
                                         nonSL_staff[2], nonSL_staff[4],
                                         nonSL_staff[3]]
        expected_priority_nonstaff = [nonstaff[0], nonstaff[1],
                                         nonstaff[4], nonstaff[2],
                                         nonstaff[3]]
        expected_list = (expected_priority_SL + expected_priority_nonSL_staff +
                         expected_priority_nonstaff)

        # Shuffle lists of people
        for lst in [nonSL_staff, sls, nonstaff]:
            random.shuffle(lst)
        everyone = nonSL_staff + sls + nonstaff
        random.shuffle(everyone)


        # SiteLeaders
        obtained_priority_SL = create_priority_list(sls)
        self.assertEqual(len(obtained_priority_SL), len(expected_priority_SL))
        self.assertListEqual([person.name for person in
                              obtained_priority_SL],
                             [person.name for person in expected_priority_SL])

        #StaffMember (not SiteLeader)
        obtained_priority_nonSL_staff = create_priority_list(nonSL_staff)
        self.assertEqual(len(obtained_priority_nonSL_staff),
                         len(expected_priority_nonSL_staff))
        self.assertListEqual([person.name for person in
                              obtained_priority_nonSL_staff],
                             [person.name for person in
                              expected_priority_nonSL_staff])

        #DecalMember
        obtained_priority_nonstaff = create_priority_list(nonstaff)
        self.assertEqual(len(obtained_priority_nonstaff),
                         len(expected_priority_nonstaff))
        self.assertListEqual([person.name for person in
                              obtained_priority_nonstaff],
                             [person.name for person in
                              expected_priority_nonstaff])

        # Compare the obtained & expected priority lists for everyone
        obtained_priority_list = create_priority_list(everyone)
        self.assertEqual(len(obtained_priority_list), len(expected_list))
        self.assertListEqual([person.name for person in
                              obtained_priority_list],
                             [person.name for person in expected_list])

        eliminate_everything()

    def test_find_potential_sites(self):
        pass

    def test_check_sites_are_full(self):
        district = District(name="BUSD")
        common_time = standardize_day_and_time("Monday 9AM - 10AM")
        common_availabilities = [common_time]
        site = district.add_site(name="MX A",
                                 time=common_time)
        site2 = district.add_site(name = "MX B",
                                  time=common_time)
        sl = SiteLeader('Aditya',
                        False,
                        common_availabilities)
        non_SL_staff = StaffMember('Akshara',
                                   False,
                                   common_availabilities)
        non_SL_staff2 = StaffMember('Donald',
                                   False,
                                   common_availabilities)
        decal1 = DecalMember('Ethan',
                             True,
                             common_availabilities)
        decal2 = DecalMember('Melody',
                             False,
                             common_availabilities)

        sl2 = SiteLeader('Surabhi',
                         False,
                         common_availabilities)
        decal3 = DecalMember('Jenna',
                             True,
                             common_availabilities)
        decal4 = DecalMember('Chelsea',
                             False,
                             common_availabilities)
        decal5 = DecalMember('Emily',
                             False,
                             common_availabilities)
        self.assertTrue(check_all_sites_are_clear())
        self.assertFalse(check_all_sites_are_full())

        # Too few people in site2
        site.add_member(sl)
        site.add_member(non_SL_staff)
        site.add_member(decal1)
        site.add_member(decal2)
        site.add_member(decal3)
        self.assertFalse(check_all_sites_are_full())

        # All sites are full
        site.remove_member(decal3)
        site2.add_member(sl2)
        site2.add_member(decal3)
        site2.add_member(decal4)
        site2.add_member(decal5)
        self.assertTrue(check_all_sites_are_full())

        eliminate_everything()

    def test_check_sites_are_valid_and_test_validate_member(self):
        """
        Tests every possible case of an "ill-formed" site.
        aka any site that breaks the rules of what a site consists of
        """
        district = District(name="BUSD")
        common_time = standardize_day_and_time("Monday 9AM - 10AM")
        common_availabilities = [common_time]
        site = district.add_site(name="MX A",
                               time=common_time)

        sl = SiteLeader('Aditya', False, common_availabilities)
        non_SL_staff = StaffMember('Akshara',
                                   False,
                                   common_availabilities)
        non_SL_staff2 = StaffMember('Donald',
                                   False,
                                   common_availabilities)
        decal1 = DecalMember('Ethan',
                             True,
                             common_availabilities)
        decal2 = DecalMember('Melody',
                             False,
                             common_availabilities)

        sl2 = SiteLeader('Surabhi',
                         False,
                         common_availabilities)
        decal3 = DecalMember('Jenna',
                             True,
                             common_availabilities)
        decal4 = DecalMember('Chelsea',
                             False,
                             common_availabilities)
        decal5 = DecalMember('Emily',
                             False,
                             common_availabilities)

        # 2 site leaders in a site
        self.assertTrue(site.validate_person(sl))
        site.add_member(sl)
        self.assertFalse(site.validate_person(sl2))
        site.add_member(sl2)
        with self.assertRaises(Exception):
            check_all_sites_are_valid()
        clear_all_sites()


        # Too many staff (nonSL) members
        for i, person in enumerate([sl, non_SL_staff, non_SL_staff2]):
            if i == 2:
                self.assertFalse(site.validate_person(person))
            else:
                self.assertTrue(site.validate_person(person))
            site.add_member(person)

        with self.assertRaises(Exception):
            check_all_sites_are_valid()
        clear_all_sites()

        # Too many people in a site
        for i, person in enumerate([sl, non_SL_staff, decal1,
                                    decal2, decal3, decal4]):
            if i == 5:
                print(i)
                self.assertFalse(site.validate_person(person))
            else:
                print(i)
                self.assertTrue(site.validate_person(person))
            site.add_member(person)
        with self.assertRaises(Exception):
            check_all_sites_are_valid()
        clear_all_sites()

        # Person added to a site despite being unavailable during the time slot
        unavailable = DecalMember('Argon', False, ["Tuesday 4PM - 5PM"])
        self.assertFalse(site.validate_person(unavailable))
        site.add_member(unavailable)
        with self.assertRaises(Exception):
            check_all_sites_are_valid()

        eliminate_everything()


    def test_find_potential_sites(self):
        pass

    def test_read_site_map(self):
        pass

    def compare_site_maps(self,
                          excel_path1,
                          excel_path2):
        """
        Compares site maps to ensure they have the same values

        Args:
            excel_path1 (str): excel path of first dataframe
            excel_path2 (str): excel path of second dataframe
        """
        assert os.path.exists(excel_path1), (f"The path ({excel_path1})passed into "
                                             "excel_path1 doesn't exist!")
        assert os.path.exists(excel_path2), (f"The path ({excel_path2})passed into "
                                             "excel_path2 doesn't exist!")


        df1 = pd.read_excel(excel_path1)
        df2 = pd.read_excel(excel_path2)
        self.assertListEqual(df1.index.tolist(), df2.index.tolist())

        # Check to ensure they have the same set of columns
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

                if pd.isnull(df1.loc[row, col_name]):
                    self.assertTrue(df2.loc[row, col_name])
                else:
                    self.assertEqual(df1.loc[row, col_name],
                                    df2.loc[row, col_name],
                                    "Df1 and Df2 differ \n"
                                    f"Row:  {row}, Column Name: {col_name}\n"
                                    f"DF1 Value: {df1.loc[row, col_name]},"
                                    f"DF2 Value: {df2.loc[row, col_name]}")



    # @unittest.skip("LOL")
    def test_unfreeze(self):
        save_dir = ROOT / 'tests' / 'test_unfreeze'
        save_path =  save_dir / 'obtained_unfreeze_case0.xlsx'
        comparison_path = save_dir / 'expected_unfreeze_case0.xlsx'
        print(f"Comparison path: {comparison_path}")
        self.assertTrue(os.path.exists(comparison_path), "Oh no!")


        district = District(name="BUSD")
        day_and_time = standardize_day_and_time("Monday 9-10 AM")

        site = district.add_site(name="MX A",
                               time=day_and_time)
        common_availabilities = [day_and_time]

        sl = SiteLeader('Aditya',
                        False,
                        common_availabilities)
        non_SL_staff = StaffMember('Akshara',
                                   False,
                                   common_availabilities)
        decal1 = DecalMember('Ethan',
                             True,
                             common_availabilities)
        decal2 = DecalMember('Melody',
                             False,
                             common_availabilities)

        site_arrangements = create_site_arrangements(
            list(names_to_people.values()),'full')
        self.assertEqual(len(site_arrangements), 1)
        site_arrangements[0].unfreeze(save_path=str(save_path))
        eliminate_everything()

        self.compare_site_maps(str(save_path),
                               str(comparison_path))

    def test_read_populated_site_map(self):
        """
        Assume each person's availabilities and other attributes were already
        encoded.
        """
        pass


    @unittest.skip('huh')
    def test_create_site_arrangements(self):
        """
        Case 1: Fall 2023 Sites: Aditya's & Surabhi's sites
        Once one site is made, the other is predetermined

        There are 2 choices for a SL.--> Aditya/Surabhi
        Akshara can be in either of the two sites. In whichever site she is in,
        there needs to be exactly 2 other decal members (one of whom can drive)

        For whichever site Akshara is in,
        there are two choices for the driver --> Ethan/Jenna

        For whichever site Akshara is in,
        there are 3 choices for the last decal member --> Chelsea/Melody/Emily

        This gives a total of 2 * 2 * 2 * 3 = 24 permutations.
        This is how one of the two sites will look like.
        Aditya/Surabhi (2 choices) Akshara (2 choices for her site),
        Ethan/Jenna (2 choices), Melody/Chelsea,Emily (3 choices)
        """
        district = District(name="BUSD")
        common_time = standardize_day_and_time("Monday 9AM - 10AM")
        site = district.add_site(name="MX A",
                               time=common_time)
        site2 = district.add_site(name="MX B",
                                time=common_time)
        common_availabilities = [common_time]

        sl = SiteLeader('Aditya',
                        False,
                        common_availabilities)
        non_SL_staff = StaffMember('Akshara',
                                   False,
                                   common_availabilities)
        decal1 = StaffMember('Ethan',
                             True,
                             common_availabilities)
        decal2 = StaffMember('Melody',
                             False,
                             common_availabilities)

        sl2 = SiteLeader('Surabhi',
                         False,
                         common_availabilities)
        decal3 = DecalMember('Jenna',
                             True,
                             common_availabilities)
        decal4 = DecalMember('Chelsea',
                             False,
                             common_availabilities)
        decal5 = DecalMember('Emily',
                             False,
                             common_availabilities)
        site_arrangements = create_site_arrangements(
            list(names_to_people.values()),'partial')
        self.assertEqual(len(site_arrangements), 24)
        eliminate_everything()

@unittest.skip("huh")
class testDistrictAndSite(unittest.TestCase):
    def test_add_to_times_to_sites(self):
        district = District(name="BUSD")
        common_time = standardize_day_and_time("Monday 9AM - 10AM")
        site = district.add_site("MX A", time=common_time)
        self.assertIn(common_time, times_to_sites.keys())
        self.assertIn(site, times_to_sites[common_time])
        self.assertIn(site, district.sites)
        eliminate_all_districts()

    def test_remove_from_times_to_sites(self):
        """
        Check district.sites and times_to_sites

        2 cases:
            - 1 site added, 1 site removed
            - N sites added, N sites removed where N > 1
        """
        district = District(name="EBAYC")
        time_slot = standardize_day_and_time("Wednesday 9AM - 10AM")
        site = district.add_site("Franklin A", time=time_slot)
        district.remove_site(site)
        self.assertNotIn(time_slot, times_to_sites.keys())
        self.assertNotIn(site, district.sites)

        time_slot2 = standardize_day_and_time("Wednesday 10AM - 11AM")
        site2_name = "Franklin B"
        site3_name = "Franklin C"
        site2 = district.add_site(site2_name, time=time_slot2)
        site3 = district.add_site(site3_name, time=time_slot2)
        district.remove_site(site2)
        self.assertIn(time_slot2, times_to_sites)
        self.assertNotIn(site2, times_to_sites[time_slot2])
        self.assertNotIn(site2, district.sites)

        eliminate_everything()

@unittest.skip(reason="idk")
class testEssentialFunction(unittest.TestCase):
    def test_eliminate_everything(self):
        district = District(name="Imaginary")
        time_slot = standardize_day_and_time("Wednesday 10AM - 11AM")
        site = district.add_site("Imagine A", time=time_slot)
        site2 = district.add_site("Imagine B", time=time_slot)
        site3 = district.add_site("Imagine C", time=time_slot)
        site4 = district.add_site("Imagine D", time=time_slot)
        sites = [site, site2, site3, site4]

        person1 = SiteLeader(name="Alpha",
                             can_drive=True)
        person2 = StaffMember(name="Bravo",
                             can_drive=True)
        person3 = StaffMember(name="Charlie",
                             can_drive=True)
        people = [person1, person2, person3]
        for person in people:
            person.add_availability(time_slot)

        site.add_member(person1)
        site.add_member(person2)
        site.add_member(person3)

        eliminate_everything()
        self.assertDictEqual(names_to_districts, {})
        self.assertListEqual(district.sites, [])
        self.assertDictEqual(names_to_sites, {})
        self.assertDictEqual(ids_to_sites, {})

        # Check dictionaries containing people
        self.assertDictEqual(names_to_people, {})
        self.assertDictEqual(names_to_site_leaders, {})
        self.assertDictEqual(names_to_nonSL_staff_members, {})
        self.assertDictEqual(names_to_nonstaff, {})

@unittest.skip(reason="idk")
class testDataPreprocessing(unittest.TestCase):
    def test_extract_availabilities_from_string(self):
        sp24_decal_responses = pd.read_excel(str(ROOT / 'tests' / 'test_sp24' /
                                     'sp24_decal_responses.xlsx'))
        time_question = ('What time slots are you available to go to site?  '
                         'Please check all the options that are available for '
                         'you, not just the ones that are the most '
                         'convenient. \n\nIf you are not available to attend '
                         'any of these times, we cannot admit you into this '
                         'decal for the Spring 2024 semester.')
        first_person_availability = sp24_decal_responses.loc[0, time_question]

        availabilities = extract_availabilities_from_string(
            first_person_availability)
        expected_list = ['Wednesday 4:15PM - 5:15PM',
                         'Friday 1:30PM - 2:30PM',
                         'Friday 2:30PM - 3:30PM',
                         'Friday 3PM - 4PM',
                         'Friday 4PM - 5PM']
        self.assertListEqual(availabilities, expected_list)



def test_compare_site_maps(site_map1, site_map2):
    """
    I'll create test dataframes within tests/test_dataframes.
    I'll create site arrangements based off of some situation and then
    compare those site arrangements to the dataframes that reflect
    the expected site arrangements.

    This either requires me to either read the expected site maps into
    site arrangements OR freeze the site arrangements into dataframes.

    Either way, this will not only test whether I make the right site
    arrangements but also whether my freeze/read_site_map functions are
    working.

    So, before I can complete this function, I need to ensure that
    the two aforementioned functions work first.

    Args:
        site_map1 (_type_): _description_
        site_map2 (_type_): _description_
    """
    assert names_to_sites is not {}, "No sites provided"
    pass







if __name__ == "__main__":
    unittest.main()
