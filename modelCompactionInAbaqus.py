import os
import sys
import json
import numpy as np
import time


def genInpForCompactionSimu(settingJson):
    """

    @param settingJson: str, path of setting file
    @param ellipticWireProfileJson: str, path of json file storing elliptical profiles for all wires in the strand
    @param partialEllipticWireProfileInBasicSectorJson: str, path of json file storing elliptical profiles only for wires
                                                        in the basic sector
    @return: none
    """
    # loading settings
    a_file = open(settingJson, 'r')
    settings = json.load(a_file)  # settings is a dict
    a_file.close()

    # create necessary folder if required
    try:
        os.mkdir(os.path.join(settings['workdir'], 'compaction'))
    except:
        pass
    try:
        os.mkdir(os.path.join(settings['workdir'], 'compaction', 'debugDataFiles'))
    except:
        pass

    # create list of materials
    from source.classes.Material import createMaterialListsForIsoPlas
    materialPerLayer = createMaterialListsForIsoPlas(pathsToCalibratedData=settings['pathsToCalibratedData'],
                                                     materialNames=settings['materialNames'],
                                                     poissonRatios=settings['poissonRatios'],
                                                     densities=settings['densities'])

    # set loading controls
    from source.classes.StaticLoading import StaticLoading
    loading = StaticLoading(typeOfLoadingApplied='compaction',
                            minInc=1e-8,
                            maxInc=0.05,
                            initialInc=1e-3,    # preset
                            targetRadialStrain=settings['targetRadialStrain'],
                            )

    # create strand object
    wireProfilesJsonFileForCompact = os.path.join(settings['workdir'], 'profileOfBasicSectorBeforeCompaction.json')
    jsonFileForL1L2OfRedudcedModel = os.path.join(settings['workdir'],'setL1L2ForProfileOfBasicSectorBeforeCompaction.json')
    a_file = open(wireProfilesJsonFileForCompact, 'r')
    basicSectorDict = json.load(a_file)  # output is a dict
    a_file.close()
    #
    a_file = open(jsonFileForL1L2OfRedudcedModel, 'r')
    L1L2DesignateDict = json.load(a_file)  # output is a dict
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

    # create compaction ring
    from source.classes.CompactionDie import CompactionDie
    compactionDie = CompactionDie(DieDiameter=basicSector.diameter * (1 - loading.targetRadialStrain),
                                  StraightStrand=basicSector,
                                  FrictCoeff=0.0,                                     # frictionless between ring and wire
                                  Overclosure=0.0 * min(settings['rWiresPerLayer']),  # user defined overlap
                                  inclRelaxStep=False,      # no relaxation
                                  )

    # create SimulationSetup object
    launchJob = 0
    useBeams = 0
    elementCode = 'C3D8'
    jobName = loading.typeOfLoadingApplied
    curveName = jobName
    workDir = os.path.join(settings['workdir'], 'compaction')   # must be absolute path
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
    #
    wireProfilesJsonFile = ''
    hardIniUserSubroutine = ''


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
        compactionDie=compactionDie,
        wireProfilesJsonFileForCompact=wireProfilesJsonFileForCompact,
        wireProfilesJsonFile=wireProfilesJsonFile,
        hardIniUserSubroutine=hardIniUserSubroutine,
        jsonFileForL1L2OfRedudcedModel=jsonFileForL1L2OfRedudcedModel,
        folderToStoreDebugDataFiles=os.path.join(settings['workdir'], 'compaction', 'debugDataFiles'),   # folder to store files generated for debugging purposes
        constraintSchemeOfReducedModel='jiang',
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

# ------------------------------------------------------------
if __name__ == '__main__':
    import sys
    genInpForCompactionSimu(settingJson=sys.argv[-1])

