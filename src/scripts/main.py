import pyspark
import numpy as np

from sipl.image import PILImageIn, ImageToPIL
from sipl.hdfs import hdfs_rm, hdfs_exists, RDDToHDFS, HDFSToRDD
from sipl.spark import ImageToRDD, RDDToImage


def change(x):
    size = x._dimData[0]["proc_grid_rank"] + 1
    rank = x._dimData[0]["proc_grid_size"]
    factor = float(size) / rank
    return (x * factor).astype(np.uint8)


def random_color_channel(x):
    r = x[:, :, 0] - np.random.randint(0, 255)
    g = x[:, :, 1] - np.random.randint(0, 255)
    b = x[:, :, 2] - np.random.randint(0, 255)
    r = np.dstack((r, g, b)).view(type(x))
    r.metadata.update(x.metadata)
    return r

if __name__ == "__main__":

    filename = "../../data/cheetah.jpg"
    hdfsFilename = "hdfs://localhost:9000/cheetah.rdd"

    if hdfs_exists(hdfsFilename):
        hdfs_rm(hdfsFilename)

    sc = pyspark.SparkContext()

    imageIn = PILImageIn()(filename)
    rdd = ImageToRDD(context=sc)(imageIn)
    RDDToHDFS(filename=hdfsFilename)(rdd)

    rdd2 = HDFSToRDD(context=sc)(hdfsFilename)

    rdd2 = rdd2.map(random_color_channel)

    imageOut = RDDToImage()(rdd2)

    ImageToPIL(decimationFactor=3)(imageOut).show()
