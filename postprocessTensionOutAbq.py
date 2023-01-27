import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
import csv
from source.postProcessing.compactionPostprocess import extractTensileForceForReducedModel

def wrapper(settingJson, folder, prefix, FUJson):
    """

    @param settingJson: str, path of json file storing settings
    @param folder: str, path of folder where nodal U RF output are stored
    @param prefix: str, prefix of nodal U RF csv files
    @param FUJson: str, path of json where where F and strain is stored
    @return:
    """
    a_file = open(settingJson, 'r')
    settings = json.load(a_file)
    targetAxialStrain = settings['targetAxialStrain']
    a_file.close()

    csvFiles = {}
    for (root, subs, files) in os.walk(folder):
        for file in files:
            if file.startswith(prefix):
                count = int(file.split(prefix)[-1].split('.csv')[0])
                csvFiles[count] = os.path.join(root, file)
    keys = list(csvFiles.keys())
    keys.sort()
    #
    csvSeq = []
    for key in keys:
        csvSeq.append(csvFiles[key])

    Increments, Forces = extractTensileForceForReducedModel(csvSeq)
    Strains = [targetAxialStrain * val for val in Increments]

    # write to file
    data = {"Strains": Strains, "Forces": [F*(2*np.pi/(settings['orientOfL2']-settings['orientOfL1'])) for F in Forces]}
    a_file = open(FUJson, 'w')
    json.dump(data, a_file)
    a_file.close()
    print('FU response written to ' + str(FUJson))
    return
# ------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    try:
        import sys
        wrapper(settingJson=sys.argv[-3],
                folder=sys.argv[-2],
                prefix='NODE_U_RF_ApplyLoads_',
                FUJson=sys.argv[-1])
    except Exception:
        settingJson = '/home/lichen/Dropbox/ropemodels/scripts/JiangModelForKW17S_393/configuration.json'
        folder = '/home/lichen/Dropbox/ropemodels/scripts/JiangModelForKW17S_393/tension'
        prefix = 'NODE_U_RF_ApplyLoads_'
        FUJson = '/home/lichen/Dropbox/ropemodels/scripts/JiangModelForKW17S_393/tension/FU.json'
        wrapper(settingJson, folder, prefix, FUJson)