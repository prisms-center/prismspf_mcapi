
#import sys

import materials_commons.api as mcapi

project_list = mcapi.get_all_projects()

for project in project_list:
    if project.name == 'PRISMS-PF API Test':
        current_project = project

experiment_list = current_project.get_all_experiments()

for experiment in experiment_list:
    if experiment.name == 'Experiment 0':
        print(experiment.name)
        current_experiment = experiment


template_list = mcapi.get_all_templates()
for template in template_list:
    print(template.name, template.id)

#experiment = project.create_experiment("Experiment 0", "Creating and modifying experiments using the API")
