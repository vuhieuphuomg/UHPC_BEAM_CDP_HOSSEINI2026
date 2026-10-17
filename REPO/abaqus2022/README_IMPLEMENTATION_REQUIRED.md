# Abaqus 2022 builder — NOT IMPLEMENTED
The V5 package does not include validated Abaqus/CAE geometry/material scripts or a `.cae`. Claude must establish exact source geometry and CDP material, check installed Abaqus release and Python version, and implement a CONFIG-first builder. Do not import the V4 `abaqus_material_loader.py` blindly; source values and postpeak laws require independent QA. This folder is the required location for Abaqus 2022 kernel scripts. Scripts here must remain Python 2.7 syntax compatible unless local Abaqus reports otherwise.

Commands will become valid only after the required scripts exist and G0-G2 PASS:
`abaqus cae noGUI=abaqus2022/build_model.py -- --run-id <RUN_ID>`
`abaqus job=<RUN_ID> input=<RUN_ID>.inp datacheck interactive`
`abaqus job=<RUN_ID> input=<RUN_ID>.inp interactive`
`abaqus viewer noGUI=abaqus2022/post_odb.py -- --run-id <RUN_ID>`
Never treat these planned commands as proof the scripts exist or are tested.
