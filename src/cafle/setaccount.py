from types import FunctionType
#from collections import OrderedDict
from .account import (
    Account,
    Merge,
)

__all__ = ['SetAccount']

#### Set Account ####
class SetAccount:
    def __init__(self, title=None, byname=None, index=None):
        self.title = title
        if byname is None:
            self.byname = title
        else:
            self.byname = byname
        self.index = index
        self._dct = {} #OrderedDict()

    @property
    def keys(self):
        return self.__dict__.keys()

    def __getitem__(self, key):
        return self.__dict__[key]

    def set_account(self, title, highlevel=None, byname=None, tag=None, index=None):
        if byname is None:
            byname = title
        if index is None:
            index = self.index
        _acc = Account(title=title, byname=byname, index=index)

        setattr(self, title, _acc)
        self._dct[title] = _acc

        if isinstance(tag, str):
            self.tag_account(_acc, tag)
        elif isinstance(tag, list):
            for tagval in tag:
                self.tag_account(_acc, tagval)
                
        if highlevel is not None:
            if 'dct_high' not in vars(self):
                self.dct_high = {} #OrderedDict()
            if highlevel not in self.dct_high.keys():
                iptvalhigh = SetAccount(highlevel)
                self.dct_high[highlevel] = iptvalhigh
                setattr(self, highlevel, iptvalhigh)
            self.dct_high[highlevel].getacc(_acc)
        return _acc
    setacc = set_account

    def get_account(self, _acc, title=None):
        if title is None:
            title = _acc.title
        if 'tag' in _acc.__dict__:
            tag = _acc.tag
        else:
            tag = None
        setattr(self, title, _acc)
        self._dct[title] = _acc
        if isinstance(tag, str):
            self.tag_account(_acc, tag)
        elif isinstance(tag, list):
            for tagval in tag:
                self.tag_account(_acc, tagval)
        return _acc
    getacc = get_account
    
    def tag_account(self, acc, tag):
        if 'tag' not in vars(self):
            self.tag = {} #OrderedDict()
        if tag not in self.tag:
            self.tag[tag] = SetAccount(tag)
        self.tag[tag].getacc(acc)

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
        
    @property
    def mrg(self):
        return Merge(self._dct)
            
    @property
    def amt(self):
        rslt = 0
        for item in self._dct.values():
            try:
                rslt += item.amt
            except:
                pass
        return rslt