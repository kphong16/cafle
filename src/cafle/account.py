"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong
"""

import pandas as pd
from pandas import Series, DataFrame
pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
import numpy as np

from datetime import datetime
from datetime import date
from functools import wraps

from .genfunc import (
    limited,
    rounding,
    listwrapper,
)
from .index import (
    RangeIndex,
    DateIndex,
    date_range,
    str_to_date,
)

__all__ = ['Account']

DFCOL      = ['scd_in', 'scd_in_cum', 'scd_out', 'scd_out_cum',
                           'bal_strt', 'amt_in', 'amt_in_cum',
                           'amt_out', 'amt_out_cum', 'bal_end',
                           'rsdl_in_cum', 'rsdl_out_cum']
DFCOL_smry = ['bal_strt', 'amt_in', 'amt_out', 'bal_end']
DFCOL_inpt = ['scd_in', 'scd_out', 'amt_in', 'amt_out']
JNLCOL     = ['amt_in', 'amt_out', 'rcvfrm', 'payto', 'note']

class Account:
    _index = RangeIndex(0)

    def __new__(cls, *args, **kwargs):
        if len(args) == 0 and len(kwargs) == 0:
            return cls._index_new(cls._index)

        if len(args) == 1 and len(kwargs) == 0:
            if isinstance(args[0], (DateIndex, RangeIndex)):
                return cls._index_new(args[0])
            if isinstance(args[0], DataFrame):
                return cls._df_new(args[0])


        if len(args) == 0 and len(kwargs) == 1:
            if 'index' in kwargs:
                if isinstance(kwargs['index'], (DateIndex, RangeIndex)):
                    return cls._index_new(kwargs['index'])
                else:
                    raise TypeError("Type of index should be an instance of DataIndex or RangeIndex.")
            if 'dataframe' in kwargs:
                if isinstance(kwargs['dataframe'], DataFrame):
                    return cls._df_new(kwargs['dataframe'])
                else:
                    raise TypeError("Type of dataframe should be an instance of DataFrame.")

    @classmethod
    def _index_new(cls, index):
        result = object.__new__(cls)
        result.index = index
        result.name = 'main'
        result._df = cls._make_dataframe(index)
        result._initialize()
        return result

    @classmethod
    def _df_new(cls, df):
        result = object.__new__(cls)
        result.index = df.index
        result.name = 'main'
        result._df = cls._make_dataframe(df.index)
        for key in df.columns:
            if key in DFCOL_inpt:
                result._df.loc[df.index, key] = df[key]
        result._initialize()
        return result

    @staticmethod
    def _make_dataframe(index, data=None):
        if data is None:
            data = np.zeros([len(index), len(DFCOL)])
        return DataFrame(data, columns=DFCOL, index=index)

    @staticmethod
    def _make_jnldf():
        return DataFrame(columns=JNLCOL)

    @staticmethod
    def _make_jnlscd():
        return DataFrame(columns=JNLCOL)

    def _initialize(self):
        self._jnl = self.__class__._make_jnldf()
        self._jnlscd = self.__class__._make_jnlscd()
        self._set_outputfunc()
        self._cal_bal()

    def __repr__(self):
        """Return a string representation for this object."""
        if '_dct' in vars(self):
            repr = f"Account({self.name}, len {len(self.index)!r}, dct: {list(self.dct.keys())!r})"
        else:
            repr = f"Account({self.name}, len {len(self.index)!r})"

        """if len(self.df) > 5:
            repr = f"{self.df.head(2)}\n...\n{self.df.tail(2)}"
        else:
            repr = f"{self.df}"
        if 'name' in self.__dict__:
            repr = f"<{self.name}>\n" + repr"""
        return repr

    def __enter__(self):
        return self
    def __exit__(self, type, value, trackback):
        pass

    #Calculate Data Balance
    def _cal_bal(self):
        if len(self.index) == 0:
            return None

        self._df.scd_in_cum = self._df.scd_in.cumsum()
        self._df.scd_out_cum = self._df.scd_out.cumsum()
        self._df.amt_in_cum = self._df.amt_in.cumsum()
        self._df.amt_out_cum = self._df.amt_out.cumsum()

        #Calculate account balance
        for i, idx in enumerate(self.index):
            if i > 0:
                self._df.loc[idx, 'bal_strt'] = self._df.loc[idxpst, 'bal_end']
            self._df.loc[idx, 'bal_end'] = (self._df.loc[idx, 'bal_strt']
                                           + self._df.loc[idx, 'amt_in']
                                           - self._df.loc[idx, 'amt_out'])
            idxpst = idx

        # Calculate the residual of scheduled amounts
        self._df.loc[:, 'rsdl_in_cum'] = self._df.loc[:, 'scd_in_cum'] \
                                         - self._df.loc[:, 'amt_in_cum']
        self._df.loc[:, 'rsdl_out_cum'] = self._df.loc[:, 'scd_out_cum'] \
                                          - self._df.loc[:, 'amt_out_cum']

    #Input Data
    @listwrapper
    def addscd(self, idxval, amt, rcvfrm=None, note='add_scd'):
        """
        Add the amount on the 'scd_in' columns of dataframe.

        Parameters
        ----------
        idxval : index, list
        amt : int, float, list
        rcvfrm : str
        note : str

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        self.iptjnlscd(idxval, amt, 0, rcvfrm, None, note)
        self._df.loc[idxval, 'scd_in'] += amt
        self._cal_bal()

    @listwrapper
    def subscd(self, idxval, amt, payto=None, note='sub_scd'):
        """
        Add the amount on the 'scd_out' columns of dataframe.

        Parameters
        ----------
        idxval : index, list
        amt : int, float, list
        payto : str
        note : str

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        self.iptjnlscd(idxval, 0, amt, None, payto, note)
        self._df.loc[idxval, 'scd_out'] += amt
        self._cal_bal()

    @listwrapper
    def addamt(self, idxval, amt, rcvfrm=None, note='add_amt'):
        """
        Add the amount on the 'amt_in' columns of dataframe.

        Parameters
        ----------
        idxval : index, list
        amt : int, float, list
        rcvfrm : str
        note : str

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        if amt == 0:
            return
        self.iptjnl(idxval, amt, 0, rcvfrm, None, note)
        self._df.loc[idxval, 'amt_in'] += amt
        self._cal_bal()

    @listwrapper
    def subamt(self, idxval, amt, payto=None, note='sub_amt'):
        """
        Add the amount on the 'amt_out' columns of dataframe.

        Parameters
        ----------
        idxval : index, list
        amt : int, float, list
        payto : str
        note : str

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        if amt == 0:
            return
        self.iptjnl(idxval, 0, amt, None, payto, note)
        self._df.loc[idxval, 'amt_out'] += amt
        self._cal_bal()

    @listwrapper
    def iptamt(self, idxval, amt, rcvfrm=None, payto=None, note=None):
        """
        If the amount is positive, apply the addamt, else apply the subamt

        Parameters
        ----------
        idxval : index, list
        amt : int, float, list
        rcvfrm : str, default None
        payto : str, default None
        note : str, default "sub_amt"

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        if amt == 0:
            return
        if amt > 0:
            if rcvfrm is None:
                rcvfrm = "add_amt"
            self.addamt(idxval, amt, rcvfrm, note)
        else:
            if payto is None:
                payto = "sub_amt"
            self.subamt(idxval, -amt, payto, note)

    def iptjnlscd(self, idxval, amt_in, amt_out, rcvfrm=None, payto=None, note=None):
        """
        Add the amount on the journal schedule.

        Parameters
        ----------
        idxval
        amt_in
        amt_out
        rcvfrm
        payto
        note

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        tmpjnl = DataFrame([[amt_in, amt_out, rcvfrm, payto, note]],
                           columns=JNLCOL,
                           index=[idxval])
        self._jnlscd = pd.concat([self._jnlscd, tmpjnl])

    def iptjnl(self, idxval, amt_in, amt_out, rcvfrm=None, payto=None, note=None):
        """
        Add the amount on the journal.

        Parameters
        ----------
        idxval : index
        amt_in : int, float
        amt_out : int, float
        rcvfrm : str, default None
        payto : str, default None
        note : str, default None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        tmpjnl = DataFrame([[amt_in, amt_out, rcvfrm, payto, note]],
                           columns=JNLCOL, index=[idxval])
        self._jnl = pd.concat([self._jnl, tmpjnl])

    #Output Data
    @property
    def df(self):
        """
        Return the summarised dataframe

        Returns
        -------
        Return columns: DFCOL_smry
            ['bal_strt', 'amt_in', 'amt_out', 'bal_end']
        """
        return self._df.loc[:, DFCOL_smry]

    @property
    def dfall(self):
        """
        Return the all dataframe
        """
        return self._df

    @property
    def jnl(self):
        """
        Return the journal dataframe
        """
        return self._jnl

    @property
    def jnlscd(self):
        """
        Return the journal schedule dataframe
        """
        return self._jnlscd

    #Decorator
    class getattr_dfcol:
        """
        Decorator
        Get a class name and use the class name as the column of dataframe.
        """

        def __call__(self, cls):
            def init(self, spristnc):
                self.spristnc = spristnc
                self.colname = cls.__name__

            cls.__init__ = init

            def getitem(self, val):
                """
                If val is an integer, return the data which is in index[val].
                If val is a date, return the data which is on the date.
                If val is a string, get the date data and return the data
                    which is on the date.

                Parameters
                ----------
                val: int, slice, date, date like string,
                    ex) 0, 1:3, datetime.date(2021, 4, 30), "2021-04", "2021-04-30"

                Return
                ------
                data from dataframe
                Array of data from dataframe

                Examples
                --------
                >>> idx = DateIndex("2021.01", "2021.12")
                >>> acc = Account(idx, "loan")
                >>> acc.addscd(idx[0], 1000)
                >>> acc.subscd(idx[5], 800)
                >>> acc.addamt(idx[1], 500, "acc_oprtg", "amount acc oprtg")
                >>> acc.scd_in[idx[3]]
                    0.0
                >>> acc.scd_in[3]
                    0.0
                >>> acc.scd_in[0:3]
                    2021-01-31    1000.0
                    2021-02-28       0.0
                    2021-03-31       0.0
                    Name: scd_in, dtype: float64
                >>> acc.scd_in[datetime.date(2021, 3, 31)]
                    0.0
                >>> acc.scd_in["2021.04"]
                    2021-04-30    0.0
                    Name: scd_in, dtype: float64
                >>> acc.scd_in["2021"]
                    2021-01-31    1000.0
                    2021-02-28       0.0
                    2021-03-31       0.0
                    2021-04-30       0.0
                    2021-05-31       0.0
                    2021-06-30       0.0
                    2021-07-31       0.0
                    2021-08-31       0.0
                    2021-09-30       0.0
                    2021-10-31       0.0
                    2021-11-30       0.0
                    Name: scd_in, dtype: float64
                """
                if isinstance(val, date):
                    return self.spristnc._df.loc[val, self.colname]
                elif isinstance(val, int):
                    val = self.spristnc.index[val]
                    return self.spristnc._df.loc[val, self.colname]
                elif isinstance(val, str):
                    val = str_to_date(val)
                    return self.spristnc._df.loc[val, self.colname]
                elif isinstance(val, slice):
                    if isinstance(val.start, str):
                        new_start = str_to_date(val.start)
                    elif isinstance(val.start, int):
                        new_start = self.spristnc.index[val.start]
                    elif isinstance(val.start, date):
                        new_start = val.start

                    if isinstance(val.stop, str):
                        new_stop = str_to_date(val.stop)
                    elif isinstance(val.stop, int):
                        new_stop = self.spristnc.index[val.stop]
                    elif isinstance(val.stop, date):
                        new_stop = val.stop

                    new_slice = slice(new_start, new_stop)
                    return self.spristnc._df.loc[new_slice, self.colname]
            cls.__getitem__ = getitem

            return cls

    @getattr_dfcol()
    class scd_in:
        pass

    @getattr_dfcol()
    class scd_in_cum:
        pass

    @getattr_dfcol()
    class scd_out:
        pass

    @getattr_dfcol()
    class scd_out_cum:
        pass

    @getattr_dfcol()
    class bal_strt:
        pass

    @getattr_dfcol()
    class amt_in:
        pass

    @getattr_dfcol()
    class amt_in_cum:
        pass

    @getattr_dfcol()
    class amt_out:
        pass

    @getattr_dfcol()
    class amt_out_cum:
        pass

    @getattr_dfcol()
    class bal_end:
        pass

    @getattr_dfcol()
    class rsdl_in_cum:
        pass

    @getattr_dfcol()
    class rsdl_out_cum:
        pass

    def _set_outputfunc(self):
        self.scd_in = self.scd_in(self)
        self.scd_in_cum = self.scd_in_cum(self)
        self.scd_out = self.scd_out(self)
        self.scd_out_cum = self.scd_out_cum(self)
        self.bal_strt = self.bal_strt(self)
        self.amt_in = self.amt_in(self)
        self.amt_in_cum = self.amt_in_cum(self)
        self.amt_out = self.amt_out(self)
        self.amt_out_cum = self.amt_out_cum(self)
        self.bal_end = self.bal_end(self)
        self.rsdl_in_cum = self.rsdl_in_cum(self)
        self.rsdl_out_cum = self.rsdl_out_cum(self)

    def amt_rqrd_excs(self, idxval, rqrdamt, minunit=100):
        """
        Calculate the additional amount required in excess of the balance.

        Parameters
        ----------
        index : index number
        rqrdamt : int, float, total required amount
        minunit : int, default 100, minimum adjustment unit

        Returns
        -------
        amt_rqrd : float
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        amt_rqrd = max(rqrdamt - self.bal_end[idxval], 0)
        amt_rqrd = round_up(amt_rqrd, -log10(minunit))
        return amt_rqrd

    def send(self, idxval, amt, account, note=None):
        """
        Transfer the amount from this account to the opponent account.

        Parameters
        ----------
        index : index
        amt : int, float, amount to transfer
        account : account
        note : str, default None

        Returns
        -------
        None
        """
        if isinstance(idxval, int):
            idxval = self.index[idxval]
        elif isinstance(idxval, str):
            idxval = str_to_date(idxval)

        if 'title' in account.__dict__:
            account_title = account.title
        else:
            account_title = None
        self.subamt(idxval, amt, account_title, note)

        if 'title' in self.__dict__:
            self_title = self.title
        else:
            self_title = None
        account.addamt(idxval, amt, self_title, note)

    #Set and Manage Sub Account
    def subacc(self, name):
        _acc = Account(self.index)
        _acc.name = name

        if '_dct' not in vars(self):
            self._dct = {}

        self._dct[name] = _acc
        return _acc

    @property
    def dct(self):
        return vars(self).get('_dct', None)

    @property
    def mrg(self):
        dflst = [item._df for item in self._dct.values()]
        return Account(sum(dflst))
