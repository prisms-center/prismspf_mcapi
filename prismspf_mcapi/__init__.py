"""PRISMS-PF - Materials Commons interface"""

# from prismspf_mcapi.main import prismspf_subcommand
from .main import prismspf_subcommand


def set_templates(value=None):
    """
    Enable swapping out templates
    """
    global templates

    if value is None:
        # dictionary of cmdname -> template_id
        templates = {
          'parameters': 'global_Phase Field Simulation: Numerical Parameters',
          'simulation': 'global_Phase Field Simulation',
        }
    else:
        templates = value

# set default template ids
set_templates()

# specify the version of PRISMS-PF these functions work for
VERSION = "2.0.1"
MCAPI_NAME = "prismspf"
MCAPI_DESC = "Create and inspect PRISMS-PF samples, processes, measurements, etc."
MCAPI_MODULE = "prismspf_mcapi"
MCAPI_SUBCOMMAND = "prismspf_subcommand"

__all__ = [
    'MCAPI_NAME',
    'MCAPI_DESC',
    'prismspf_subcommand',
    'set_templates']
