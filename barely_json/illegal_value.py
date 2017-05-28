# __author__ = 'tusharmakkar08'


class IllegalValue(object):
    '''
    A value that is illegal in JSON.

    ``parse`` wraps anything that isn't standard JSON into an
    ``IllegalValue`` instance. By default, these are then automatically
    resolved into standard Python types via ``resolve``. However, if you
    pass ``resolver=None`` to ``parse`` and your input contains illegal
    values then your output will contain instances of this class.

    The part of the source that is represented by this instance is
    stored in the ``source`` attribute. That may be the empty string in
    cases like ``[1, , 2]``.
    '''

    def __init__(self, source):
        '''
        Constructor.

        ``source`` is a string.
        '''
        self.source = source

    def __str__(self):
        return self.source

    def __repr__(self):
        return '<{} {!r}>'.format(self.__class__.__name__, self.source)

    def __eq__(self, other):
        return (isinstance(other, self.__class__) and
                other.source == self.source)

    def __hash__(self):
        return hash(self.source)
