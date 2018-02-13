# -*- coding: utf-8 -*-
import unittest
from graas_openeo_core_wrapper.graas_interface import GRaaSInterface
from graas_openeo_core_wrapper.test_base import TestBase
from pprint import pprint

__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


class GRaaSInterfaceTestCase(TestBase):

    def test_health_check(self):
        iface = GRaaSInterface(self.gconf)
        self.assertTrue(iface.check_health())

    def test_list_raster(self):
        iface = GRaaSInterface(self.gconf)
        status, layers = iface.list_raster(mapset="PERMANENT")
        pprint(layers)

        self.assertEqual(status, 200)
        self.assertEqual(len(layers), 126)

    def test_list_vector(self):
        iface = GRaaSInterface(self.gconf)
        status, layers = iface.list_vector(mapset="PERMANENT")
        pprint(layers)

        self.assertEqual(status, 200)
        self.assertEqual(len(layers), 0)

    def test_list_strds(self):
        iface = GRaaSInterface(self.gconf)
        status, layers = iface.list_strds(mapset="PERMANENT")
        pprint(layers)

        self.assertEqual(status, 200)
        self.assertEqual(len(layers), 2)

    def test_strds_info(self):
        iface = GRaaSInterface(self.gconf)
        status, info = iface.strds_info(mapset="PERMANENT",
                                        strds_name="precipitation_1950_2013_yearly_mm")
        pprint(info)

        self.assertEqual(status, 200)
        self.assertTrue("temporal_type" in info)
        self.assertTrue("aggregation_type" in info)
        self.assertTrue("creation_time" in info)
        self.assertTrue("creator" in info)
        self.assertTrue("granularity" in info)
        self.assertTrue("modification_time" in info)
        self.assertTrue("number_of_maps" in info)

    def test_mapset_info(self):
        iface = GRaaSInterface(self.gconf)
        status, info = iface.mapset_info(mapset="PERMANENT")
        pprint(info)

        self.assertEqual(status, 200)
        self.assertTrue("region" in info)
        self.assertTrue("projection" in info)

    def test_list_mapsets(self):
        iface = GRaaSInterface(self.gconf)
        status, mapsets = iface.list_mapsets()
        pprint(mapsets)

        self.assertEqual(status, 200)
        self.assertEqual(len(mapsets), 1)

    def test_strds_exists(self):
        iface = GRaaSInterface(self.gconf)
        status = iface.check_strds_exists(strds_name="precipitation_1950_2013_yearly_mm@PERMANENT")
        self.assertTrue(status)

        iface = GRaaSInterface(self.gconf)
        status = iface.check_strds_exists(strds_name="precipitation_1950_2013_yearly_mm")
        self.assertTrue(status)

        iface = GRaaSInterface(self.gconf)
        status = iface.check_strds_exists(strds_name="precipitation_1950_2013_yearly_mm_nope")
        self.assertFalse(status)


if __name__ == "__main__":
    unittest.main()