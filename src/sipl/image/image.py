import numpy as np
import json
import base64
import copy
from cStringIO import StringIO
from pprint import pprint
from os.path import abspath

from sipl import Algorithm

# References
# http://docs.scipy.org/doc/numpy/user/basics.subclassing.html
# https://github.com/enthought/distributed-array-protocol
# http://distributed-array-protocol.readthedocs.org/en/rel-0.9.0/#
# http://docs.scipy.org/doc/numpy/reference/generated/numpy.asarray.html


class ImageJSONEncoder(json.JSONEncoder):

    """ The class used by json to encode the image object """

    def default(self, obj):
        if isinstance(obj, Image):
            return Image._dump(obj)
        if isinstance(obj, str):
            return obj
        if isinstance(obj, unicode):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def construct_image(dct):
    """ Used to reconstruct the image from a pickled object. Must be a function
    at the base level and not a static method of a class. """
    data = base64.b64decode(dct["data"])
    image = np.frombuffer(data, dct["dtype"]).reshape(dct["shape"])
    image = image.view(Image)
    image.metadata.update(json.loads(dct["metadata"]))
    image._dimData = dct["dimData"]
    return image


def image_json_hook(data):
    """ Used by json to deserialize into an Image object """

    # If we are actually a serialized image, reconstruct it
    if isinstance(data, dict) and "data" in data:
        return construct_image(data)

    # Otherwise, decode unicode strings and return
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        # Set the key/value pair
        rv[key] = value

    # Return
    return rv


def dim_data_dict(dist_type='b', size=1, proc_grid_size=1, proc_grid_rank=0,
                  start=0, stop=1, padding=(0, 0)):
    return {"dist_type": dist_type,
            "size": size,
            "proc_grid_size": proc_grid_size,
            "proc_grid_rank": proc_grid_rank,
            "start": start,
            "stop": stop,
            "padding": padding}


def default_dim_data(obj):
    """ Create a default structure for data used by __distarray__ """
    return [dim_data_dict(size=int(dim), stop=int(dim)) for dim in obj.shape]


class Image(np.ndarray):

    """ The base class for all the file readers. """

    def __new__(cls, inputArray=np.zeros((0, 0, 0), dtype=np.uint8)):

        # Use asarray to make the memory contiguous and have copy by default
        obj = np.asarray(inputArray).view(cls)
        obj.metadata = {}

        # If the input array has metadata, update the object. Don't use getattr
        # as it will just copy a reference to the original.
        if hasattr(inputArray, "metadata"):
            obj.metadata.update(inputArray.metadata)

        # Ditto with the dimData
        obj._dimData = default_dim_data(obj)
        if hasattr(inputArray, "_dimData"):
            obj._dimData = copy.deepcopy(inputArray._dimData)

        # Return the created object
        return obj

    @staticmethod
    def loads(s):
        """ Load an image from a json string. """

        return json.loads(s, object_hook=image_json_hook)

    def __array_finalize__(self, obj):

        # Standard __array_finalize__ syntax
        if obj is None:
            return

        # Create an empty metadata
        self.metadata = {}

        # If it exists, grab the metadata from the original object. Again,
        # don't use getattr as it will copy a reference.
        if hasattr(obj, "metadata"):
            self.metadata.update(obj.metadata)

        # Create a _dimData for the object
        self._dimData = default_dim_data(obj)

    def __distarray__(self):
        """ For use in the distributed array protocol. The defaults are a
        single block of of the entire data. Split functions will update
        these values. """

        return {"__version__": "0.9.0",
                "buffer": buffer(self),
                "dim_data": self._dimData}

    def _dump(self):
        """ Store the state of the array. Used in pickling and
        json serialization """

        # b64encoding is much faster and smaller than tostring()
        data64 = base64.b64encode(self.data)

        # Store the necessary information to recreate the object
        return {"data": data64,
                "dtype": str(self.dtype),
                "shape": self.shape,
                "metadata": json.dumps(self.metadata),
                "dimData": self._dimData}

    def __reduce__(self):
        """ Used during pickling. """

        # The second item must be a tuple, so I made a tuple with one item
        return (construct_image, (self._dump(),))

    def __str__(self):

        # Spark uses the string representation when serializing, so I have to
        # dump the whole thing into a string. Try to not call this on it's own.
        return str(json.dumps(self, cls=ImageJSONEncoder))

    def __repr__(self):

        # Create a string buffer to pretty print to
        reprString = StringIO()

        # Pretty print to the buffer
        pprint({"metadata": self.metadata,
                "_dimData": self._dimData,
                "data": np.copy(self),
                "id": "0x%x" % id(self)}, reprString)

        # Return the string representation
        return reprString.getvalue()

    def dumps(self):
        return str(self)

    def __getitem__(self, index):

        # The return value
        retVal = Image(np.ndarray.__getitem__(self, index))

        # Ensure we are passing an iterable object to the next code block
        if type(index) != tuple:
            index = [index]

        # Create an empty dim data dict for each dimension in index
        dimData = copy.deepcopy(retVal._dimData)

        # In case we insert an empty dimension and need to offset our reads
        addedDims = 0

        # Enumerate through the dimensions and fix the distData
        for i in range(len(index)):

            # If the current slice is None, keep the dimension empty. This can
            # occur if we just add an arbitrary dimension, such as
            # np.array([[[[[1]]]]])
            if index[i] == None:
                dimData.insert(i, dim_data_dict())
                addedDims += 1

            # Otherwise we are good, parse the dimdata from the parent array
            else:

                # Keep the code clean
                parentIndex = i - addedDims
                parentData = self._dimData[parentIndex]

                # If we still have dimension info from the parent, use it
                if parentIndex < len(self._dimData):
                    dimData[i] = copy.deepcopy(parentData)

                # Fix the slice indices for the current dimension
                if type(index[i]) == int:
                    # A single int index was passed. Start + 1 = Stop
                    start = parentData["start"] + index[i]
                    dimData[i]["start"] = start
                    dimData[i]["stop"] = start + 1
                    # Also add a dimension in the return array
                    newShape = list(retVal.shape)
                    newShape.insert(i, 1)
                    retVal = retVal.reshape(newShape)

                else:
                    # Otherwise it was a slice. Calculate the start and stop.
                    if index[i].start is None:
                        dimData[i]["start"] = parentData["start"]
                    else:
                        dimData[i]["start"] = parentData[
                            "start"] + index[i].start
                    if index[i].stop is None:
                        dimData[i]["stop"] = parentData["stop"]
                    else:
                        dimData[i]["stop"] = index[i].stop

        # Return
        retVal._dimData = dimData
        return retVal

    def __getslice__(self, start, stop):
        return self.__getitem__(slice(start, stop))


class ImageIn(Algorithm, Image):

    # The filter for a file open dialog box
    fileFilter = "All Files (*.*)"

    def __call__(self, filename, **kwargs):

        # Try to open file via the baseclass _open method
        try:
            obj = self._open(filename, **kwargs)
        except Exception, e:
            raise IOError("%s - unable to open %s: %s" %
                          (self.__class__.__name__, filename, str(e)))

        # Call the base class __new__ with the object, to populate metadata
        obj = Image.__new__(self.__class__, obj)

        # Set special metadata
        obj.metadata["filename"] = abspath(filename)

        # Return
        return obj

    def _open(self, filename, **kwargs):
        raise NotImplementedError("Must overwrite _open method")


class ImageOut(Algorithm):

    params = {"filename": None}

    def __call__(self, image, **kwargs):
        raise NotImplementedError("Must overwrite __call__ method")
