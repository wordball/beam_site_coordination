import unittest
from classes import (
    DecalMember, StaffMember, SiteLeader, District, School, Site,
    SiteArrangement, add_to_times_to_sites, remove_from_times_to_sites,
    times_to_sites
)

class TestDecalMember(unittest.TestCase):

    def test_decal_member_initialization(self):
        member = DecalMember(name="Alice", can_drive=True, availabilities=["Monday", "Wednesday"])
        self.assertEqual(member.name, "Alice")
        self.assertTrue(member.drives)
        self.assertEqual(member.availabilities, ["Monday", "Wednesday"])
        self.assertIsNone(member.assigned_site)

    def test_decal_member_add_availability(self):
        member = DecalMember(name="Alice", can_drive=True)
        member.add_availability("Friday")
        self.assertIn("Friday", member.availabilities)

    def test_decal_member_remove_availability(self):
        member = DecalMember(name="Alice", can_drive=True, availabilities=["Monday", "Wednesday"])
        member.remove_availability("Monday")
        self.assertNotIn("Monday", member.availabilities)


class TestStaffMember(unittest.TestCase):

    def test_staff_member_initialization(self):
        staff = StaffMember(name="Bob", can_drive=False)
        self.assertEqual(staff.name, "Bob")
        self.assertTrue(staff.in_staff)


class TestSiteLeader(unittest.TestCase):

    def test_site_leader_initialization(self):
        sl = SiteLeader(name="Charlie", can_drive=True)
        self.assertEqual(sl.name, "Charlie")
        self.assertTrue(sl.in_staff)
        self.assertTrue(sl.leads_site)


class TestDistrictAndSchool(unittest.TestCase):

    def test_add_school(self):
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        self.assertIn("Malcolm X Elementary", district.schools)
        self.assertEqual(school.name, "Malcolm X Elementary")

    def test_remove_school(self):
        district = District(name="EBAYC")
        school = district.add_school(name="Malcolm X Elementary")
        district.remove_school(school)
        self.assertNotIn("Malcolm X Elementary", district.schools)


class TestSite(unittest.TestCase):

    def test_site_initialization(self):
        district = District(name="EBAYC")
        school = School(name="Malcolm X Elementary", district=district)
        site = Site(name="Harding A", time="9:00 AM", school=school)
        self.assertEqual(site.name, "Harding A")
        self.assertEqual(site.time, "9:00 AM")

    def test_add_member(self):
        district = District(name="EBAYC")
        school = School(name="Malcolm X Elementary", district=district)
        site = Site(name="Harding A", time="9:00 AM", school=school)
        member = DecalMember(name="Alice", can_drive=True)
        site.add_member(member)
        self.assertIn(member, site.members)
        self.assertEqual(member.assigned_site, site)


# class TestSiteArrangement(unittest.TestCase):

#     def test_freeze_and_unfreeze(self):
#         # Setup
#         district = District(name="EBAYC")
#         school = School(name="Malcolm X Elementary", district=district)
#         site = Site(name="Harding A", time="9:00 AM", school=school)
#         member = DecalMember(name="Alice", can_drive=True)
#         site.add_member(member)

#         arrangement = SiteArrangement()
#         arrangement.freeze()
#         self.assertIn(site.id, arrangement.site_assignments)
#         self.assertIn(member.name, arrangement.site_assignments[site.id])

#         # Test unfreeze
#         arrangement.unfreeze()
#         self.assertEqual(member.assigned_site, site)


class testSchoolAndSite(unittest.TestCase):

    def test_add_to_times_to_sites(self):
        district = District(name="BUSD")
        school = district.add_school("Malcolm X Elementary")
        site = school.add_site("MX A", time="9:00 AM")
        self.assertIn("9:00 AM", times_to_sites.keys())
        self.assertIn(site, times_to_sites["9:00 AM"])
        self.assertIn(site, school.sites)

    def test_remove_from_times_to_sites(self):
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
