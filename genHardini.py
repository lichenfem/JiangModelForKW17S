import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import json
import pandas as pd

# csvFileNamePEEQ = os.path.join(os.path.join(os.environ['ropemodels'], 'scripts', 'JiangModelForKW17S_393', 'compaction'), 'PEEQAtIntPtForCmpSimu.csv')

def genPEEQField(csvFileNamePEEQ, settingJson, hardiniPath='hardini_partialSec.f'):
    from source.postProcessing.compactionPostprocess import extractPeeqAtIntPtAsPtCloud
    x0y0z0xyzPeeqOnBasicSec, __ = extractPeeqAtIntPtAsPtCloud(csvFileNamePEEQ, includeXYZ=True)
    xyzPeeqOnBasicSec = [line[3:] for line in x0y0z0xyzPeeqOnBasicSec]
    x0y0z0PeeqOnBasicSec = [[line[0], line[1], line[2], line[-1]] for line in x0y0z0xyzPeeqOnBasicSec]

    from source.postProcessing.compactionPostprocess import plotPeeqPtCloudData
    ax0 = plotPeeqPtCloudData(data=np.array(xyzPeeqOnBasicSec, dtype=float))       # visualize contour
    ax0.set_title(r'Field of PEEQ in deformed shape')
    plt.close('all')
    ax1 = plotPeeqPtCloudData(data=np.array(x0y0z0PeeqOnBasicSec, dtype=float))       # visualize contour
    ax1.set_title(r'Field of PEEQ in undeformed shape')
    plt.close('all')

    # group integration points based on z coordinates
    from sklearn.cluster import dbscan
    z = np.array([[row[2]] for row in x0y0z0xyzPeeqOnBasicSec])
    eps = (np.max(z) - np.min(z))/10.0
    core_samples, cluster_ids = dbscan(z, eps=eps, min_samples=2)
    assert len(np.unique(cluster_ids)) == 2
    chosenClusterID = 0
    averageZ0 = np.sum(z[cluster_ids==0])/len(z[cluster_ids==0])
    averageZ1 = np.sum(z[cluster_ids==1])/len(z[cluster_ids==1])
    if averageZ1 < averageZ0:
        chosenClusterID = 0
    # filter a single layer of element
    xyPeeqOnBasicSec = [[line[0], line[1], line[-1]] for (line, id) in zip(xyzPeeqOnBasicSec, cluster_ids) if id == chosenClusterID]
    ax2 = plotPeeqPtCloudData(data=np.array(xyPeeqOnBasicSec, dtype=float))  # for tension simulation using Jiang's reduced model
    plt.close('all')

    # #----------------------following part of script replicate the PEEQ field for whole strand section-----------------------
    # # get the layer of integration point closer to z = 0
    # xyPeeqOnBasicSec = [[line[0], line[1], line[-1]] for line in xyzPeeqOnBasicSec if line[2] < 0.1/2]    # extract one layer
    # ax0 = plotPeeqPtCloudData(data=np.array(xyPeeqOnBasicSec, dtype=float))       # for tension simulation using Jiang's reduced model
    # # adjust to make L1 horizontal
    # i = np.argmin([line[0] for line in xyPeeqOnBasicSec])
    # j = np.argmax([line[0] for line in xyPeeqOnBasicSec])
    # dx = xyPeeqOnBasicSec[j][0] - xyPeeqOnBasicSec[i][0]
    # dy = xyPeeqOnBasicSec[j][1] - xyPeeqOnBasicSec[i][1]
    # phi = np.pi - np.arctan2(dy, -dx)
    # rotMat = np.array([[np.cos(-phi), -np.sin(-phi)],
    #                    [np.sin(-phi), np.cos(-phi)]])
    # xyPeeqOnBasicSecTRot = []
    # for line in xyPeeqOnBasicSec:
    #     x, y, peeq = line
    #     xr, yr = rotMat.dot([x, y])
    #     xyPeeqOnBasicSecTRot.append([xr, yr, peeq])
    # ax0 = plotPeeqPtCloudData(data=np.array(xyPeeqOnBasicSec, dtype=float))       # for tension simulation using Jiang's reduced model
    # # for tension simulation using 3d model, extend to represent full strand section
    # xyPeeqFullSec = mapPeeqInFan2Full(azimuthalAngleOfL1=0, azimuthalAngleOfL2=np.pi/6, PeeqPtCloudInFan=xyPeeqOnBasicSecTRot)
    # ax1 = plotPeeqPtCloudData(data=np.array(xyPeeqFullSec, dtype=float),
    #                           title='Distribution of equivalent plastic strain')       # visualize contour
    # ax1.set_xticklabels([])
    # ax1.set_yticklabels([])
    # #----------------------above part of script replicate the PEEQ field for whole strand section-----------------------

    # below generates hardini.f file
    a_file = open(settingJson, 'r')
    settings = json.load(a_file)  # loading settings, settings is a dict
    a_file.close()

    from source.utilities.peeqXY2Fortran77Code import genHardini
    wireLayLength = settings['wireLayLength']
    wireLayDirection = settings['wireLayDirection']
    lengthOfReducedModel = settings['thickness']
    genHardini(length=lengthOfReducedModel,
               wireLayLength=wireLayLength,
               wireLayDirection=wireLayDirection[0],    # int, 1 or -1
               xypeeq=xyPeeqOnBasicSec,
               filePath=hardiniPath)    # for Jiang's reduced model
    print('Abaqus user subroutine is saved to: ' + str(hardiniPath))
    # lengthOf3DModel = wireLayLength * 0.25  # setting this value arbitrarily incurs no difference
    # genHardini(length=lengthOf3DModel,
    #            wireLayLength=27.2,
    #            wireLayDirection=1,
    #            xypeeq=xyPeeqFullSec,
    #            filePath=os.path.join(folder, 'hardini_fullSec.f'))   # for 3D reduced model

    return

# ---------------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    genPEEQField(csvFileNamePEEQ=sys.argv[-3],
                 settingJson=sys.argv[-2],
                 hardiniPath=sys.argv[-1])
