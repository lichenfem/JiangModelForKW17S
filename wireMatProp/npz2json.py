import os
import sys
import numpy as np
import json

npzFiles = [os.path.join('/home/lichen/Dropbox/ropemodels/scripts/JiangModelForKW17S_393', fname) for fname in
            ['lay0CalibatedMaterial.npz', 'lay1CalibatedMaterial.npz', 'lay2CalibatedMaterial.npz']]

for file in npzFiles:
    data = np.load(file)
    # print(data.files)
    E = data['E'].tolist()
    yield_stress = data['yield_stress'].tolist()
    plastic_strain = data['plastic_strain'].tolist()
    #
    dict = {"E": E, "yield_stress": yield_stress, "plastic_strain":plastic_strain}
    jsonFile = os.path.join(os.path.dirname(file), os.path.basename(file).replace('.npz', '.json'))
    a_file = open(jsonFile, "w")
    json.dump(dict, a_file)
    a_file.close()
    print('Generating ' + jsonFile)

