import os
import sys
import json
import numpy as np
import time


def genInpForTensionSimu(settingJson):
    """
    generate inp file for tension simulation
    @param settingJson: str, path of setting file
    @return: none
    """
    # loading settings
    a_file = open(settingJson, 'r')
    settings = json.load(a_file)  # settings is a dict
    a_file.close()

    # create necessary folder if required
    try:
        os.mkdir(os.path.join(settings['workdir'], 'tension'))
    except Exception:
        pass
    try:
        os.mkdir(os.path.join(settings['workdir'], 'tension', 'debugDataFiles'))
    except Exception:
        pass

    # create list of materials
    from source.classes.Material import createMaterialListsForIsoPlas
    materialPerLayer = createMaterialListsForIsoPlas(pathsToCalibratedData=settings['pathsToCalibratedData'],
                                                     materialNames=settings['materialNames'],
                                                     poissonRatios=settings['poissonRatios'],
                                                     densities=settings['densities'])

    # set loading controls
    from source.classes.StaticLoading import StaticLoading
    loading = StaticLoading(typeOfLoadingApplied='tension',
                            minInc=1e-8,
                            maxInc=0.05,
                            initialInc=1e-3,    # preset
                            targetAxialStrain=settings['targetAxialStrain'],
                            )

    # create strand object
    wireProfilesJsonFile = os.path.join(settings['workdir'], 'profileOfBasicSectorAfterCompaction.json')
    hardIniUserSubroutine = os.path.join(settings['workdir'], 'hardini_partialSec.f')
    wireProfilesJsonFileForCompact = ''
    jsonFileForL1L2OfRedudcedModel = os.path.join(settings['workdir'],'setL1L2ForProfileOfBasicSectorAfterCompaction.json')
    #
    a_file = open(wireProfilesJsonFile, 'r')
    basicSectorDict = json.load(a_file)     # load profile of basic sector
    a_file.close()
    #
    a_file = open(jsonFileForL1L2OfRedudcedModel, 'r')
    L1L2DesignateDict = json.load(a_file)   # load L1/L2 labels of nodes
    a_file.close()



    from source.classes.StrandBasicSector import StrandBasicSector  # rely on abaqus modules
    basicSector = StrandBasicSector(nWiresPerLayer=np.array(settings['nWiresPerLayer'], dtype=int),
                                    wireLayRadii=np.array(settings['wireLayRadii']),
                                    rWiresPerLayer=np.array(settings['rWiresPerLayer']),
                                    wireLayLength=settings['wireLayLength'],
                                    phaseAngle=np.array(settings['phaseAngle'], dtype=float),
                                    angles=[settings['orientOfL1'], settings['orientOfL2']],
                                    loading=loading,
                                    thickness=settings['thickness'],  # create basic sector
                                    basicSectorDict=basicSectorDict,    # manually set cutState
                                    L1L2DesignateDict=L1L2DesignateDict,
                                    )

    # create SimulationSetup object
    launchJob = 0
    useBeams = 0
    elementCode = 'C3D8'
    jobName = loading.typeOfLoadingApplied
    curveName = jobName
    workDir = os.path.join(settings['workdir'], 'tension')   # must be absolute path
    postProcess = 0
    generateSimImages = 0
    #
    howSurfacesAreRepelled = 'FiniteSlidingContact'
    contactNormalBehaviour = 'Hard'
    normalContactConstraintEnforceMethod = 'Penalty'
    contactTangentialFrictionCoefficient = 0        # frictionless between wires
    numericalStabilization = 0
    interferenceStep = 0
    contactCtrl = 0
    requestRestart = 0
    restartFrequency = 1
    stiffnessScaleFactor = 1
    penaltyType = 'linear'
    constructGeometryMethod = 'reducedModelOfJiang'
    dynamic = 'static'
    meshCtrl = {'meshSize': settings['meshSize']}       # set mesh density


    from source.classes.SimulationSetup import SimulationSetup
    setup = SimulationSetup(
        launchJob=launchJob,
        loading=loading,
        materialList=materialPerLayer,
        design=settings['design'],
        useBeams=useBeams,
        elementCode=elementCode,
        jobName=jobName,
        curveName=curveName,
        dirSaveImages=workDir,
        workDir=workDir,
        postProcess=postProcess,
        skipJobIfODBPresent=0,
        generateInputFile=1,
        generateImages=generateSimImages,
        nCPU=2,
        toleranceForContactDetection=0.10 * np.min(settings['rWiresPerLayer']),
        removeContactPairsInvolvingWiresEnds=0,
        howSurfacesAreRepelled=howSurfacesAreRepelled,
        contactNormalBehaviour=contactNormalBehaviour,
        normalContactConstraintEnforceMethod=normalContactConstraintEnforceMethod,
        contactTangentialFrictionCoefficient=contactTangentialFrictionCoefficient,
        numericalStabilization=numericalStabilization,
        interferenceStep=interferenceStep,
        contactCtrl=contactCtrl,
        requestRestart=requestRestart,
        restartFrequency=restartFrequency,
        stiffnessScaleFactor=stiffnessScaleFactor,
        penaltyType=penaltyType,
        constructGeometryMethod=constructGeometryMethod,
        dynamic=dynamic,
        compactionDie=None,     # no compaction ring
        wireProfilesJsonFileForCompact=wireProfilesJsonFileForCompact,
        wireProfilesJsonFile=wireProfilesJsonFile,
        hardIniUserSubroutine=hardIniUserSubroutine,
        jsonFileForL1L2OfRedudcedModel=jsonFileForL1L2OfRedudcedModel,
        folderToStoreDebugDataFiles=os.path.join(settings['workdir'], 'tension', 'debugDataFiles'),   # folder to store files generated for debugging purposes
        constraintSchemeOfReducedModel='jiang',
        useBalancedContactBetweenWires=True,
        **meshCtrl
    )


    # map material to strand layers in abaqus model
    from source.classes.MaterialData import MaterialData
    materialData = MaterialData(
        strand=basicSector,
        materialPerLayer=materialPerLayer
    )

    # construct model and generate inp file
    from source.simulationLaunchers.LaunchSimulation import constructModel
    start = time.time()
    constructModel(setup, strand=basicSector)
    end = time.time()
    print('Timelapse of modeling compaction: ' + str(end - start) + 's.')

    return

# -------------------------------------------------------------------------
if __name__ == '__main__':

    try:
        import sys
        genInpForTensionSimu(settingJson=sys.argv[-1])
    except Exception:
        settingJson = os.path.join(os.getcwd(), 'configuration.json')
