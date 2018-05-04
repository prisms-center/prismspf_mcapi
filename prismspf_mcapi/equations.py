"""mc prismspf equations subcommand"""

import sys
import os.path
import subprocess
import prismspf_mcapi
from prismspf_mcapi.equations_dot_h_parser import parse_equations_file
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt


class EquationInformation:
    def __init__(self, _index):
        index = _index
        name = 'var'
        type = 'SCALAR'
        eq_type = 'PARABOLIC'


def get_equations_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a PRISMS-PF Equations sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 PRISMS-PF Equations samples exist in the experiment.

    Arguments:

        expt: mcapi.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        software: mcapi.Sample instance, or None
          A PRISMS-PF Equations sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_equations = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['environment']]
        if len(candidate_equations) == 0:
            out.write('Did not find a Equations sample.\n')
            out.write('Use \'mc prismspf equations --create\' to create a Equations sample, or --environment-id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_equations) > 1:
            out.write('Found multiple Equations samples:')
            for cand in candidate_equations:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --equations-id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        equations_proc = candidate_equations[0]
        equations_proc.decorate_with_output_samples()
        return equations_proc.output_samples[0]
    else:
        # print("The sample id is: ")
        # print(sample_id[0])

        # This is broken, temporarily replaced by a more complicated work-around
        # environment = expt.get_sample_by_id(sample_id)

        sample_found = False
        for proc in expt.get_all_processes():
            for sample in proc.get_all_samples():
                if sample.id == sample_id[0]:
                    # print("Sample found with id of: ", sample.id)
                    equations = sample
                    sample_found = True
                    break
            if sample_found:
                break

    return equations


def create_equations_sample(expt, args, sample_name=None, verbose=False):
    """
    Create a PRISMS-PF Equations Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        sample_name: str
          Name for sample, default is: Equations

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    template_id = prismspf_mcapi.templates['equations']

    print("The template ID is: " + template_id)

    # This function is different than the others, it will create one process and one sample for each variable/governing equation

    # First, parse the equations file
    file_name = "equations.h"
    equation_information_list = parse_equations_file(file_name)

    # Second, create a sample for each variable/equation
    new_sample_list = []
    proc_list = []
    for equation_information in equation_information_list:
        # Process that will create samples
        proc = expt.create_process_from_template(template_id)

        proc.rename('Set ' + 'Equations: ' + equation_information.name)

        if sample_name is None:
            full_sample_name = "Equations"

        full_sample_name = full_sample_name + ": " + equation_information.name

        new_sample_list.append(proc.create_samples([full_sample_name]))

        proc.add_string_measurement('Variable Name', equation_information.name)
        proc.add_string_measurement('Variable Index', equation_information.index)
        proc.add_string_measurement('Variable Type', equation_information.type)
        proc.add_string_measurement('Variable Equation Type', equation_information.equation_type)

        equations_file = expt.project.add_file_by_local_path(file_name, verbose=verbose)
        proc.add_files([equations_file])

        proc_list.append(proc)

        # new_sample_list[-1][0].pretty_print(shift=0, indent=2, out=sys.stdout)

    return proc_list


class EquationsSubcommand(ListObjects):
    desc = "(sample) PRISMS-PF Software"

    def __init__(self):
        super(EquationsSubcommand, self).__init__(["prismspf", "equations"], "Equations", "Equations", desc="Creates a set of entities (samples) representing the variables and governing equations for a phase field calculation.", expt_member=True, list_columns=['name', 'owner', 'template_name', 'id', 'mtime'], creatable=True)

    def get_all_from_experiment(self, expt):
        return [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates[self.cmdname[-1]]]

    def get_all_from_project(self, proj):
        return [proc for proc in proj.get_all_processes() if proc.template_id == prismspf_mcapi.templates[self.cmdname[-1]]]

    def create(self, args, out=sys.stdout):
        proj = make_local_project()
        expt = make_local_expt(proj)
        proc_list = create_equations_sample(expt, args, verbose=True)

        for proc in proc_list:
            out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')

    def add_create_options(self, parser):
        """
        """

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
