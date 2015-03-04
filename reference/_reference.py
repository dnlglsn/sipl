# Open these in browser windows
# http://localhost:8080/
# http://localhost:4040/stages/
# http://localhost:50075/dataNodeHome.jsp
# http://localhost:50070/dfshealth.html#tab-overview

# Start a webserver to view the output image
# python -m SimpleHTTPServer
# http://localhost:8000/

###########
# Imports #
###########

from pyspark import SparkContext

import numpy as np
from os import remove
from os.path import exists, join

####################
# Global Variables #
####################

# The file names
rddFilename = join("hdfs://localhost:9000/cheetah.rdd")  # load from HDFS
jpgFilename = join("output.jpg")

####################
# Useful functions #
####################


def vstack(arrays):
    return stack(arrays, np.vstack)


def hstack(arrays):
    return stack(arrays, np.hstack)


def stack(arrays, npFunc):

    # results = Image(np.vstack(collected))
    # results._dimData = collected[0]._dimData
    # pprint(results._dimData)
    # results = results.reshape([x["size"] for x in results._dimData])

    retVal = None
    # If we have metadata, we need to keep it
    if hasattr(arrays[0], "metadata"):
        retVal = npFunc(arrays).view(type(arrays[0]))
        retVal.metadata.update(arrays[0].metadata)
    # Otherwise, just call the regular numpy functions
    else:
        retVal = npFunc(arrays)
    return retVal


def random_color_channel(x):
    r = x[:, :, 0] - np.random.randint(0, 255)
    g = x[:, :, 1] - np.random.randint(0, 255)
    b = x[:, :, 2] - np.random.randint(0, 255)
    r = np.dstack((r, g, b)).view(type(x))
    r.metadata.update(x.metadata)
    return r

if __name__ == "__main__":

    ##################
    # Initialization #
    ##################

    # Create the spark context
    sc = SparkContext(appName="Spark Image Processing")
    # sc.addPyFile("danimage.zip")

    #################################################################
    # Load the RDD from disk or HDFS and translate back to an image #
    #################################################################

    # Load the rdd and attempt to get back the data
    rdd = sc.textFile(rddFilename)

    # Deserialize the rdd
    def load(x):
        # from danimage.stuff import Image
        from image import Image
        return Image.loads(x)
    rdd = rdd.map(load)

    #######################
    # Continue Processing #
    #######################

    # Do a little algorithm so we can see the chunks
    rdd = rdd.map(random_color_channel)

    # Regenerate the keys from the chunk's metadata
    def gen_keys(x):
        return [x.__distarray__()["dim_data"][0]["proc_grid_rank"], x]
    rdd = rdd.map(gen_keys)

    # Sort by the keys, which should be the chunk index
    rdd = rdd.sortByKey()

    # Delete the old file
    if exists(jpgFilename):
        remove(jpgFilename)

    # Collect the rdd and save to disk
    arrays = rdd.collect()
    finalArray = vstack([data for _, data in arrays])
    from pilImage import PILImageOut
    PILImageOut(filename=jpgFilename)(finalArray)
