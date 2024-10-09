import unittest
from classes import (
    DecalMember, StaffMember, SiteLeader,
    District, School, Site, SiteArrangement,
    add_to_times_to_sites, remove_from_times_to_sites, clear_all_sites,
    times_to_sites, eliminate_all_sites
)

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

    def test_decal_member_add_availability(self):
        """
        Check whether adding an availability will show up in availabilities
        attribute

        """
        member = DecalMember(name="Alice", can_drive=True)
        member.add_availability("Friday")
        self.assertIn("Friday", member.availabilities)

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
        self.assertFalse(staff.can_drive)
        self.assertListEqual(staff.availabilities, [])
        self.assertIsNone(staff.assigned_site)
        self.assertTrue(staff.in_staff)
        self.assertFalse(staff.leads_site)




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


class TestDistrictAndSchool(unittest.TestCase):

    def test_add_school(self):
        """
        Check the following:
        1. district.schools
        2. names_to_schools
        3. School instance attributes
            a. name
            b. sites
            c. district
        # TODO
        """
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        self.assertIn("Malcolm X Elementary", district.schools)
        self.assertEqual(school.name, "Malcolm X Elementary")


    def test_remove_school(self):
        """
        Removing school should remove it from all records
        Check the following:
        1. district.schools
        2. names_to_schools
        3. School instance attributes
            a. name
            b. sites
            c. district
        # TODO
        """
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        district.remove_school(school)
        self.assertNotIn("Malcolm X Elementary", district.schools)

    def test_get_num_sites(self):
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        school.add_site("MX A", time="9:00 AM")
        school.add_site("MX B", time="10:00 AM")
        self.assertEqual(school.get_num_sites(), 2)

    def test_get_num_site_leaders(self):
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        site1 = school.add_site("MX A", time="9:00 AM")
        site2 = school.add_site("MX B", time="10:00 AM")
        sl = SiteLeader(name="Charlie", can_drive=True)
        site1.add_member(sl)
        self.assertEqual(school.get_num_site_leaders(), 1)


class TestSite(unittest.TestCase):

    def test_add_site(self):
        """
        Check the following:
        1. Site instance
            - name
            - time
            - school reference
        """
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        site = school.add_site(name="Harding A", time="9:00 AM")
        self.assertEqual(site.name, "Harding A")
        self.assertEqual(site.time, "9:00 AM")
        self.assertEqual(site.school, school)

    def test_add_member(self):
        """
        Check member.assigned_site and site.members
        """
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        site = school.add_site(name="Harding A", time="9:00 AM")
        member = DecalMember(name="Alice", can_drive=True)
        site.add_member(member)
        self.assertIn(member, site.members)
        self.assertEqual(member.assigned_site, site)

    def test_clear_site(self):
        """
        Checks each assigned person's assigned_site attribute
        and the site.members list
        # TODO
        """
        pass

    def test_validate_person(self):
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        site = school.add_site(name="Harding A", time="9:00 AM")

        sl = SiteLeader(name="Charlie",
                        can_drive=True,
                        availabilities=["9:00 AM"])
        staff = StaffMember(name="Bob",
                            can_drive=False,
                            availabilities=["9:00 AM"])
        decal1 = DecalMember(name="Alice",
                             can_drive=True,
                             availabilities=["9:00 AM"])
        decal2 = DecalMember(name="David",
                             can_drive=False,
                             availabilities=["9:00 AM"])

        self.assertTrue(site.validate_person(sl))
        site.add_member(sl)
        self.assertFalse(site.validate_person(
            SiteLeader(name="Eve",
                       can_drive=True,
                       availabilities=["9:00 AM"])))

        self.assertTrue(site.validate_person(staff))
        site.add_member(staff)
        self.assertFalse(site.validate_person(
            StaffMember(name="Frank",
                        can_drive=True,
                        availabilities=["9:00 AM"])))

        self.assertTrue(site.validate_person(decal1))
        site.add_member(decal1)
        self.assertTrue(site.validate_person(decal2))
        site.add_member(decal2)
        self.assertFalse(site.validate_person(
            DecalMember(name="Grace",
                        can_drive=True,
                        availabilities=["9:00 AM"])))

    def test_update_booleans(self):
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        site = school.add_site(name="Harding A", time="9:00 AM")

        sl = SiteLeader(name="Charlie",
                        can_drive=True,
                        availabilities=["9:00 AM"])
        decal = DecalMember(name="Alice",
                            can_drive=False,
                            availabilities=["9:00 AM"])

        site.add_member(sl)
        site.update_booleans()
        self.assertTrue(site.has_site_leader)
        self.assertTrue(site.has_driver)
        self.assertFalse(site.is_full)

        site.add_member(decal)
        site.update_booleans()
        self.assertTrue(site.is_full)




class TestSiteArrangement(unittest.TestCase):
    def test_freeze_and_unfreeze(self):
        district = District(name="BUSD")
        school = district.add_school("Malcolm X Elementary")
        site = school.add_site(name="MX A",
                               time="9:00 AM")

        # Create a DecalMember object
        member = DecalMember(name="Alice", can_drive=True,
                             availabilities=["9:00 AM"])
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
        eliminate_all_sites()

    def test_create_site_arrangements(self):
        district = District(name="EBAYC")
        school = district.add_school("Malcolm X Elementary")
        site = school.add_site(name="MX A",
                               time="9:00 AM")
        site2 = school.add_site(name="MX B",
                                time="10:00 AM")

        sl = SiteLeader('Aditya',
                        False,
                        ["9:00 AM"])
        non_SL_staff = StaffMember('Akshara',
                                   False,
                                   ["9:00 AM"])
        decal1 = StaffMember('Ethan',
                             True,
                             ["9:00 AM"])
        decal2 = StaffMember('Melody',
                             False,
                             ["9:00 AM"])

        sl2 = SiteLeader('Surabhi',
                         False,
                         )



class testSchoolAndSite(unittest.TestCase):

    def test_add_to_times_to_sites(self):
        district = District(name="BUSD")
        school = district.add_school("Malcolm X Elementary")
        site = school.add_site("MX A", time="9:00 AM")
        self.assertIn("9:00 AM", times_to_sites.keys())
        self.assertIn(site, times_to_sites["9:00 AM"])
        self.assertIn(site, school.sites)

    def test_remove_from_times_to_sites(self):
        """
        Check school.sites and times_to_sites

        2 cases:
            - 1 site added, 1 site removed
            - N sites added, N sites removed where N > 1
        """
        district = District(name="EBAYC")
        school = district.add_school("Franklin Elementary")
        site = school.add_site("Franklin A", time="11:00 AM")
        school.remove_site(site)
        self.assertNotIn("11:00 AM", times_to_sites.keys())
        self.assertNotIn(site, school.sites)

        time2 = "10:00 AM"
        site2_name = "Franklin B"
        site3_name = "Franklin C"
        site2 = school.add_site(site2_name, time=time2)
        site3 = school.add_site(site3_name, time=time2)
        school.remove_site(site2)
        self.assertIn(time2, times_to_sites)
        self.assertNotIn(site2, times_to_sites[time2])
        self.assertNotIn(site2, school.sites)


if __name__ == "__main__":
    unittest.main()
