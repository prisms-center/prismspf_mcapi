"""Create Processes"""
# It is unclear if this file is actually needed
import os
import json
import numpy as np
import mcapi


def create_set_numerical_parameters(expt, settings_local_abspath,
                                    numerical_parameters_sample):
    """
    Create a PRISMS-PF "Set Numerical Parameters" process and upload associated
        parameters file.

    Assumes expt.project.path exists and adds files relative to that path.
    Arguments:
        expt: mcapi.Experiment object
        settings_local_abspath: Path to PRISMS-PF parameters file. Results
             are expected in the same directory.
        numerical_parameters_sample: Numerial Parameters sample
    Returns:
        proc: mcapi.Process
    """
