import os
import sys
from source.postProcessing.compactionPostprocessInAqa import extractPEEQAtIntPtFromOdb, \
    extractElemNodalInfoFromOdb, extractL1L2NodalInfoFromCAE

# -------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    # odbFileOfCompactionSimu = os.path.join(os.getcwd(), 'compaction.odb')
    # csvFileNamePEEQ = os.path.join(os.getcwd(), 'PEEQAtIntPtForCmpSimu.csv')
    # csvFileNameElemNodal = os.path.join(os.getcwd(), 'ElemNodalInfoForCmpSimu.csv')
    odbFileOfCompactionSimu = sys.argv[-5]
    csvFileNameElemNodal = sys.argv[-4]
    csvFileNamePEEQ = sys.argv[-3]
    caeFile = sys.argv[-2]
    jsonFile = sys.argv[-1]

    extractPEEQAtIntPtFromOdb(odbFileOfCompactionSimu=odbFileOfCompactionSimu,
                              csvFileName=csvFileNamePEEQ)
    extractElemNodalInfoFromOdb(odbFileOfCompactionSimu=odbFileOfCompactionSimu,
                                csvFileName=csvFileNameElemNodal)
    extractL1L2NodalInfoFromCAE(caeFile=caeFile, jsonFile=jsonFile)
