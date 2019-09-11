# -*- coding: utf-8 -*-
from random import randint
import json

from openeo_grass_gis_driver.models.process_graph_schemas import ProcessGraphNode, ProcessGraph

from openeo_grass_gis_driver.actinia_processing.base import Node, check_node_parents
from openeo_grass_gis_driver.actinia_processing.base import PROCESS_DICT, PROCESS_DESCRIPTION_DICT
from openeo_grass_gis_driver.models.process_schemas import Parameter, ProcessDescription, ReturnValue, ProcessExample
from openeo_grass_gis_driver.actinia_processing.actinia_interface import ActiniaInterface

__license__ = "Apache License, Version 2.0"
__author__ = "Markus Metz"
__copyright__ = "Copyright 2018, Sören Gebbert, mundialis"
__maintainer__ = "Soeren Gebbert"
__email__ = "soerengebbert@googlemail.com"

PROCESS_NAME = "hants"


def create_process_description():
    p_data = Parameter(description="Any openEO process object that returns raster datasets "
                                   "or space-time raster dataset",
                       schema={"type": "object", "format": "eodata"},
                       required=True)
    p_nf = Parameter(description="The number of frequencies to use",
                             schema={"type": "object", "format": "integer"},
                             required=True)
    p_dod = Parameter(description="Degree of over-determination",
                             schema={"type": "object", "format": "integer"},
                             required=False)
    p_fet = Parameter(description="Fit error tolerance when filtering outliers",
                             schema={"type": "object", "format": "float"},
                             required=False)
    p_rangelo = Parameter(description="Ignore values below this limit",
                             schema={"type": "object", "format": "float"},
                             required=False)
    p_rangehi = Parameter(description="Ignore values above this limit",
                             schema={"type": "object", "format": "float"},
                             required=False)
    p_rejlo = Parameter(description="Reject low outliers",
                             schema={"type": "object", "format": "boolean"},
                             required=False)
    p_rejhi = Parameter(description="Reject high outliers",
                             schema={"type": "object", "format": "boolean"},
                             required=False)

    rv = ReturnValue(description="Processed EO data.",
                     schema={"type": "object", "format": "eodata"})

    # Example
    arguments = {"data": {"from_node": "get_strds_data"},
                 "nf": 6,
                 "dod": 2,
                 "fet": 0.1,
                 "range_low": -0.3,
                 "range_high": 0.9,
                 "reject_low": "true"
                 }
    node = ProcessGraphNode(process_id=PROCESS_NAME, arguments=arguments)
    graph = ProcessGraph(title="title", description="description", process_graph={"hants_1": node})
    examples = [ProcessExample(title="Simple example", description="Simple example",
                               process_graph=graph)]

    pd = ProcessDescription(id=PROCESS_NAME,
                            description="Apply Harmonic Analysis of Time-Series (HANTS) "
                                        "to a space-time raster dataset.",
                            summary="Apply HANTS to a space-time raster dataset.",
                            parameters={"data": p_data, "nf": p_nf, "dod": p_dod, "fet": p_fet,
                                        "range_low": p_rangelo, "range_high": p_rangehi,
                                        "reject_low": p_rejlo, "reject_high": p_rejhi},
                            returns=rv,
                            examples=examples)

    return json.loads(pd.to_json())


PROCESS_DESCRIPTION_DICT[PROCESS_NAME] = create_process_description()


def create_process_chain_entry(input_name, nf, dod, fet, range_low, range_high, reject_low, reject_high, output_name):
    """Create a Actinia process description that uses t.rast.hants 
    to filter a time series with HANTS.

    :param input_time_series: The input time series name
    :param nf: number of frequencies
    :param dod: degree of over-determination
    :param fet: fit-error tolerance
    :param range_low: lower limit of valid values
    :param range_high: upper limit of valid values
    :param reject_low: reject low outliers
    :param reject_high: reject high outliers
    :param output_map: The name of the output raster map
    :return: A Actinia process chain description
    """
    input_name = ActiniaInterface.layer_def_to_grass_map_name(input_name)

    rn = randint(0, 1000000)

    flags = ""
    if reject_low:
        flags = flags + 'l'
    if reject_high:
        flags = flags + 'h'

    hants_range = "%g,%g" % (range_low, range_high)

    if len(flags) > 0:
        pc = {"id": "t_rast_hants_%i" % rn,
              "module": "t.rast.hants",
              "inputs": [{"param": "input", "value": input_name},
                         {"param": "nf", "value": nf},
                         {"param": "dod", "value": dod},
                         {"param": "fet", "value": fet},
                         {"param": "range", "value": hants_range},
                         {"param": "output", "value": output_name}],
              "flags": flags}
    else:
        pc = {"id": "t_rast_hants_%i" % rn,
              "module": "t.rast.hants",
              "inputs": [{"param": "input", "value": input_name},
                         {"param": "nf", "value": nf},
                         {"param": "dod", "value": dod},
                         {"param": "fet", "value": fet},
                         {"param": "range", "value": hants_range},
                         {"param": "output", "value": output_name}]
              }

    return pc


def get_process_list(node: Node):
    """Analyse the process description and return the Actinia process chain
    and the name of the processing result layer
    which is a single raster layer

    :param node: The process node
    :return: (output_names, actinia_process_list)
    """

    input_names, process_list = check_node_parents(node=node)
    output_names = []

    if "nf" not in node.arguments:
        raise Exception("Parameter nf is required.")
    nf = int(node.arguments["nf"])
    dod = 0
    if "dod" in node.arguments:
        dod = int(node.arguments["dod"])
    fet = 1.7977e308
    if "fet" in node.arguments:
        fet = float(node.arguments["fet"])
    range_low = -1.7977e308
    if "range_low" in node.arguments:
        range_low = float(node.arguments["range_low"])
    range_high = 1.7977e308
    if "range_high" in node.arguments:
        range_high = float(node.arguments["range_high"])
    reject_low = False
    if "reject_low" in node.arguments:
        reject_low = bool(node.arguments["reject_low"])
    reject_high = False
    if "reject_high" in node.arguments:
        reject_high = bool(node.arguments["reject_high"])

    for input_name in node.get_parent_by_name("data").output_names:
        # multiple strds as input ?
        location, mapset, datatype, layer_name = ActiniaInterface.layer_def_to_components(input_name)
        output_name = "%s_%s" % (layer_name, PROCESS_NAME)
        output_names.append(output_name)
        node.add_output(output_name=output_name)

        pc = create_process_chain_entry(input_name, nf, dod, fet,
                                        range_low, range_high,
                                        reject_low, reject_high,
                                        output_name)
        process_list.append(pc)

    return output_names, process_list


PROCESS_DICT[PROCESS_NAME] = get_process_list