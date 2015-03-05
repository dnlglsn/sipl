import numpy as np


def vsplit(array, numSplits):
    """ Split an array into numSplits number of row chunks """

    numRowsPerRead = array.shape[0] / numSplits
    remainder = array.shape[0] % numSplits
    numRows = [numRowsPerRead] * numSplits
    numRows[:remainder] = [numRowsPerRead + 1] * remainder
    startingRows = np.cumsum([0] + numRows[:-1])
    return zip(startingRows, numRows)


def vstack(arrays):
    return stack(arrays, np.vstack)


def hstack(arrays):
    return stack(arrays, np.hstack)


def dstack(arrays):
    return stack(arrays, np.dstack)


def stack(arrays, npFunc):

    retVal = None

    # If we have metadata, we need to keep it
    if hasattr(arrays[0], "metadata"):
        retVal = npFunc(arrays).view(type(arrays[0]))
        retVal.metadata.update(arrays[0].metadata)

    # Otherwise, just call the regular numpy functions
    else:
        retVal = npFunc(arrays)

    return retVal
