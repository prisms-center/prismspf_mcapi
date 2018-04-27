"""mc prismspf parameters subcommand"""

import sys
import prismspf_mcapi
from prismspf_mcapi.prismspf_parameter_parser import parse_parameters_file
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
        # This is broken, temporarily replaced by the first sample in the experiment
        #parameters = expt.get_sample_by_id(sample_id)

        # Temp hack-y fix
        candidate_parameters = [proc for proc in expt.get_all_processes() if proc.template_id == prismspf_mcapi.templates['parameters']]
        parameters_proc = candidate_parameters[0]
        parameters_proc.decorate_with_output_samples()
        return parameters_proc.output_samples[0]

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

    proc.rename('Set_' + 'Numerical_Parameters')

    ## Create sample
    if sample_name is None:
        sample_name = "Numerical_Parameters"
    new_sample = proc.create_samples([sample_name])

    proc = expt.get_process_by_id(proc.id)

    # Populate the list of numerical parameter descriptors used in parameters.in (skipping anything in a subsection for now)
    # The order of entries is "descriptor string in parameters.in", "type", "default value", "the subsection name" (if applicable)
    parameter_descriptor_list = []
    parameter_descriptor_list.append(('Domain size X', 'double', '-1', ''))
    parameter_descriptor_list.append(('Domain size Y', 'double', '-1', ''))
    parameter_descriptor_list.append(('Domain size Z', 'double', '-1', ''))
    parameter_descriptor_list.append(('Element degree', 'int', '1', ''))
    parameter_descriptor_list.append(('Number of dimensions', 'int', '-1', ''))
    parameter_descriptor_list.append(('Subdivisions X', 'int', '1', ''))
    parameter_descriptor_list.append(('Subdivisions Y', 'int', '1', ''))
    parameter_descriptor_list.append(('Subdivisions Z', 'int', '1', ''))
    parameter_descriptor_list.append(('Refine factor', 'int', '-1', ''))
    parameter_descriptor_list.append(('Mesh adaptivity', 'bool', 'false', ''))
    parameter_descriptor_list.append(('Max refinement level', 'int', '-1', ''))
    parameter_descriptor_list.append(('Min refinement level', 'int', '-1', ''))
    parameter_descriptor_list.append(('Refinement criteria fields', 'string', '', ''))  # Actually a list of strings
    parameter_descriptor_list.append(('Refinement window max', 'string', '', ''))  # Actually a list of doubles
    parameter_descriptor_list.append(('Refinement window min', 'string', '', ''))  # Actually a list of doubles
    parameter_descriptor_list.append(('Steps between remeshing operations', 'int', '1', ''))
    parameter_descriptor_list.append(('Number of time steps', 'int', '-1', ''))
    parameter_descriptor_list.append(('Time step', 'double', '0', ''))
    parameter_descriptor_list.append(('Simulation end time', 'double', '0', ''))
    parameter_descriptor_list.append(('Output file name (base)', 'string', 'solution', ''))
    parameter_descriptor_list.append(('Output file type', 'string', 'vtu', ''))
    parameter_descriptor_list.append(('Output separate files per process', 'bool', 'false', ''))
    parameter_descriptor_list.append(('Output condition', 'string', 'EQUAL_SPACING', ''))
    parameter_descriptor_list.append(('List of time steps to output', 'string', '0', ''))  # Actually a list of ints
    parameter_descriptor_list.append(('Number of outputs', 'int', '10', ''))
    parameter_descriptor_list.append(('Skip print steps', 'int', '1', ''))
    parameter_descriptor_list.append(('Load initial conditions', 'bool', 'false', ''))
    parameter_descriptor_list.append(('Load parallel file', 'bool', 'false', ''))
    parameter_descriptor_list.append(('File names', 'string', '', ''))  # Actually a list of strings
    parameter_descriptor_list.append(('Variable names in the files', 'string', '', ''))  # Actually a list of strings
    parameter_descriptor_list.append(('Load from a checkpoint', 'bool', 'false', ''))
    parameter_descriptor_list.append(('Checkpoint condition', 'string', 'EQUAL_SPACING', ''))
    parameter_descriptor_list.append(('List of time steps to save checkpoints', 'string', '0', ''))  # Actually a list of ints
    parameter_descriptor_list.append(('Number of checkpoints', 'int', '1', ''))

    parameter_descriptor_list.append(('Tolerance type', 'string', 'RELATIVE_RESIDUAL_CHANGE', 'Linear solver parameters:'))
    parameter_descriptor_list.append(('Tolerance value', 'double', '1.0e-10', 'Linear solver parameters:'))
    parameter_descriptor_list.append(('Maximum linear solver iterations', 'int', '1000', 'Linear solver parameters:'))

    parameter_descriptor_list.append(('Maximum nonlinear solver iterations', 'int', '100', ''))
    parameter_descriptor_list.append(('Tolerance type', 'string', 'ABSOLUTE_CHANGE', 'Nonlinear solver parameters:'))
    parameter_descriptor_list.append(('Tolerance value', 'double', '1.0e-10', 'Nonlinear solver parameters:'))
    parameter_descriptor_list.append(('Use backtracking line search damping', 'bool', 'true', 'Nonlinear solver parameters:'))
    parameter_descriptor_list.append(('Backtracking step size modifier', 'double', '0.5', 'Nonlinear solver parameters:'))
    parameter_descriptor_list.append(('Backtracking residual decrease coefficient', 'double', '1.0', 'Nonlinear solver parameters:'))
    parameter_descriptor_list.append(('Constant damping value', 'double', '1.0', 'Nonlinear solver parameters:'))
    parameter_descriptor_list.append(('Use Laplace\'s equation to determine the initial guess', 'bool', 'false', 'Nonlinear solver parameters:'))

    parameter_descriptor_list.append(('Minimum allowed distance between nuclei', 'double', '-1', ''))
    parameter_descriptor_list.append(('Order parameter cutoff value', 'double', '0.01', ''))
    parameter_descriptor_list.append(('Time steps between nucleation attempts', 'int', '100', ''))

    parameter_descriptor_list.append(('Nucleus semiaxes (x, y, z)', 'string', '0,0,0', 'Nucleation parameters:'))  # Actually a list of doubles
    parameter_descriptor_list.append(('Nucleus rotation in degrees (x, y, z)', 'string', '0,0,0', 'Nucleation parameters:'))  # Actually a list of doubles
    parameter_descriptor_list.append(('Freeze zone semiaxes (x, y, z)', 'string', '0,0,0', 'Nucleation parameters:'))  # Actually a list of doubles
    parameter_descriptor_list.append(('Freeze time following nucleation', 'double', '0', 'Nucleation parameters:'))
    parameter_descriptor_list.append(('Nucleation-free border thickness', 'double', '0', 'Nucleation parameters:'))


    parameter_dictionary = parse_parameters_file()

    for parameter_descriptor in parameter_descriptor_list:
        # The standard case where a parameter is directly set in the parameters file
        if parameter_descriptor[0] in parameter_dictionary:
            parameter_value = parameter_dictionary[parameter_descriptor[0]]
            parameter_description = parameter_descriptor[0]

            if parameter_descriptor[1] == 'double':
                proc.add_number_measurement(parameter_description, parameter_value)
            elif parameter_descriptor[1] == 'int':
                proc.add_integer_measurement(parameter_description, parameter_value)
            elif parameter_descriptor[1] == 'string':
                proc.add_string_measurement(parameter_description, parameter_value)
            elif parameter_descriptor[1] == 'bool':
                proc.add_boolean_measurement(parameter_description, parameter_value)

        # The default value if the parameter isn't set in the parameters file
        elif len(parameter_descriptor[3]) < 1:
            parameter_value = parameter_descriptor[2]
            parameter_description = parameter_descriptor[0]

            if parameter_descriptor[1] == 'double':
                proc.add_number_measurement(parameter_description, parameter_value)
            elif parameter_descriptor[1] == 'int':
                proc.add_integer_measurement(parameter_description, parameter_value)
            elif parameter_descriptor[1] == 'string':
                proc.add_string_measurement(parameter_description, parameter_value)
            elif parameter_descriptor[1] == 'bool':
                proc.add_boolean_measurement(parameter_description, parameter_value)

        else:
            # Need to find all versions of the parameters in subsections
            base_subsection_name = parameter_descriptor[3]
            base_subsection_name = base_subsection_name[:-1]

            for entry in parameter_dictionary:
                if entry[:len(base_subsection_name)] == base_subsection_name and entry[-len(parameter_descriptor[0]):] == parameter_descriptor[0]:
                    parameter_value = parameter_dictionary[entry]
                    parameter_description = entry

                    if parameter_descriptor[1] == 'double':
                        proc.add_number_measurement(parameter_description, parameter_value)
                    elif parameter_descriptor[1] == 'int':
                        proc.add_integer_measurement(parameter_description, parameter_value)
                    elif parameter_descriptor[1] == 'string':
                        proc.add_string_measurement(parameter_description, parameter_value)
                    elif parameter_descriptor[1] == 'bool':
                        proc.add_boolean_measurement(parameter_description, parameter_value)




    # new_sample[0].pretty_print(shift=0, indent=2, out=sys.stdout)

    parameters_file = expt.project.add_file_by_local_path('parameters.in', verbose=verbose)  # I need to pass in the path to the PRISMS-PF app folder
    proc.add_files([parameters_file])

    return expt.get_process_by_id(proc.id)

"""
def parse_parameters_file(parameter_descriptor_list):
    # Starting out this will be a dummy function where I just set the parameters. Later I'll add the file parse_args
    parameter_dictionary = {}
    parameter_dictionary['Domain size (x)'] = 1.0
    parameter_dictionary['Domain size (y)'] = 1.0
    parameter_dictionary['Domain size (z)'] = 1.0
    parameter_dictionary['Element degree'] = 2

    return parameter_dictionary
"""

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
