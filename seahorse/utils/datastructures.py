
from collections.abc import Mapping

class ImmutableList(tuple):
    def __new__(cls, *args, warning="Is immutable",**kwargs):
        self = tuple.__new__(cls, *args, **kwargs)
        self.warning = warning

    def complain(self, *args,**kwargs):
        raise AttributeError(self.warning)
    
    # all mutable functions get complained
    __delitem__ = complain
    __delslice__ = complain

class DictWrapper(dict):
    def __init__(self, data,func, prefix):
        super().__init__(data)
        self.func = func
        self.prefix = prefix
    
    def __getitem__(self, key):
        """
        Retrieve the real value after stripping the prefix string
        """
        use_func = key.startswith(self.prefix)
        key = key.removeprefix(self.prefix)
        value = super().__getitem__(key)
        if use_func:
            return self.func(value)
        return value

class CaseInsensitiveMapping(Mapping):
    """
    Mapping allows case-insenstive key lookups.
    Original case of keys is preserved for iterations and string
    representation
    """
    def __init__(self, data):
        self._store = {k.lower(): (k, v) for k, v in self._unpack_items(data)}
    
    def __getitem__(self, key):
        return self._store[key.lower()][1]
    
    def __len__(self):
        return len(self._store)
    
    def __eq__(self, other):
        if isinstance(other, Mapping):
            return (
                {k.lower(): v for k, v in self.items()}
                ==
                {k.lower(): v for k, v in other.items()}
            )

    def __iter__(self):
        return (org_key for org_key, value in self._store.values())
    
    def __repr__(self):
        return repr({key:value for key, value in self._store.values()})
    
    @staticmethod
    def _unpack_items(data):
        # if data wrong type,raise TypeError
        if isinstance(data, (dict,Mapping)):
            yield from data.items()
            return
        for i, elem in enumerate(data):
            if len(elem) != 2:
                raise ValueError("#{} {}".format(i,len(elem)))
            if not isinstance(elem[0], str):
                raise ValueError(" %r"%elem[0])
            yield elem