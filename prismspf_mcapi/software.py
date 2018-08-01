"""mc prismspf software subcommand"""

import sys
import os.path
import subprocess
import prismspf_mcapi
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt


def get_software_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a PRISMS-PF Software sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 PRISMS-PF Software samples exist in the experiment.

    Arguments:

        expt: mcapi.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        software: mcapi.Sample instance, or None
          A PRISMS-PF Software sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_software = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['software']]
        if len(candidate_software) == 0:
            out.write('Did not find a Software sample.\n')
            out.write('Use \'mc prismspf software --create\' to create a Software sample, or --parameters-id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_software) > 1:
            out.write('Found multiple Software samples:')
            for cand in candidate_software:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --software-id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        software_proc = candidate_software[0]
        software_proc.decorate_with_output_samples()
        return software_proc.output_samples[0]
    else:
        # print("The sample id is: ")
        # print(sample_id[0])

        # This is broken, temporarily replaced by a more complicated work-around
        # software = expt.get_sample_by_id(sample_id)

        sample_found = False
        for proc in expt.get_all_processes():
            for sample in proc.get_all_samples():
                if sample.id == sample_id[0]:
                    # print("Sample found with id of: ", sample.id)
                    software = sample
                    sample_found = True
                    break
            if sample_found:
                break

    return software


def create_software_sample(expt, sample_name=None, verbose=False):
    """
    Create a PRISMS-PF Software Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        sample_name: str
          Name for sample, default is: Software

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    template_id = prismspf_mcapi.templates['software']

    print("The template ID is: " + template_id)
    ## Process that will create samples
    proc = expt.create_process_from_template(template_id)

    proc.rename('Set ' + 'Software')

    ## Create sample
    if sample_name is None:
        sample_name = "Software"
    new_sample = proc.create_samples([sample_name])

    proc = expt.get_process_by_id(proc.id)

    # Add the appropriate attributes

    # Assume for now that PRISMS-PF is the software being used
    proc.add_string_measurement('Simulation Software Name', 'PRISMS-PF')

    # Get the name of the current app (assumed to be the name of the current directory)
    app_name = os.path.basename(os.getcwd())
    proc.add_string_measurement('Simulation Software App Name', app_name)

    # Get the version
    if (os.path.isfile('../../version')):
        with open('../../version') as f:
            version = f.read()
        f.closed
    else:
        print('Did not find the \'version\' file where expected (two directories up from the current working directory). The version is being uploaded as \'unknown\'.\n')
        version = 'unknown'

    proc.add_string_measurement('Simulation Software Version', version)

    # Get the Git hash (if available)
    try:
        git_hash = subprocess.check_output(["git", "rev-parse", "HEAD"]).strip()
    except subprocess.CalledProcessError:
        print('Did not find git information connected to this project. The git hash is being uploaded as \'unknown\'.\n')
        git_hash = 'unknown'

    proc.add_string_measurement('Simulation Software Git Hash', git_hash)

    # new_sample[0].pretty_print(shift=0, indent=2, out=sys.stdout)


    return expt.get_process_by_id(proc.id)


class SoftwareSubcommand(ListObjects):
    desc = "(sample) PRISMS-PF Software"

    def __init__(self):
        super(SoftwareSubcommand, self).__init__(["prismspf", "software"], "Software", "Softwares",
            desc="Creates an entity (sample) representing the simulation software used for a phase field calculation.",
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
        proc = create_software_sample(expt, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')


    def add_create_options(self, parser):
        #some_option_help = "Some option help info"
        #parser.add_argument('--some_option', action="store_true", default=False, help=some_option_help)
        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
