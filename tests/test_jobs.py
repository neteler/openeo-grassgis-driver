# -*- coding: utf-8 -*-
import unittest
import pprint
from flask import json

from openeo_grass_gis_driver.test_base import TestBase
from openeo_grass_gis_driver.utils.process_graph_examples_v10 import \
    FILTER_BBOX, NDVI_STRDS, ACTINIA_PROCESS

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


JOB_TEMPLATE = {
    "title": "The title of the job",
    "description": "The description of the job",
    "process": None,
}


class JobsTestCase(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        response = self.app.delete(self.prefix + '/jobs', headers=self.auth)
        self.assertEqual(204, response.status_code)

    def test_job_creation_1(self):
        """Run the test in the ephemeral database
        """
        JOB_TEMPLATE["process"] = FILTER_BBOX["process"]

        response = self.app.post(
            self.prefix +
            '/jobs',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(201, response.status_code)
        job_id = response.get_data().decode("utf-8")

        response = self.app.get(self.prefix + '/jobs', headers=self.auth)
        data = json.loads(response.get_data().decode("utf-8"))
        pprint.pprint(data)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.get_data().decode("utf-8"))
        pprint.pprint(data)

        self.assertEqual(job_id, data["jobs"][0]["id"])

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.get_data().decode("utf-8"))
        pprint.pprint(data)

        self.assertEqual(job_id, data["id"])

    def test_job_creation_2(self):
        """Run the test in the ephemeral database
        """
        JOB_TEMPLATE["process"] = NDVI_STRDS["process"]

        response = self.app.post(
            self.prefix +
            '/jobs',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(201, response.status_code)
        job_id = response.get_data().decode("utf-8")

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(200, response.status_code)

        data = json.loads(response.get_data().decode("utf-8"))
        pprint.pprint(data)
        self.assertEqual(job_id, data["id"])

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}' + "_nope", headers=self.auth)
        self.assertEqual(404, response.status_code)

    def test_job_creation_deletion_1(self):
        """Run the test in the ephemeral database
        """
        JOB_TEMPLATE["process"] = NDVI_STRDS["process"]

        response = self.app.post(
            self.prefix +
            '/jobs',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(201, response.status_code)
        job_id = response.get_data().decode("utf-8")

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(200, response.status_code)

        response = self.app.delete(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(204, response.status_code)

        response = self.app.delete(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(404, response.status_code)

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(404, response.status_code)

    def test_actinia_process(self):
        """Run the test in the ephemeral database
        """
        JOB_TEMPLATE["process"] = ACTINIA_PROCESS["process"]

        response = self.app.post(
            self.prefix +
            '/jobs',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(201, response.status_code)
        job_id = response.get_data().decode("utf-8")

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(200, response.status_code)

        response = self.app.delete(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(204, response.status_code)

        response = self.app.delete(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(404, response.status_code)

        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        self.assertEqual(404, response.status_code)


class JobsTestResultsCase(TestBase):

    def setUp(self):
        TestBase.setUp(self)
        response = self.app.delete(self.prefix + '/jobs', headers=self.auth)
        self.assertEqual(204, response.status_code)

    def test_job_creation_and_processing_filter_box(self):
        """Run the test in the ephemeral database
        """
        JOB_TEMPLATE["process"] = FILTER_BBOX["process"]

        response = self.app.post(
            self.prefix +
            '/jobs',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(201, response.status_code)
        job_id = response.get_data().decode("utf-8")

        # Get job information
        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}/results', headers=self.auth)
        self.assertEqual(200, response.status_code)
        data = response.get_data().decode("utf-8")
        pprint.pprint(data)

        # Start the job
        response = self.app.post(
            f'{self.prefix}/jobs/{job_id}/results', headers=self.auth)
        data = response.get_data().decode("utf-8")
        pprint.pprint(data)
        self.assertEqual(202, response.status_code)

        # get job information
        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}/results', headers=self.auth)
        data = response.get_data().decode("utf-8")
        pprint.pprint(data)
        self.assertEqual(200, response.status_code)

#    def test_job_creation_and_processing_zonal_stats(self):
#        """Run the test in the ephemeral database
#        """
#        JOB_TEMPLATE["process_graph"] = ZONAL_STATISTICS["process_graph"]
#
#        response = self.app.post('/jobs', data=json.dumps(JOB_TEMPLATE),
#                                 content_type="application/json",
#                                 headers=self.auth)
#        self.assertEqual(201, response.status_code)
#        job_id = response.get_data().decode("utf-8")
#
#        # Get job information
#        response = self.app.get(f'/jobs/{job_id}/results',
#                                content_type="application/json",
#                                headers=self.auth)
#        self.assertEqual(200, response.status_code)
#        data = response.get_data().decode("utf-8")
#        print(data)
#
#        # Start the job
#        response = self.app.post(f'/jobs/{job_id}/results', headers=self.auth)
#        data = response.get_data().decode("utf-8")
#        print(data)
#        self.assertEqual(202, response.status_code)
#
#        # get job information
#        response = self.app.get(f'/jobs/{job_id}/results', headers=self.auth)
#        data = response.get_data().decode("utf-8")
#        print(data)
#        self.assertEqual(200, response.status_code)
#
#        # cancel the job
#        response = self.app.delete(f'/jobs/{job_id}/results',
#                                   headers=self.auth)
#        data = response.get_data().decode("utf-8")
#        print(data)
#        self.assertEqual(204, response.status_code)
#
#        import time
#        time.sleep(2)
#
#        # get job information
#        response = self.app.get(f'/jobs/{job_id}/results', headers=self.auth)
#        data = response.get_data().decode("utf-8")
#        print(data)
#        self.assertEqual(200, response.status_code)

    def test_job_creation_and_patch_filter_box(self):
        """Run job creation and patch test
        """
        # as of openeo API 1.0, patch is no longer supported
        JOB_TEMPLATE["process"] = FILTER_BBOX["process"]

        response = self.app.post(
            self.prefix +
            '/jobs',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(201, response.status_code)
        job_id = response.get_data().decode("utf-8")
        print(job_id)

        # Get job information
        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        data = response.get_data().decode("utf-8")
        print(data)
        self.assertEqual(200, response.status_code)

        JOB_TEMPLATE["process"] = NDVI_STRDS["process"]

        response = self.app.patch(
            f'{self.prefix}/jobs/{job_id}',
            data=json.dumps(JOB_TEMPLATE),
            content_type="application/json",
            headers=self.auth)
        self.assertEqual(204, response.status_code)

        # Get job information
        response = self.app.get(
            f'{self.prefix}/jobs/{job_id}', headers=self.auth)
        data = response.get_data().decode("utf-8")
        print(data)
        self.assertEqual(200, response.status_code)


if __name__ == "__main__":
    unittest.main()
