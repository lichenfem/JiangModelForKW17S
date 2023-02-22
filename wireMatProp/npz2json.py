import os
import sys
import numpy as np
import json

def translate(npzFile):
    data = np.load(npzFile)
    # print(data.files)
    E = data['E'].tolist()
    yield_stress = data['yield_stress'].tolist()
    plastic_strain = data['plastic_strain'].tolist()
    #
    dict = {"E": E, "yield_stress": yield_stress, "plastic_strain": plastic_strain}
    jsonFile = os.path.join(os.path.dirname(npzFile), os.path.basename(npzFile).replace('.npz', '.json'))
    a_file = open(jsonFile, "w")
    json.dump(dict, a_file)
    a_file.close()
    print('Generating ' + jsonFile)
    return

if __name__ == '__main__':
    import sys
    translate(npzFile=sys.argv[-1])
