# prismspf_mcapi
## PRISMS-PF - Materials Commons Interface

This is the initial version of the Materials Commons command-line-interface plugin for PRISMS-PF, which is still under active development. The base Materials Commons CLI can be found [here](https://github.com/materials-commons/mcapi/tree/master/python).

This plugin assists you in creating a Materials Commons representation of phase field simulations conducted with PRISMS-PF. From the directory of your PRISMS-PF app, it can create Materials Commons entities representing the governing equations, model parameters, numerical parameters, simulation software, and computing environment as well as the process for the phase field simulation itself. The metadata is populated by automatically parsing PRISMS-PF files and command-line arguments.

## Basic Instructions:

### Installation
- Install mcapi (`pip install mcapi`)
- Clone the prismspf_mcapi repository (`git clone https://github.com/prisms-center/prismspf_mcapi`, pip support coming soon)
- Add the location of the prismspf_mcapi to your Python path (`export PYTHONPATH=$PYTHONPATH:/path/to/prismspf_mcapi`)
- Add the interface information for PRISMS-PF to your .materialscommons/config.json file (typically found in your home directory). It should look like (possibly with other interfaces given as well):

        {
            "apikey": "[redacted, put your real api key here]",
            "mcurl": "https://materialscommons.org/api",
            "interfaces": [
               { "name": "prismspf",
                 "desc":"Create PRISMS-PF samples, processes, measurements, etc.",
                 "subcommand":"prismspf_subcommand",
                 "module":"prismspf_mcapi"
               }
            ]
        }

### Uploading metadata for a simulation (all at once)
- Go to the app directory for the PRISMS-PF simulation being conducted
- Enter at the command line: `mc prismspf full-simulation --create --num-cores N`, where N is the number of cores used in the simulation

### Uploading metadata for a simulation (each component seperately)
- Go to the app directory for the PRISMS-PF simulation being conducted
- Create the governing equations processes and samples: `mc prismspf equations --create`
- Create the model parameters process and sample: `mc prismspf model-parameters --create`
- Create the numerical parameters process and sample: `mc prismspf numerical-parameters --create`
- Create the simulation software process and sample: `mc prismspf software --create`
- Create the computing environment process and sample: `mc prismspf environment --create  --num-cores N`, where N is the number of cores used in the simulation
- Get the list of sample ids from the samples created in the previous steps: `mc samp`
- Create the phase field simulation process that takes all of the previously created samples as inputs: `mc prismspf simulation --create --input-sample-ids SAMPLE IDS`, where 'SAMPLE IDS' is replaced with a list of the sample ids from the input samples separated by spaces
