"""
write_input.py — Write Abaqus .inp file from CAE model.

NOT_TESTED_IN_ABAQUS: requires `abaqus cae noGUI script=...` to verify.

solver_authorized=false: this module ONLY writes the .inp file.
It does NOT submit the job. Submission requires explicit engineer action.
"""

import os

try:
    from abaqus import mdb
    from abaqusConstants import ANALYSIS
    _IN_ABAQUS = True
except ImportError:
    _IN_ABAQUS = False


def write_inp(model_name, job_name, output_dir,
              description="UHPC T-beam CDP G2 preparation"):
    """
    Write .inp file for the specified model.
    Does NOT submit. solver_authorized=false.

    Args:
        model_name: mdb model name string
        job_name: Abaqus job name (output file base name)
        output_dir: directory to write .inp into
        description: job description string

    Returns path to written .inp file.
    NOT_TESTED_IN_ABAQUS.
    """
    if not _IN_ABAQUS:
        raise RuntimeError("write_input must run inside Abaqus CAE kernel")

    inp_path = os.path.join(output_dir, job_name + ".inp")

    job = mdb.Job(
        name=job_name,
        model=model_name,
        type=ANALYSIS,
        description=description,
        numCpus=1,
        numGPUs=0,
    )
    job.writeInput(consistencyChecking=ON)

    # Move written .inp to output_dir if not already there
    default_inp = job_name + ".inp"
    if os.path.isfile(default_inp) and default_inp != inp_path:
        import shutil
        shutil.move(default_inp, inp_path)

    print("INP written: {0}".format(inp_path))
    print("solver_authorized=false — do NOT submit without engineer approval")
    return inp_path
