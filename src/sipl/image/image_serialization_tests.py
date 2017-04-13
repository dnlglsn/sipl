import numpy as np
import json

from image import Image


class STRImageJSONEncoder(json.JSONEncoder):

    """ The class used by json to encode the image object """

    def default(self, obj):
        if isinstance(obj, STRImage):
            return STRImage._dump(obj)
        if isinstance(obj, str):
            return obj
        if isinstance(obj, unicode):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def construct_str_image(dct):
    """ Used to reconstruct the image from a pickled object. Must be a function
    at the base level and not a static method of a class. """
    data = dct["data"]
    image = np.fromstring(data, dct["dtype"]).reshape(dct["shape"])
    image = image.view(STRImage)
    image.metadata.update(json.loads(dct["metadata"]))
    image._dimData = dct["dimData"]
    return image


def str_image_json_hook(data):
    """ Used by json to deserialize into an Image object """

    # If we are actually a serialized image, reconstruct it
    if isinstance(data, dict) and "data" in data:
        return construct_str_image(data)

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


class STRImage(Image):

    @staticmethod
    def loads(s):
        """ Load an image from a json string. """

        return json.loads(s, object_hook=str_image_json_hook)

    def _dump(self):
        """ Store the state of the array. Used in pickling and
        json serialization """

        # Try with a string to see the speed
        data = self.tostring()

        # Store the necessary information to recreate the object
        return {"data": data,
                "dtype": str(self.dtype),
                "shape": self.shape,
                "metadata": json.dumps(self.metadata),
                "dimData": self._dimData}

    def __reduce__(self):
        """ Used during pickling. """

        # The second item must be a tuple, so I made a tuple with one item
        return (construct_str_image, (self._dump(),))

    def __str__(self):

        # Spark uses the string representation when serializing, so I have to
        # dump the whole thing into a string. Try to not call this on it's own.
        return str(json.dumps(self, cls=STRImageJSONEncoder))

    def dumps(self):
        return str(self)


if __name__ == "__main__":

    arraySize = (1024, 1024)
    arraySize = (4, 5)
    data = np.random.random_sample(arraySize).astype(np.complex64)
    data.imag = np.random.random_sample(data.shape)

    # Make the regular image which uses the b64encode/b64decode functions
    Image.loads(Image(data).dumps())

    # Make the image which doesn't use base64 encoding
    STRImage.loads(STRImage(data).dumps())

    # Time it
    # timeit.timeit("Image.loads(Image(data).dumps())")
    # a = b64Image.dumps()
    # b = Image.loads(a)
