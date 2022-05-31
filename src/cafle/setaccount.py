from types import FunctionType
from .account import (
    Account,
    Merge,
)

__all__ = ['SetAccount']

#### Set Account ####
class SetAccount:
    def __init__(self):
        self._dct = {}

    def set_account(self, title, byname=None, tag=None):
        _acc = Account(title=title, byname=byname)

        setattr(self, title, _acc)
        self._dct[title] = _acc

        if isinstance(tag, str):
            self.tag_account(_acc, tag)
        elif isinstance(tag, list):
            for tagval in tag:
                self.tag_account(_acc, tagval)
        return _acc

    def tag_account(self, acc, tag, addstr='t_'):
        tag = addstr + tag
        if tag in self.__dict__.keys():
            if isinstance(getattr(self, tag), dict):
                pass
            else:
                raise NameError("The tag name is already existing in account keys.")
        else:
            setattr(self, tag, {})
        getattr(self, tag)[acc.title] = acc

    def get_item(self, valdct=None, item='amt_ttl', func='sum'):
        if valdct is None:
            valdct = self._dct
        if isinstance(valdct, str):
            valdct = getattr(self, valdct)
        itemlst = []
        for tmpval in valdct.values():
            try:
                itemval = getattr(tmpval, item)
                itemlst.append(itemval)
            except:
                pass
        if isinstance(func, str):
            return eval(f"{func}({str(itemlst)})")
        elif isinstance(func, FunctionType):
            return func(itemlst)

    def mrg_account(self, valdct=None):
        if valdct is None:
            valdct = self._dct
        if isinstance(valdct, str):
            valdct = getattr(self, valdct)
        return Merge(valdct)

    @property
    def dct(self):
        if len(self._dct) == 0:
            return None
        return self._dct