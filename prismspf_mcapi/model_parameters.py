"""mc prismspf model-parameters subcommand"""

import sys
import prismspf_mcapi
from prismspf_mcapi.prismspf_parameter_parser import parse_parameters_file
from materials_commons.cli import ListObjects
from materials_commons.cli.functions import make_local_project, make_local_expt


def get_parameters_sample(expt, sample_id=None, out=sys.stdout):
    """
    Return a PRISMS-PF Model Parameters sample from provided Materials Commons
    experiment and optionally explicit sample id. Returns None if sample_id is None
    and zero or >1 PRISMS-PF Model Parameters samples exist in the experiment.

    Arguments:

        expt: mcapi.Experiment object

        sample_id: str, optional (default=None)
          Sample id to use explicitly

    Returns:

        parameters: mcapi.Sample instance, or None
          A PRISMS-PF Model Parameters sample, or None if not found uniquely

    """
    if sample_id is None:
        candidate_parameters = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['model_parameters']]
        if len(candidate_parameters) == 0:
            out.write('Did not find a model Parameters sample.\n')
            out.write('Use \'mc prismspf model-parameters --create\' to create a Model Parameters sample, or --parameters-id <id> to specify explicitly.\n')
            out.write('Aborting\n')
            return None
        if len(candidate_parameters) > 1:
            out.write('Found multiple Model Parameters samples:')
            for cand in candidate_parameters:
                out.write(cand.name + '  id: ' + cand.id + '\n')
            out.write('Use --parameters-id <id> to specify explicitly\n')
            out.write('Aborting\n')
            return None
        parameters_proc = candidate_parameters[0]
        parameters_proc.decorate_with_output_samples()
        return parameters_proc.output_samples[0]
    else:
        # print("The sample id is: ")
        # print(sample_id[0])

        # This is broken, temporarily replaced by a more complicated work-around
        # parameters = expt.get_sample_by_id(sample_id)

        sample_found = False
        for proc in expt.get_all_processes():
            for sample in proc.get_all_samples():
                if sample.id == sample_id[0]:
                    # print("Sample found with id of: ", sample.id)
                    parameters = sample
                    sample_found = True
                    break
            if sample_found:
                break

    return parameters


def create_parameters_sample(expt, args, process_name=None, sample_name=None, verbose=False):
    """
    Create a PRISMS-PF Model Parameters Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment object

        sample_name: str
          Name for sample, default is: Model Parameters

        verbose: bool
          Print messages about uploads, etc.

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    template_id = prismspf_mcapi.templates['model-parameters']

    print("The template ID is: " + template_id)
    ## Process that will create samples
    proc = expt.create_process_from_template(template_id)

    if process_name is None:
        proc.rename('Set Model Parameters')
    else:
        proc.rename(process_name)

    ## Create sample
    if sample_name is None:
        sample_name = "Model Parameters"
    new_sample = proc.create_samples([sample_name])

    proc = expt.get_process_by_id(proc.id)

    parameter_dictionary = parse_parameters_file()

    model_constant_prefix = 'Model constant'

    for entry in parameter_dictionary:
        if entry[:len(model_constant_prefix)] == model_constant_prefix:
            parameter_value_type_set = parameter_dictionary[entry]
            parameter_description = entry[len(model_constant_prefix):].strip()

            split_parameter_value_type_set = parameter_value_type_set.split(',')
            parameter_type = split_parameter_value_type_set[-1]

            single_parameter_types = ['double', 'int', 'bool']

            '''
            if parameter_type.casefold() in single_parameter_types:
                if parameter_type.casefold() == 'double':
                    proc.add_number_measurement(parameter_description, split_parameter_value_type_set[0])
                elif parameter_type.casefold() == 'int':
                    proc.add_integer_measurement(parameter_description, split_parameter_value_type_set[0])
                elif parameter_type.casefold() == 'bool':
                    proc.add_boolean_measurement(parameter_description, split_parameter_value_type_set[0])
            else:
                # For tensors and elastic constants (currently just a string is uploaded, in the future I'd like to do much more formatting)
                proc.add_string_measurement(parameter_description, ', '.join(split_parameter_value_type_set[:-1]))
            '''
            if parameter_type.casefold() in single_parameter_types:
                proc.add_string_measurement(parameter_description, split_parameter_value_type_set[0])
            else:
                # For tensors and elastic constants (currently just a string is uploaded, in the future I'd like to do much more formatting)
                proc.add_string_measurement(parameter_description, ', '.join(split_parameter_value_type_set[:-1]))

    # new_sample[0].pretty_print(shift=0, indent=2, out=sys.stdout)

    parameters_file = expt.project.add_file_by_local_path('parameters.in', verbose=verbose)  # I need to pass in the path to the PRISMS-PF app folder
    parameters_file.direction = "in"
    proc.add_files([parameters_file])

    for sample in new_sample:
        sample.link_files([parameters_file])

    return expt.get_process_by_id(proc.id)


class ModParametersSubcommand(ListObjects):
    desc = "(sample) PRISMS-PF Model Parameters"

    def __init__(self):
        super(ModParametersSubcommand, self).__init__(["prismspf", "model-parameters"], "Model Parameters", "Model Parameters",
            desc="Uploads parameters.in and creates an entity (sample) representing the model parameters.",
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

        if args.proc_name is None:
            proc_name = None
        else:
            proc_name = " ".join(args.proc_name)

        if args.samp_name is None:
            samp_name = None
        else:
            samp_name = " ".join(args.samp_name)

        proc = create_parameters_sample(expt, args, proc_name, samp_name, verbose=True)
        out.write('Created process: ' + proc.name + ' ' + proc.id + '\n')


    def add_create_options(self, parser):
        sample_name_help = "Set the name of the output sample"
        parser.add_argument('--samp-name', nargs='*', default=None, help=sample_name_help)

        process_name_help = "Set the name of the process"
        parser.add_argument('--proc-name', nargs='*', default=None, help=process_name_help)

        return

    def list_data(self, obj):
        return {
            'name': _trunc_name(obj),
            'owner': obj.owner,
            'template_name': obj.template_name,
            'id': obj.id,
            'mtime': _format_mtime(obj.mtime)
        }
