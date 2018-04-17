"""mc prismspf simulation subcommand"""

import sys
import prismspf_mcapi
from prismspf_mcapi.parameters import get_parameters_sample
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt

def get_simulation_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a PRISMS-PF Simulation sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 PRISMS-PF Simulation samples exist in the experiment.

    Arguments:

        expt: mcapi.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        simulation: mcapi.Sample instance, or None
          A PRISMS-PF Simulation sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_simulation = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['simulation']]
        if len(candidate_simulation) == 0:
            out.write('Did not find a Phase Field Simulation sample.\n')
            out.write('Use \'mc prismspf simulation --create\' to create a Simulation sample, or --simulation -id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_simulation) > 1:
            out.write('Found multiple Simulation samples:')
            for cand in candidate_simulation:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --simulation -id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        simulation_proc = candidate_simulation[0]
        simulation_proc.decorate_with_output_samples()
        return simulation_proc.output_samples[0]
    else:
        # This is broken, temporarily replaced by the first sample in the experiment
        simulation = expt.get_sample_by_id(sample_id)

    return simulation


def create_simulation_sample(expt, parameters_sample, sample_name=None, verbose=False):
    """
    Create a PRISMS-PF Simulation Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        parameters_sample: an mcapi.Sample object containing the numerical parameters for the simulation

        sample_name: str
          Name for sample, default is: Phase Field Simulation

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    template_id = prismspf_mcapi.templates['simulation']

    print("The template ID is: " + template_id)
    ## Process that will create samples
    proc = expt.create_process_from_template(template_id)

    # Hardcoding the name of the template
    # proc = expt.create_process_from_template('global_Create Samples')

    proc.rename('Run_' + 'Simulation')

    proc = expt.get_process_by_id(proc.id)

    print("Adding input sample(s)...")
    proc.add_input_samples_to_process([parameters_sample])
    print("Finshed adding input sample(s).")

    return expt.get_process_by_id(proc.id)


class SimulationSubcommand(ListObjects):
    desc = "(sample) PRISMS-PF Simulation"

    def __init__(self):
        super(SimulationSubcommand, self).__init__(["prismspf", "simulation"], "Simulation", "Simulations",
            desc="Creates an entity (sample) representing the simulation itself.",
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

        # Get the necessary input samples
        parameters_sample = get_parameters_sample(expt, args.parameters_id, out)

        proc = create_simulation_sample(expt, parameters_sample, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')


    def add_create_options(self, parser):
        parameters_id_help = "Specify parameters sample id explicitly"
        parser.add_argument('--parameters-id', nargs='*', default=None, help=parameters_id_help)

        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
