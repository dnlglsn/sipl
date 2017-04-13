import numpy as np
from PIL import Image as _PILImage

from sipl import Algorithm
from sipl.image import ImageIn, ImageOut

# References
# http://docs.scipy.org/doc/numpy/user/basics.subclassing.html
# http://pillow.readthedocs.org/en/2.3.0/handbook/image-file-formats.html


class ImageToPIL(Algorithm):

    _params = {"decimationFactor": 0}

    def __call__(self, image):
        """ Convert an image to a PIL representation """

        # I only care about showing images which can map to pixel values
        if image.dtype != np.uint8:
            raise TypeError("Can only show images with an unsigned byte dtype")

        # Figure out the mode based on the number of channels
        mode = {1: "L", 3: "RGB", 4: "RGBA"}[image.shape[2]]

        # Return a PIL image object
        if (mode == "L"):
            # Using squeeze would get rid of a single row or column, so
            # do this method instead.
            rows, cols = image.shape[:2]
            pilImage = _PILImage.fromarray(image.reshape((rows, cols)), mode)
        pilImage = _PILImage.fromarray(image, mode)

        # Decimate if requested
        if self.decimationFactor > 0:
            newSize = [dim / (self.decimationFactor + 1)
                       for dim in pilImage.size]
            pilImage = pilImage.resize(newSize)

        return pilImage


class PILImageIn(ImageIn):

    """ An image reader for the standard image types used by PIL. """

    # The filter for a file open dialog box
    fileFilter = "PIL Images (*.png *.bmp *.jpg *.jpeg *.gif *.pcx "
    fileFilter += "*.ppm *.eps *.tiff *.psd *.tga *.xpm)"

    def _open(self, filename):

        # Open the image
        pilImage = _PILImage.open(filename)

        # Open the file using PIL and convert to a numpy array
        numCols, numRows = pilImage.size
        numChannels = {"L": 1, "RGB": 3, "RGBA": 4}[pilImage.mode]
        obj = np.fromstring(pilImage.tobytes(), dtype=np.uint8)
        obj = obj.reshape((numRows, numCols, numChannels))
        return obj


class PILImageOut(ImageOut):

    """ An image writer for the standard image types used by PIL. """

    def __call__(self, image, **kwargs):
        """ Write an image to disk via PIL """

        if not self.filename:
            raise IOError("PILImageOut.filename must be set")

        # Use the ToPIL algorithm to convert to PIL and then write to disk
        ImageToPIL(**kwargs)(image).save(self.filename)
