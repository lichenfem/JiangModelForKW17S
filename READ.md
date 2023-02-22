The analysis flow: (Mind that / for linux, \ for windows, pls modify accordingly)

step 1:
update settings in "setGeomAndMatr.py" accordingly, then run
"python3 setGeomAndMatr.py"
this generates "ellipticalWireProfilesOfUncompactedStrand.json" (contains
elliptical wire profiles for all wires in the strand)
and 
"configuration.json"(contains all variables regarding to the configuration)
and
"profileOfBasicSectorBeforeCompaction.json" (contain profiles of wires in the basic sector)
and
"setL1L2ForProfileOfBasicSectorBeforeCompaction.json"(contain detection of L1/L2/L1L2 nodes for the profiles of wires in the basic sector);
what is also generated is a figure called 'L1L2DesignationOfProfileNodes.png',
It shows the classification of boundary points of the profiles of wires in the basic sector into 'L1', 'L2', 'L1L2'.


step 2:
in command line of windows (ctrl+R->cmd), locate to the work directory, 
run following command, make sure 'ropemodels' environment variable of Python (in PYTHONPATH)
is set to the correct directory:
cd workdir
"abaqus cae noGUI=modelCompactionInAbaqus.py -- .\configuration.json" (win)
"abaqus cae noGUI=modelCompactionInAbaqus.py -- ./configuration.json" (linux)
This script builds cae model for compaction in abaqus.

step 3:
Navigate to subfolder 'compaction', 
in command line of windows (ctrl+R->cmd), locate to the 'compaction' directory using cd command, 
run in the command line the following command:
"abaqus job=compaction input=compaction.inp cpus=4 interactive"
The above command will kick off the compaction simulation.


step 4:
navigate to the working directory, and run the following command
"abaqus cae noGUI=postprocessCompactionInAbq.py -- .\compaction\compaction.odb  .\compaction\ElemNodalInfoForCmpSimu.csv  .\compaction\PEEQAtIntPtForCmpSimu.csv .\compaction\compaction.cae .\compaction\L1L2SetNamesAndCoordinates.json" (win)
This command outputs the PEEQ fields, the deformed shape, the designation of nodes as L1 and L2.


step 5:
navigate to the working directory, and run the following command
"python3 genHardini.py .\compaction\PEEQAtIntPtForCmpSimu.csv .\configuration.json .\hardini_partialSec.f" (win)
"python3 genHardini.py ./compaction/PEEQAtIntPtForCmpSimu.csv ./configuration.json ./hardini_partialSec.f" (linux)
This generates the user subroutine while will be used to derive the initial PEEQ field for tension simulation.

step 6:
navigate to the working directory, and run the following command
"python3 genCompactedProfileOfBasicSector.py ./compaction/ElemNodalInfoForCmpSimu.csv ./compaction/L1L2SetNamesAndCoordinates.json ./profileOfBasicSectorAfterCompaction.json ./setL1L2ForProfileOfBasicSectorAfterCompaction.json ./L1L2DesignationOfProfileNodesAfterCompaction.png" (linux)


step 7:
navigate to the working directory, and run the following command
"abaqus cae noGUI=modelTensionInAbaqus.py -- .\configuration.json" (win)


step 8:
Navigate to subfolder 'tension', 
in command line of windows (ctrl+R->cmd), locate to the 'tension' directory using cd command, 
"abaqus job=tension input=tension.inp cpus=4 user=..\hardini_partialSec.f interactive" (win)
This step will compile the fortran script which will take dozens of minutes.


step 9:
Navigate to the work directory, open cmd window, run following commands
"
cd workdir
abaqus cae noGUI=postprocessTensionInAbq.py -- .\tension\tension.odb .\tension
" (win)
This step generates csv files for each frame in workdir/tension folder.

step 10:
Navigate to the work directory, open a terminal and run following command, note module sklearn is needed.
"python3 postprocessTensionOutAbq.py  ./configuration.json ./tension  ./tension/FU.json"(linux)
This generates './tension/FU.json' where strain (x axis) and forces (y axis) are use to plot x, y curve.

------------------------------------------------------------
commands to run on UniLu HPC:


available packgaes on UniLu HPC using 'module keyword packageName':
lang/Python: lang/Python/2.7.18-GCCcore-10.2.0, lang/Python/3.8.6-GCCcore-10.2.0
lang/SciPy-bundle: lang/SciPy-bundle/2020.11-foss-2020b-Python-2.7.18, lang/SciPy-bundle/2020.11-foss-2020b, ...
cae/ABAQUS: cae/ABAQUS/2021-hotfix-2207

module load cae/ABAQUS/2021-hotfix-2207
module load lang/Python
module load lang/SciPy-bundle

------------------------------------------------------------
Third party Python packages:
python3 -m pip install --user shapely
python3 -m pip install --user sympy
python3 -m pip install --user matplotlib








