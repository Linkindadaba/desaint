# Python 3.14 compatibility patch for Django Context.__copy__
try:
    from django.template import context as _context_mod

    def _django_context_copy(self):
        duplicate = object.__new__(self.__class__)
        duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    _context_mod.Context.__copy__ = _django_context_copy
except Exception:
    pass
