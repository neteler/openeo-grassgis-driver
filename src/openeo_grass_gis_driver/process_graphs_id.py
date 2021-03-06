# -*- coding: utf-8 -*-
from uuid import uuid4
import traceback
import sys
from flask import make_response, jsonify, request
from openeo_grass_gis_driver.process_graph_db import GraphDB
from openeo_grass_gis_driver.actinia_processing.actinia_interface import \
     ActiniaInterface
from openeo_grass_gis_driver.authentication import ResourceBase
from openeo_grass_gis_driver.models.error_schemas import ErrorSchema

__license__ = "Apache License, Version 2.0"
__author__ = "Sören Gebbert"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"


class ProcessGraphId(ResourceBase):
    """The /process_graphs/{process_graph_id} endpoint implementation"""

    def __init__(self):
        ResourceBase.__init__(self)
        self.iface = ActiniaInterface()
        self.graph_db = GraphDB()

    def get(self, id):
        """Return all jobs in the job database"""
        # TODO: Implement user specific database access

        if id in self.graph_db:

            graph = self.graph_db[id]
            graph["id"] = id
            return make_response(jsonify(graph), 200)
        else:
            return ErrorSchema(
                id=str(
                    uuid4()),
                code=400,
                message=f"Process graph id {id} not found").as_response(400)

    # PATCH and POST have been removed from the openeo API
    def put(self, id):
        try:
            """Store and replace custom process-graphs"""
            # TODO: Implement user specific database access

            process_graph = request.get_json()
            self.graph_db[id] = process_graph
            return make_response(id, 200)
        except Exception:

            e_type, e_value, e_tb = sys.exc_info()
            traceback_model = dict(message=str(e_value),
                                   traceback=traceback.format_tb(e_tb),
                                   type=str(e_type))
            return ErrorSchema(
                id="1234567890",
                code=2,
                message=str(traceback_model)).as_response(400)

    def delete(self, id):
        """Remove a single process graph from the database"""

        if id in self.graph_db:

            del self.graph_db[id]
            return make_response(
                f"Process graph {id} have been successfully deleted", 204)
        else:
            return ErrorSchema(
                id=str(
                    uuid4()),
                code=400,
                message=f"Process graph id {id} not found").as_response(400)
