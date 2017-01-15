class Algorithm(object):

    """ The base class for all algorithms """

    # The algorithm parameters, which are set during object initialization
    # and usually used during algorithm invocation. Each param is automatically
    # added to the object's __dict__ and accessed through the "." operator.
    _params = {}

    def __init__(self, **kwargs):
        """ Create an instance of an Algorithm, which can be reused. Once
        created, the object is invoked through the __call__ method, or "()".
        Run __call__ with an object of whatever needs to be transformed. """

        # Update the params with the keyword arguments
        self._params.update(kwargs)

        # Store the params as the class object's dictionary. Allows a user
        # to type in "obj.whatever" to set/retrieve values in the params
        # dictionary
        self.__dict__ = self._params

    def __call__(self, input, **kwargs):
        """ Execute the algorithm on the input """

        # This method needs to be overwritten in the derived class
        raise NotImplementedError("Must overwrite the __call__ method")
