# Copyright (C) 2023 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause

# Copyright (C) 2022 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions
# and limitations under the License.
#

import argparse
import sys
import os

from data.medical_data_prepare import data_preperation
from data.video_data_prep import ingest_multimodal

# from ref_utils.postprocess_functions import (
#     create_train_scores_json,
#     create_prediction_dict,
#     create_confusion_matrix_for_inference,
#     create_torch_model_archiver,
#     create_ensemble_workflow,
#     create_model_config_file,
#     create_model_snapshot,
# )

root_folder = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, os.path.join(root_folder, "nlp_classification_wf"))
# sys.path.insert(0, os.path.join(root_folder, "image_classification_wf"))

# from nlp_classification_wf.nlp_workload import nlp_main
# from image_classification_wf.vision_wl import vision_main


class CreateDictParam(argparse.Action):
    """
    This class is a custom action to be used in the argparse module.
    It takes in parameters in the form of key=value pairs and adds them to a dictionary.

    Inherits From:
    argparse.Action : The base class for action classes to be used with the argparse module.
    """

    def __call__(self, parser, input_params_names, param_pairs, option_string=None):
        """
        The method that is called when this action is specified.

        Parameters:
        parser : ArgumentParser
            The ArgumentParser object that this action is attached to.
        input_params_names : Namespace
            The Namespace object that holds the command line arguments.
        param_pairs : list
            The command line arguments that this action is responsible for.
        option_string : str, optional
            The option string that was used to invoke this action.
        """
        param_dict = getattr(input_params_names, self.dest) or {}

        if param_pairs:
            for item in param_pairs:
                key, value = item.split("=", 1)
                param_dict[key.strip()] = value

        setattr(input_params_names, self.dest, param_dict)


def set_parameters():
    """
    This function sets up the command line arguments for the script.

    Returns:
    argparse.Namespace
        The command line arguments parsed by argparse.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--set_workload",
        required=False,
        metavar="KEY=VALUE",
        nargs="+",
        help="Set multiple key-value pairs without spaces before or after the '=' sign. Enclose values with spaces in double quotes. All values are interpreted as strings.",
        action=CreateDictParam,
    )

    return parser.parse_args()


def set_output_folder(wl_params):
    wl_params["output_dir"] = os.path.join(
        wl_params["output_dir"], wl_params["workload_name"], wl_params["version"]
    )
    return wl_params


def main():
    """
    This function sets up the command line arguments for the script, runs the appropriate main function
    based on the specified use_case, and creates the necessary output files.

    Raises:
    ValueError: If 'use_case' is not defined or an unknown use_case is requested.
    """
    # Set the command line arguments
    params = set_parameters()
    print(">>> Parameters:", params)

    prediction_dict = {}
    for wl, use_case_params in vars(params).items():
        if use_case_params is not None:
            use_case = use_case_params.get("use_case")
            
            if use_case is None:
                raise ValueError(
                    "'use_case' is not defined."
                )

            data_prep_func = {
                "mm_rag_medical": data_preperation,
                "mm_rag_vision": ingest_multimodal,
                
            }.get(use_case)
            
            if data_prep_func is None:
                raise ValueError(
                    "Unknown data_prep_func request."
                )

            return data_prep_func(**use_case_params)
            
if __name__ == "__main__":
    df = main()
    
    print(df.head())
