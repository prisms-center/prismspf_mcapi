"""mc prismspf software subcommand"""

import sys
import os.path
import subprocess
import prismspf_mcapi
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt


def get_environment_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a PRISMS-PF Computing Environment sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 PRISMS-PF Software samples exist in the experiment.

    Arguments:

        expt: mcapi.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        software: mcapi.Sample instance, or None
          A PRISMS-PF Computing Environment sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_environment = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['environment']]
        if len(candidate_environment) == 0:
            out.write('Did not find a Computing Environment sample.\n')
            out.write('Use \'mc prismspf environment --create\' to create a Software sample, or --environment-id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_environment) > 1:
            out.write('Found multiple Computing Environment samples:')
            for cand in candidate_environment:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --environment-id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        environment_proc = candidate_environment[0]
        environment_proc.decorate_with_output_samples()
        return environment_proc.output_samples[0]
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
                    environment = sample
                    sample_found = True
                    break
            if sample_found:
                break

    return environment


def create_environment_sample(expt, args, sample_name=None, verbose=False):
    """
    Create a PRISMS-PF Computing Environment Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        sample_name: str
          Name for sample, default is: Computing Environment

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    template_id = prismspf_mcapi.templates['environment']

    print("The template ID is: " + template_id)
    ## Process that will create samples
    proc = expt.create_process_from_template(template_id)

    proc.rename('Set ' + 'Computing Environment')

    ## Create sample
    if sample_name is None:
        sample_name = "Computing Environment"
    new_sample = proc.create_samples([sample_name])

    proc = expt.get_process_by_id(proc.id)

    # Add the appropriate attributes

    # Add the number of cores
    if int(args.num_cores[0]) > 0:
        # proc.add_integer_measurement('Number of simulation cores', int(args.num_cores[0]))
        proc.add_string_measurement('Number of simulation cores', args.num_cores[0])
    else:
        raise ValueError("The number of simulation cores must be explicitly given and must be > 0.")

    # Get the computer name (if available) and add it
    try:
        machine_name = subprocess.check_output("hostname").strip()  # Note: subprocess.check_output() yields a binary sequence of bytes, not a string
    except subprocess.CalledProcessError:
        print('Did not find the computer name. The computer name is being uploaded as \'unknown\'.\n')
        machine_name = 'unknown'

    proc.add_string_measurement('Computer name', machine_name.decode('ascii'))

    # new_sample[0].pretty_print(shift=0, indent=2, out=sys.stdout)

    return expt.get_process_by_id(proc.id)


class EnvironmentSubcommand(ListObjects):
    desc = "(sample) PRISMS-PF Software"

    def __init__(self):
        super(EnvironmentSubcommand, self).__init__(["prismspf", "software"], "Environment", "Environments",
            desc="Creates an entity (sample) representing the computing enviroment used for a phase field calculation.",
            expt_member=True,
            list_columns=['name', 'owner', 'template_name', 'id', 'mtime'],
            creatable=True)

    def get_all_from_experiment(self, expt):
        return [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates[self.cmdname[-1]]]

    def get_all_from_project(self, proj):
        return [proc for proc in proj.get_all_processes() if proc.template_id == prismspf_mcapi.templates[self.cmdname[-1]]]

    def create(self, args, out=sys.stdout):
        proj = make_local_project()
        expt = make_local_expt(proj)
        proc = create_environment_sample(expt, args, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')


    def add_create_options(self, parser):
        num_cores_help = "Add the number of cores to be used in the simulation"
        parser.add_argument('--num-cores', default=-1, help=num_cores_help)
        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
