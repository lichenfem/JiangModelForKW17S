import os
import sys
from source.postProcessing.compactionPostprocessInAqa import extractNodalURFFromOdb

# -------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    odbPath = sys.argv[-2]
    folderOfCsvs = sys.argv[-1]
    extractNodalURFFromOdb(odbPath, folderOfCsvs, csvPrefix='NODE_U_RF_')
