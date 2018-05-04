"""mc prismspf full-simulation subcommand"""

import sys
import argparse
import prismspf_mcapi
from prismspf_mcapi.numerical_parameters import get_parameters_sample
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt

class FullSimulationSubcommand:
    desc = "(sample) PRISMS-PF Simulation"

    def __init__(self, argv):

        parser = argparse.ArgumentParser(
            description='Creates the entire set of input samples and processes for a simulation',
            prog='mc prismspf full-simulation')

        parser.add_argument('--create', action='store_true', help='Creates the input processes, input samples, and the simulation prcoess.')

        num_cores_help = "Add the number of cores to be used in the simulation"
        parser.add_argument('--num-cores', default=-1, help=num_cores_help)


        if argv[3] == '--create':
            self.create(parser, argv)
        else:
            parser.print_help()

    def create(self, parser, argv):
        out = sys.stdout

        proj = make_local_project()
        expt = make_local_expt(proj)

        sample_list = []

        proc = prismspf_mcapi.numerical_parameters.create_parameters_sample(expt, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')
        sample_list.extend(proc.output_samples)

        proc = prismspf_mcapi.model_parameters.create_parameters_sample(expt, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')
        sample_list.extend(proc.output_samples)

        args = parser.parse_args(argv[3:])
        proc = prismspf_mcapi.environment.create_environment_sample(expt, args, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')
        sample_list.extend(proc.output_samples)

        proc_list = prismspf_mcapi.equations.create_equations_sample(expt, args, verbose=True)
        for p in proc_list:
            out.write('Created process: ' + p.name + ' ' + p.id + '\n')
            sample_list.extend(p.output_samples)

        proc = prismspf_mcapi.software.create_software_sample(expt, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')
        sample_list.extend(proc.output_samples)

        out.write('List of samples created as inputs for the simulation sample:\n')
        for s in sample_list:
            out.write(s.name + ' ' + s.id + '\n')
        out.write('\n')

        proc = prismspf_mcapi.simulation.create_simulation_sample(expt, sample_list, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')
