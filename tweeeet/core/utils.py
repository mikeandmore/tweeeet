# decorators and utils functions

def singleton_new(cls):
    if not hasattr(cls, 'instance'):
        cls.instance = object.__new__(cls)
    else:
        cls.__init__ = object.__init__
    return cls.instance
