from sipl import DEFAULT_NUM_SPLITS, Algorithm
from sipl.image import Image, vsplit, vstack


class ImageToRDD(Algorithm):

    _params = {"numSplits": DEFAULT_NUM_SPLITS,
               "context": None}

    def __call__(self, image):

        # Create an rdd of the split offsets and sizes
        splits = vsplit(image, self.numSplits)

        # Split the images. Make sure to make a copy using the Image
        # constructor, otherwise the metadata is shared by each array.
        images = [Image(image[s[0]:s[0] + s[1]]) for s in splits]

        # Update their chunkIndex metadata
        for i in range(len(images)):
            images[i]._dimData[0]["proc_grid_rank"] = i
            images[i]._dimData[0]["proc_grid_size"] = self.numSplits

        # Create an rdd to save
        if not self.context:
            raise RuntimeError("Must set ImageToRDD.context")
        rdd = self.context.parallelize(images, self.numSplits)

        # Return the rdd
        return rdd


class RDDToImage(Algorithm):

    def __call__(self, rdd):

        # Regenerate the keys from the chunk's metadata
        # TODO: Make 2d indices instead of 1d. I'm not sure how i'll split
        # the data in the future. It might be in chunks instead of rows.
        def gen_keys(x):
            return [x._dimData[0]["proc_grid_rank"], x]

        # Sort by the keys (chunk index) and collect
        arrays = rdd.map(gen_keys).sortByKey().collect()

        # Return the stacked data from the rdd
        return vstack([data for _, data in arrays])
