import os
import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def genProfileAndL1L2AfterCompaction(ElemNodalInfoCsvFile, L1L2SetNamesAndCoordinatesJsonFile,
                                     profileOfBasicSectorAfterCompactionJson,
                                     setL1L2ForProfileOfBasicSectorAfterCompactionJson,
                                     pngOfNodalClassification=''):
    """
    this function reads in the nodal coordinates as well as the sets of L1 L2 nodes, then extract the profiles of wires,
    and label the profile nodes as L1 or L2
    @param ElemNodalInfoCsvFile: str, path of file
    @param L1L2SetNamesAndCoordinatesJsonFile: str, path of file
    @param profileOfBasicSectorAfterCompactionJson: str, path of file
    @param setL1L2ForProfileOfBasicSectorAfterCompactionJson: str, path of file
    @param pngOfNodalClassification: str, path to save the png file for nodal classification into L1 and L2
    @return:
    """
    from source.postProcessing.compactionPostprocess import extractx0y0z0xyzFromELEM_NODALRpt, \
        extractQuadMeshAndProfileOnBotOfBasicSectors

    x0y0z0xyzDict, connectivityDict, labelNodeDict = extractx0y0z0xyzFromELEM_NODALRpt(
        ElemNodalInfoCsvFile=ElemNodalInfoCsvFile,
        L1L2SetNamesAndCoordinatesJson=L1L2SetNamesAndCoordinatesJsonFile
    )

    botConnectivityDict, boundSeqDict = extractQuadMeshAndProfileOnBotOfBasicSectors(x0y0z0xyzDict, connectivityDict)

    # extract profile of basic sector after compaction
    profiles = {}
    for wireName in boundSeqDict.keys():
        profile = []
        seq = boundSeqDict[wireName]  # list
        nodes = np.array(x0y0z0xyzDict[wireName])  # 2d array, [x0, y0, z0, x, y, z]
        nodes = nodes[:, [-3, -2]]
        for inode in seq:
            profile.append(nodes[inode].tolist())
        profiles[wireName] = profile

    # from source.postProcessing.compactionPostprocess import plotProfiles
    # ax = plotProfiles(wireProfiles=profiles)  # plot profiles of wires

    a_file = open(profileOfBasicSectorAfterCompactionJson, "w")    # write wire profiles to json file
    json.dump(profiles, a_file)
    a_file.close()

    # set L1L2 for nodes of profiles of wires in profileOfBasicSectorAfterCompaction.json
    L1L2Lables = {}
    for wireName in boundSeqDict.keys():
        L1L2Label = []
        seq = boundSeqDict[wireName]
        labels = labelNodeDict[wireName]
        for inode in seq:
            L1L2Label.append(labels[inode])
        L1L2Lables[wireName] = L1L2Label

    a_file = open(setL1L2ForProfileOfBasicSectorAfterCompactionJson, "w")  # save L1 and L2 labels to file
    json.dump(L1L2Lables, a_file)
    a_file.close()

    # plot for verification if required
    if pngOfNodalClassification != '':
        from source.utilities.utilitiesOfReducedModel import plotProfileAndL1L2Classification
        fig = plotProfileAndL1L2Classification(profiles=profiles, classification=L1L2Lables)
        fig.savefig(pngOfNodalClassification, dpi=300, transparent=True)
        print('Nodal classification saved to: ' + str(pngOfNodalClassification))
        plt.close(fig)

    return

# # plot profile
# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)
# for (wireName, color) in zip(botConnectivityDict.keys(), ['--ro', '--gs', '--^b']):
#     nodes = x0y0z0xyzDict[wireName]
#     seq = boundSeqDict[wireName]
#     profileNodes = [[nodes[inode][-3], nodes[inode][-2]] for inode in seq]
#     profileNodes.append(profileNodes[0])    # repeat starting node
#     ax.plot([xy[0] for xy in profileNodes], [xy[1] for xy in profileNodes], color, label=wireName)
# plt.legend()


# # find nodes on the bottom using unsupervised learning
# maskOfNodesOnBottom = {key: [] for key in x0y0z0xyzDict.keys()}
# for (key, val) in x0y0z0xyzDict.items():
#     arr = np.array(val)
#     z0 = arr[:, 2]      # 1d array
#     eps = (np.max(z0)-np.min(z0))/10.0
#     core_samples, cluster_ids = dbscan([[item] for item in z0], eps=eps, min_samples=2)     # classification
#     assert len(np.unique(cluster_ids)) == 2
#     if np.mean(z0[cluster_ids==0]) < np.mean(z0[cluster_ids==1]):
#         selectCat = 0
#     else:
#         selectCat = 1
#     #
#     mask = cluster_ids == selectCat
#     maskOfNodesOnBottom[key] = mask

def redundant():
    from sklearn.cluster import dbscan
    # ------------------- below derive wire profiles after compaction ----------------
    elemNodalAbqRptFile = os.path.join(folder, 'ELEM_NODAL.csv')
    jsonFile = os.path.join(folder, 'partialStrandProfilesAfterCompaction.json')    # write to target file
    wireProfiles = deriveCompactedStrandProfileForJiangReducedModel(elemNodalAbqRptFile, jsonFile)
    plotProfiles(wireProfiles, marker='o')      # visualize compacted shape of the basic sector

    # check accuracy
    from scipy.spatial.distance import pdist
    for (key, val) in wireProfiles.items():
        pts = wireProfiles[key]
        D = pdist(pts)
        print('shortest edge length in ' + str(key) + ': ' + str(min(D)))
        if any(D < 1e-4):
            raise ValueError('min = ' + str(min(D)))

    # below extend the compacted profile of the basic sector to full strand section
    replicates = mapProfileInFan2Full(azimuthalAngleOfL1=0, azimuthalAngleOfL2=np.pi/6, wireProfiles=wireProfiles)
    plotProfiles(replicates)      # visualize
    #
    allWireProfiles = {}
    # for central wire
    relevantParts = [key for key in replicates.keys() if 'wire0-0-0-0' in key.lower()]
    lookupTab = {int(item.split('-')[-1]): item for item in relevantParts}
    fullProfile = replicates[lookupTab[0]]
    for i in range(1, len(relevantParts)):
        uniqPts, segPolyCmb, fullProfile = mergePolygons(polygon0=fullProfile,
                                                         polygon1=replicates[lookupTab[i]],
                                                         tol=1e-2)
    allWireProfiles['WIRE0-0-0-0'] = fullProfile
    plotProfiles(allWireProfiles, marker='o')           # visualize for debugging
    #
    # for wire in 1st layer
    pairs = [[0, 11], [1, 2], [3, 4], [5,6], [7, 8], [9, 10]]
    for (i, pair) in enumerate(pairs):
        key0 = 'WIRE0-0-1-0' + '-' + str(pair[0])
        key1 = 'WIRE0-0-1-0' + '-' + str(pair[-1])
        #
        __, __, fullProfile = mergePolygons(polygon0=replicates[key0],
                                            polygon1=replicates[key1],
                                            tol=1e-3)
        allWireProfiles['WIRE0-0-1-'+str(i)] = fullProfile
    ax = plotProfiles(allWireProfiles)  # visualize for debugging
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_xlabel('X')
    ax.set_xlabel('Y')
    ax.set_title('Strand profile after compaction')

    # write to file
    jsonFile = os.path.join(folder, 'fullStrandProfilesAfterCompaction.json')
    a_file = open(jsonFile, "w")
    json.dump(allWireProfiles, a_file)
    a_file.close()
    # ------------------- above derive wire profiles after compaction ----------------

    # superimpose the wire profile of strand onto the point cloud of PEEQ
    ax = plotProfiles(allWireProfiles)           # visualize for debugging
    ax1 = plotPeeqPtCloudData(data=np.array(xyPeeqFullSec, dtype=float), ax=ax)       # visualize contour
    return

if __name__ == '__main__':
    import sys
    genProfileAndL1L2AfterCompaction(ElemNodalInfoCsvFile=sys.argv[-5],
                                     L1L2SetNamesAndCoordinatesJsonFile=sys.argv[-4],
                                     profileOfBasicSectorAfterCompactionJson=sys.argv[-3],
                                     setL1L2ForProfileOfBasicSectorAfterCompactionJson=sys.argv[-2],
                                     pngOfNodalClassification=sys.argv[-1]
                                     )


