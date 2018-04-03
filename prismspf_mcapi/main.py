"""CASM - Materials Commons CLI"""

import argparse
import sys
import StringIO
from prismspf_mcapi.parameters import ParametersSubcommand

#import prismspf_mcapi.samples

prismspf_usage = [
    {'name':'parameters', 'desc': ParametersSubcommand.desc, 'subcommand': ParametersSubcommand()}
]

def prismspf_subcommand(argv=sys.argv):
    usage_help = StringIO.StringIO()
    usage_help.write("mc prismspf <command> [<args>]\n\n")
    usage_help.write("The mc prismspf commands are:\n")

    for interface in prismspf_usage:
        usage_help.write("  {:20} {:40}\n".format(interface['name'], interface['desc']))
    interfaces = {d['name']: d for d in prismspf_usage}

    parser = argparse.ArgumentParser(
        description='Materials Commons - PRISMS-PF command line interface',
        usage=usage_help.getvalue())
    parser.add_argument('command', help='Subcommand to run')

    if len(argv) < 3:
        parser.print_help()
        return

    # parse_args defaults to [1:] for args, but you need to
    # exclude the rest of the args too, or validation will fail
    args = parser.parse_args(argv[2:3])

    if args.command in interfaces:
        interfaces[args.command]['subcommand'](argv)
    else:
        print('Unrecognized command')
        parser.print_help()
        exit(1)
