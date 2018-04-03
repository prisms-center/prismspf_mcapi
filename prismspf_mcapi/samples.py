"""Create Samples"""

def create_clex_sample(expt, casm_proj, prim, clex_desc):
    """
    Create a CASM Cluster Expansion Effective Hamiltonian Sample

    Assumes expt.project.path exists and adds files relative to that path.

    Arguments:

        expt: mcapi.Experiment instance

        casm_proj: casm.project.Project instance

        prim: mcapi.Sample instance
          Sample of type CASM "global_Primitive Crystal Structure"

        clex_desc: casm.project.ClexDescription instance

    Returns:

        proc: mcapi.Process instance
          The Process that created the sample
    """
    ## Create Sample
    proc = expt.create_process_from_template('global_Cluster Expansion Effective Hamiltonian')

    # "prim" (sample)
    proc.add_sample_measurement('prim', prim)

    # "bspecs" (file)
    mcfile = expt.project.add_file(casm_proj.dir.bspecs(clex_desc))
    proc.add_file_measurement('bspecs', mcfile)

    # "eci" (file)
    mcfile = expt.project.add_file(casm_proj.dir.eci(clex_desc))
    proc.add_file_measurement('eci', mcfile.id, mcfile.name)

    return mcapi.get_process_from_id(expt.project, expt, proc.id)

