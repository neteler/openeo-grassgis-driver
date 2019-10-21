# -*- coding: utf-8 -*-
from random import randint
import json
from openeo_grass_gis_driver.actinia_processing.base import PROCESS_DICT, PROCESS_DESCRIPTION_DICT, Node, check_node_parents
from openeo_grass_gis_driver.models.process_graph_schemas import ProcessGraphNode, ProcessGraph
from openeo_grass_gis_driver.models.process_schemas import Parameter, ProcessDescription, ReturnValue, ProcessExample
from openeo_grass_gis_driver.actinia_processing.actinia_interface import ActiniaInterface

__license__ = "Apache License, Version 2.0"
__author__ = "Markus Metz"
__copyright__ = "Copyright 2018, Markus Metz, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

PROCESS_NAME = "filter_temporal"


def create_process_description():
    p_data = Parameter(description="Any openEO process object that returns raster datasets "
                                   "or space-time raster dataset",
                       schema={"type": "object", "format": "eodata"},
                       required=True)

    p_extent = Parameter(description="Left-closed temporal interval, i.e. an array with exactly two elements:\n\n1. The first element is the start of the date and/or time interval. The specified instance in time is **included** in the interval.\n2. The second element is the end of the date and/or time interval. The specified instance in time is **excluded** from the interval.\n\nThe specified temporal strings follow [RFC 3339](https://tools.ietf.org/html/rfc3339). Although [RFC 3339 prohibits the hour to be '24'](https://tools.ietf.org/html/rfc3339#section-5.7), **this process allows the value '24' for the hour** of an end time in order to make it possible that left-closed time intervals can fully cover the day.\n\nAlso supports open intervals by setting one of the boundaries to `null`, but never both.",
                       schema={"type": "array",
                               "format": "temporal-interval",
                               "minItems": 2,
                               "maxItems": 2,
                               "items": {
                                 "anyOf": [
                                  {
                                    "type": "string",
                                    "format": "date-time"
                                  },
                                  {
                                  "type": "string",
                                    "format": "date"
                                  },
                                  {
                                    "type": "string",
                                    "format": "time"
                                  },
                                  {
                                    "type": "null"
                                  }
                                ]
                              },
                              "examples": [
                                [
                                  "2015-01-01",
                                  "2016-01-01"
                                ],
                                [
                                  "12:00:00Z",
                                  "24:00:00Z"
                                ]
                              ]},
                       required=True)

    p_dim = Parameter(description="The temporal dimension to filter on. If the dimension is not set or is set to `null`, the data cube is expected to only have one temporal dimension. Fails with a `TooManyDimensions` error if it has more dimensions. Fails with a `DimensionNotAvailable` error if the specified dimension does not exist.\n\n**Note:** The default dimensions a data cube provides are described in the collection's metadata field `cube:dimensions`.",
                      schema={"type": [
                                "string",
                                "null"
                              ],
                              "default": "null"})

    rv = ReturnValue(description="Processed EO data.",
                     schema={"type": "object", "format": "eodata"})

    # Example
    arguments = {
                "data": {"from_node": "get_strds_data"},
                "extent": ["2001-01-01", "2005-01-01"],
            }
    node = ProcessGraphNode(process_id=PROCESS_NAME, arguments=arguments)
    graph = ProcessGraph(title="title", description="description", process_graph={"filter_daterange_1": node})
    examples = [ProcessExample(title="Simple example", description="Simple example",
                               process_graph=graph)]

    pd = ProcessDescription(id=PROCESS_NAME,
                            description="Limits the data cube to the specified interval of dates and/or times.",
                            summary="Temporal filter for a date and/or time interval",
                            parameters={"data": p_data, "extent": p_extent, "dimension": p_dim},
                            returns=rv,
                            examples=examples)

    return json.loads(pd.to_json())


PROCESS_DESCRIPTION_DICT[PROCESS_NAME] = create_process_description()


def create__process_chain_entry(input_name, start_time, end_time, output_name):
    """Create a Actinia command of the process chain that uses t.rast.extract to create a subset of a strds
       The filter checks whether the temporal dimension value is 
       greater than or equal to the lower boundary (start date/time) 
       and the temporal dimension value is less than the value of the 
       upper boundary (end date/time). This corresponds to a 
       left-closed interval, which contains the lower boundary but not 
       the upper boundary.

    :param strds_name: The name of the strds
    :param start_time:
    :param end_time:
    :return: A Actinia process chain description
    """
    location, mapset, datatype, layer_name = ActiniaInterface.layer_def_to_components(input_name)
    input_name = layer_name
    if mapset is not None:
        input_name = layer_name + "@" + mapset
    base_name = "%s_extract" % layer_name
    start_time = start_time.replace('T', ' ')
    end_time = end_time.replace('T', ' ')

    # Get info about the time series to extract its resolution settings and bbox
    rn = randint(0, 1000000)

    pc = {"id": "t_rast_extract_%i" % rn,
          "module": "t.rast.extract",
          "inputs": [{"param": "input", "value": input_name},
                     {"param": "where", "value": "start_time >= '%(start)s' "
                                                 "AND end_time < '%(end)s'" % {"start": start_time, "end": end_time}},
                     {"param": "output", "value": output_name},
                     {"param": "expression", "value": "1.0 * %s" % input_name},
                     {"param": "basename", "value": base_name},
                     {"param": "suffix", "value": "num"}]}

    return pc


def get_process_list(node: Node):
    """Analyse the process description and return the Actinia process chain and the name of the processing result
    strds that was filtered by start and end date

    :param node: The process node
    :return: (output_names, actinia_process_list)
    """

    input_names, process_list = check_node_parents(node=node)
    output_names = []

    for input_name in node.get_parent_by_name(parent_name="data").output_names:

        location, mapset, datatype, layer_name = ActiniaInterface.layer_def_to_components(input_name)

        # Skip if the datatype is not a strds and put the input into the output
        if datatype and datatype != "strds":
            output_names.append(input_name)
            continue

        output_name = "%s_%s" % (layer_name, PROCESS_NAME)
        output_names.append(output_name)
        node.add_output(output_name)

        start_time = None
        end_time = None

        if "extent" in node.arguments:
            start_time = node.arguments["extent"][0]
            end_time = node.arguments["extent"][1]

        pc = create__process_chain_entry(input_name=input_name,
                                         start_time=start_time,
                                         end_time=end_time,
                                         output_name=output_name)
        process_list.append(pc)

    return output_names, process_list


PROCESS_DICT[PROCESS_NAME] = get_process_list