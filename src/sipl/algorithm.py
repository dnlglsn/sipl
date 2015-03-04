class Algorithm(object):

    _params = {}

    def __init__(self, **kwargs):

        # Update the params with the keyword arguments
        self._params.update(kwargs)

        # Store the params as the class object's dictionary. Allows a user
        # to type in "obj.whatever" to set/retrieve values in the params
        # dictionary
        self.__dict__ = self._params

    def __call__(self, input, **kwargs):
        """ Execute the algorithm on the input """

        # This method needs to be overwritten in the derived class
        raise NotImplementedError("Must overwrite the execute method")
