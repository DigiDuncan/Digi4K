class EnumPlus(type):
    def __init__(cls, name, bases, dct):
        cls._vals = {v for k, v in dct.items() if not k.startswith("_")}

    def __contains__(cls, val):
        return val in cls._vals
