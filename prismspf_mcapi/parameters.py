"""mc prismspf parameters subcommand"""

import sys
import prismspf_mcapi
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt

def get_parameters_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a PRISMS-PF Numerical Parameters sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 PRISMS-PF Numerical Parameters samples exist in the experiment.

    Arguments:

        expt: mcapi.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        parameters: mcapi.Sample instance, or None
          A PRISMS-PF Numerical Parameters sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_parameters = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['parameters']]
        if len(candidate_parameters) == 0:
            out.write('Did not find a Numerical Parameters sample.\n')
            out.write('Use \'mc prismspf parameters --create\' to create a Numerical Parameters sample, or --parameters-id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_parameters) > 1:
            out.write('Found multiple Numerical Parameters samples:')
            for cand in candidate_parameters:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --parameters-id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        parameters_proc = candidate_parameters[0]
        parameters_proc.decorate_with_output_samples()
        return parameters_proc.output_samples[0]
    else:
        print("The sample id is: ")
        print(sample_id[0])
        parameters = expt.get_sample_by_id(sample_id[0])
    return parameters


def create_parameters_sample(expt, sample_name=None, verbose=False):
    """
    Create a PRISMS-PF Numerical Parameters Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        sample_name: str
          Name for sample, default is: Numerical Parameters

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    template_id = prismspf_mcapi.templates['parameters']

    print("The template ID is: " + template_id)
    ## Process that will create samples
    proc = expt.create_process_from_template(template_id)

    # Hardcoding the name of the template
    # proc = expt.create_process_from_template('global_Create Samples')

    proc.rename('Set_' + 'Numerical_Parameters')

    ## Create sample
    if sample_name is None:
        sample_name = "Numerical_Parameters"
    new_sample = proc.create_samples([sample_name])

    proc = expt.get_process_by_id(proc.id)

    # Sample attributes (how to check names?):
    parameter_list = parse_parameters_file()

    proc.add_number_measurement('Domain size (x)', parameter_list['Domain size (x)'])
    # proc.add_number_measurement('Domain size (y)', parameter_list['Domain size (y)'])
    # proc.add_number_measurement('Domain size (z)', parameter_list['Domain size (z)'])

    proc.add_integer_measurement('Element degree', 2)

    #new_sample[0].pretty_print()

    parameters_file = expt.project.add_file_by_local_path('parameters.in', verbose=verbose)  # I need to pass in the path to the PRISMS-PF app folder
    proc.add_files([parameters_file])

    return expt.get_process_by_id(proc.id)

def parse_parameters_file():
    # Starting out this will be a dummy function where I just set the parameters. Later I'll add the file parse_args
    parameter_list = {}
    parameter_list['Domain size (x)'] = 1
    parameter_list['Domain size (y)'] = 1
    parameter_list['Domain size (z)'] = 1

    return parameter_list

class ParametersSubcommand(ListObjects):
    desc = "(sample) PRISMS-PF Numerical Parameters"

    def __init__(self):
        super(ParametersSubcommand, self).__init__(["prismspf", "parameters"], "Numerical Parameters", "Numerical_Parameters",
            desc="Uploads parameters.in and creates an entity (sample) representing the numerical parameters.",
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
        proc = create_parameters_sample(expt, verbose=True)
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
