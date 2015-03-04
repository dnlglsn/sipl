from rdd_algorithms import defaultNumSplits
from algorithm import Algorithm
from image import Image


class HDFSToRDD(Algorithm):

    """ An image reader for the Hadoop File System. Reads into an RDD."""

    _params = {"numSplits": defaultNumSplits,
               "context": None}

    def __call__(self, filename):

        # Load an rdd from hdfs. Will load as text.
        if not self.context:
            raise RuntimeError("Must set ImageToRDD.context")
        rdd = self.context.textFile(filename, self.numSplits)

        # Deserialize the text rdd into an rdd of images and return
        def load(x):
            return Image.loads(x)
        return rdd.map(load)


class RDDToHDFS(Algorithm):

    _params = {"filename": None}

    def __call__(self, rdd):

        # Save the rdd to hdfs
        rdd.saveAsTextFile(self.filename)
