import sys
import unittest
from autoprotocol.container_type import ContainerType
from autoprotocol.container import Container, Well
from autoprotocol.unit import Unit

if sys.version_info[0] >= 3:
    xrange = range

dummy_type = ContainerType(name="dummy",
                           well_count=15,
                           well_depth_mm=None,
                           well_volume_ul=200,
                           well_coating=None,
                           sterile=False,
                           is_tube=False,
                           capabilities=[],
                           shortname="dummy",
                           col_count=5,
                           dead_volume_ul=15)


class ContainerWellRefTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Container(None, dummy_type)

    def test_well_ref(self):
        self.assertIsInstance(self.c.well("B4"), Well)
        self.assertIsInstance(self.c.well(14), Well)

    def test_decompose(self):
        self.assertEqual((2, 3), self.c.decompose("C4"))

    def test_well_identity(self):
        self.assertIs(self.c.well("A1"), self.c.well(0))

    def test_humanize(self):
        self.assertEqual("A1", self.c.well(0).humanize())
        self.assertEqual("B3", self.c.well(7).humanize())
        # check bounds
        with self.assertRaises(ValueError):
            self.c.humanize(20)
            self.c.humanize(-1)
        # check input type
        with self.assertRaises(TypeError):
            self.c.humanize("10")
            self.c.humanize(self.c.well(0))

    def test_robotize(self):
        self.assertEqual(0, self.c.robotize("A1"))
        self.assertEqual(7, self.c.robotize("B3"))
        # check bounds
        with self.assertRaises(ValueError):
            self.c.robotize("A10")
            self.c.robotize("J1")


class ContainerWellGroupConstructionTestCase(unittest.TestCase):
    def setUp(self):
        self.c = Container(None, dummy_type)

    def test_all_wells(self):
        # all_wells() should return wells in row-dominant order
        ws = self.c.all_wells()
        self.assertEqual(15, len(ws))
        for i in xrange(15):
            self.assertEqual(i, ws[i].index)

    def test_columnwise(self):
        # or column-dominant order if columnwise
        ws = self.c.all_wells(columnwise=True)
        self.assertEqual(15, len(ws))
        row_count = dummy_type.well_count / dummy_type.col_count
        for i in xrange(15):
            row, col = self.c.decompose(ws[i].index)
            self.assertEqual(i, row+col*row_count)

    def test_wells_from(self):
        # wells_from should return the correct things
        ws = self.c.wells_from("A1", 6)
        self.assertEqual([0, 1, 2, 3, 4, 5], [w.index for w in ws])

        ws = self.c.wells_from("B3", 6)
        self.assertEqual([7, 8, 9, 10, 11, 12], [w.index for w in ws])

        ws = self.c.wells_from("A1", 6, columnwise=True)
        self.assertEqual([0, 5, 10, 1, 6, 11], [w.index for w in ws])

        ws = self.c.wells_from("B3", 6, columnwise=True)
        self.assertEqual([7, 12, 3, 8, 13, 4], [w.index for w in ws])


class WellVolumeTestCase(unittest.TestCase):
    def test_set_volume(self):
        c = Container(None, dummy_type)
        c.well(0).set_volume("20:microliter")
        self.assertEqual(20, c.well(0).volume.value)
        self.assertEqual("microliter", c.well(0).volume.unit)
        self.assertIs(None, c.well(1).volume)

    def test_set_volume_through_group(self):
        c = Container(None, dummy_type)
        c.all_wells().set_volume("30:microliter")
        for w in c.all_wells():
            self.assertEqual(30, w.volume.value)

    def test_set_volume_unit_conv(self):
        c = Container(None, dummy_type)
        c.well(0).set_volume("200:nanoliter")
        self.assertTrue(c.well(0).volume == Unit(0.2, "microliter"))
        c.well(1).set_volume(".1:milliliter")
        self.assertTrue(c.well(1).volume == Unit(100, "microliter"))
        with self.assertRaises(ValueError):
            c.well(2).set_volume("1:liter")

class WellPropertyTestCase(unittest.TestCase):
    def test_set_properties(self):
        c = Container(None, dummy_type)
        c.well(0).set_properties({"Concentration": "40:nanogram/microliter"})
        self.assertIsInstance(c.well(0).properties, dict)
        self.assertEqual(["Concentration"],
                         list(c.well(0).properties.keys()))
        self.assertEqual(["40:nanogram/microliter"],
                         list(c.well(0).properties.values()))

    def test_add_properties(self):
        c = Container(None, dummy_type)
        c.well(0).add_properties({"nickname": "dummy"})
        self.assertEqual(len(c.well(0).properties.keys()), 1)
        c.well(0).set_properties({"concentration": "12:nanogram/microliter"})
        self.assertEqual(len(c.well(0).properties.keys()), 2)
        c.well(0).add_properties({"property1": "2", "ratio": "1:10"})
        self.assertEqual(len(c.well(0).properties.keys()), 4)
        self.assertRaises(TypeError, c.well(0).add_properties,
                          ["property", "value"])

    def test_add_properties_wellgroup(self):
        c = Container(None, dummy_type)
        group = c.wells_from(0, 3).set_properties({"property1": "value1",
                                                   "property2": "value2"})
        c.well(0).add_properties({"property4": "value4"})
        self.assertEqual(len(c.well(0).properties.keys()), 3)
        for well in group:
            self.assertTrue("property1" in well.properties)
            self.assertTrue("property2" in well.properties)

class WellNameTestCase(unittest.TestCase):
    def test_set_name(self):
        c = Container(None, dummy_type)
        c.well(0).set_name("sample")
        self.assertEqual(c.well(0).name, "sample")
