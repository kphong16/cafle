"""
Written by KP_Hong <kphong16@daum.net>
2021, KP_Hong

INDEX

Modules
-------
Index : Create and manage an array of dates
PrjtIndex : Create and manage index objects

Methods
-------
booleanloc : Return boolean array of data which is in array
"""

import pandas as pd
import numpy as np

#from pandas import (
#    date_range,
#    DatetimeIndex,
#    PeriodIndex,
    #RangeIndex,
#)

from datetime import (
    date,
    timedelta,
)
from dateutil.relativedelta import relativedelta

#from .genfunc import is_iterable
__all__ = ['RangeIndex', 'DateIndex', 'date_range', 'Index'] #, 'booleanloc', 'PrjtIndex']


def is_scalar(value):
    if isinstance(value, int):
        return True
    else:
        return False
        
def str_to_date(value):
    # date
    if isinstance(value, date):
        return value

    # date('-')
    value_lst = value.split('-')
    if len(value_lst) == 3:
        int_lst = [int(x) for x in value_lst]
        return date(*int_lst)
    elif len(value_lst) == 2:
        int_lst = [int(x) for x in value_lst]
        return date_monthend(*int_lst)
    
    # date('.')
    value_lst = value.split('.')
    if len(value_lst) == 3:
        int_lst = [int(x) for x in value_lst]
        return date(*int_lst)
    elif len(value_lst) == 2:
        int_lst = [int(x) for x in value_lst]
        return date_monthend(*int_lst)
        
    raise TypeError("Type of the data is not suitable.")
        
def date_monthend(year, month=None):
    if isinstance(year, date):
        dt = year
        return date_monthend(dt.year, dt.month)
        
    if isinstance(year, str):
        dt = year
        return date_monthend(str_to_date(dt))
    
    if month in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
        month_next = month + 1
        dt_next = date(year, month_next, 1)
        dt_monthend = dt_next - timedelta(days=1)
    elif month == 12:
        year_next = year + 1
        dt_next = date(year_next, 1, 1)
        dt_monthend = dt_next - timedelta(days=1)
    return dt_monthend

def date_next(dt, num=1, freq='M'):
    if isinstance(dt, str):
        dt = str_to_date(dt)
    assert isinstance(dt, date)
    if freq=='M':
        month_next = dt.month + num - 1
        year_next, month_next = divmod(month_next, 12)
        month_next += 1
        year_next = dt.year + year_next
        dt_next = date_monthend(year_next, month_next)
        return dt_next
    if freq=='Y':
        dt_next = dt + relativedelta(years=num)
        return dt_next
    if freq=='D':
        dt_next = dt + timedelta(days=num)
        return dt_next
    
def is_samemonth(*args):
    if len(args) < 2:
        raise ValueError("Number of values are not enough.")
    year_crit = args[0].year
    month_crit = args[0].month
    
    for val in args[1:len(args)]:
        if val.year != year_crit:
            return False
        if val.month != month_crit:
            return False
    return True

def all_none(*args):
    tmp_lst = [x==None for x in args]
    return all(tmp_lst)
    
def any_none(*args):
    tmp_lst = [x==None for x in args]
    return any(tmp_lst)

def allnot_none(*args):
    tmp_lst = [x!=None for x in args]
    return all(tmp_lst)
    
def anynot_none(*args):
    tmp_lst = [x!=None for x in args]
    return any(tmp_lst)


class RangeIndex():
    """
    Immutable sequence used for indexing a monotonic integer range.

    Parameters
    ----------
    start : int(default:0), range, RangeIndex instance
        If 'start' is an int and 'stop' is not given, interpreted as 'stop' instead.
    stop : int(default:0)
    step : int(default:1)
    name : str(default None)
        Name of the index.
    
    
    Attributes
    ----------
    name : The name of index
    len : The length of the index
    data : Raw data of index
    values : Raw data of index
    
    Methods
    -------
    copy : Deep copy of the index

    Examples
    --------
    Input one integer.
    >>> idxa = RangeIndex(10, name='IdxA')
    >>> idxa
        RangeIndex(range(0, 10))
    >>> idxa.name
        'IdxA'
    >>> len(idxa)
        10
    >>> idxa.len
        10
    >>> idxa.copy(name='NewIdxA')
        RangeIndex(range(0, 10))
    Input a RangeIndex.
    >>> RangeIndex(idxa)
        RangeIndex(range(0, 10))
    Input a range.
    >>> RangeIndex(range(0, 20))
        RangeIndex(range(0, 20))
    Input two integer(start, stop).
    >>> RangeIndex(10, 20)
        RangeIndex(range(10, 20))
    """
    def __new__(
        cls, 
        start=None,
        stop=None,
        step=None,
        name=None,
        ):
        
        # RangeIndex, range
        if isinstance(start, RangeIndex):
            if name is None:
                name = start.name
            return start.copy(name=name)
        elif isinstance(start, range):
            return cls._simple_new(start, name)
            
        # validate the arguments
        if all_none(start, stop, step):
            raise TypeError("RangeIndex(...) must be called with integers.")
            
        if start is not None:
            start = cls._ensure_int(start)
        else:
            start = 0
        
        if stop is None:
            (start, stop) = (0, start)
        else:
            stop = cls._ensure_int(stop)
            
        step = cls._ensure_int(step) if step is not None else 1
        if step == 0:
            raise ValueError("Step must not be zero.")
            
        rng = range(start, stop, step)
        
        return cls._simple_new(rng, name=name)
        
            
    @classmethod
    def _simple_new(cls, values: range, name=None):
        result = object.__new__(cls)
        
        assert isinstance(values, (range, RangeIndex))
        
        result._data = values
        result._range = values
        result._name = name
        result._cache = {}
        return result
        
    @classmethod
    def _ensure_int(cls, value):
        new_value = int(value)
        assert new_value == value
        return new_value
            
    def copy(self, name=None):
        try:
            casted = self._data
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"Cannot cast {type(self).__name__}"
                ) from err
        if name is None:
            name = self.name
        return RangeIndex(casted, name=name)
    
    def __len__(self) -> int:
        """
        Return the length of the Index.
        """
        return len(self._data)
    
    def __setitem__(self, key, value):
        raise TypeError("Index does not support mutable operations")
    
    def __getitem__(self, key):
        getitem = self._data.__getitem__
        
        if is_scalar(key):
            return getitem(key)
        
        if isinstance(key, slice):
            result = getitem(key)
            return type(self)._simple_new(result, name=self.name)
        
    def __repr__(self):
        """
        Return a string representation for this object.
        """
        klass_name = type(self).__name__
        data = str(self._data)
        return f"{klass_name}({data})"
    
    @property
    def values(self):
        return self._data
    
    @property
    def data(self):
        return self._data
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def len(self):
        return self.__len__()
        

class DateIndex():
    """
    Immutable sequence used for indexing date.

    Parameters
    ----------
    data : date string, datetime.date, list(...)
    name : str(default None)
        Name of the index.

    Attributes
    ----------
    name : The name of index
    len : The length of the index
    data : Raw data of index
    values : Raw data of index

    Methods
    -------
    copy : Deep copy of the index

    Examples
    --------
    Input one date string.
    >>> DateIndex('2022.01')
        DateIndex(['2022.01.31'])
    >>> DateIndex("2022-3-27")
        DateIndex(['2022.03.27'])
    Input one date type data.
    >>> DateIndex(datetime.date(2022, 1, 1))
        DateIndex(['2022.01.01'])
    Input a list of date string.
    >>> DateIndex(['2022.01', '2022.02', '2022.03'])
        DateIndex(['2022.01.31', '2022.02.28', '2022.03.31'])
    Input a list of date type data.
    >>> DateIndex([date(2022, 1, 31), date(2022, 2, 28)])
        DateIndex(['2022.01.31', '2022.02.28'])
    """
    def __new__(
        cls,
        data=None,
        name=None,
        ):
        
        # DateIndex
        if isinstance(data, DateIndex):
            dtarr = data.copy(name=name)
            
        # string
        elif isinstance(data, str):
            dtarr = [str_to_date(data)]

        # date
        elif isinstance(data, date):
            dtarr = [data]
            
        # list
        elif isinstance(data, list):
            new_lst = []
            for val in data:
                if isinstance(val, date):
                    new_lst.append(val)
                elif isinstance(val, str):
                    new_lst.append(str_to_date(val))
            dtarr = new_lst
        else:
            raise TypeError("There is a problem with the entered data type.")
            
        subarr = cls._simple_new(dtarr, name=name)
        return subarr
        
    @classmethod
    def _simple_new(cls, values: list, name=None):
        result = object.__new__(cls)
        
        assert isinstance(values, (list, DateIndex))
        
        result._data = values
        result._name = name
        result._cache = {}
        return result
        
    def copy(self, name=None):
        try:
            casted = self._data
        except (TypeError, ValueError) as err:
            raise TypeError(
                f"Cannot cast {type(self).__name__}"
                ) from err
        if name is None:
            name = self.name
        return DateIndex(casted, name=name)        
    
    def __len__(self) -> int:
        """
        Return the length of the Index.
        """
        return len(self._data)
    
    def __setitem__(self, key, value):
        raise TypeError("Index does not support mutable operations")
    
    def __getitem__(self, key):
        getitem = self._data.__getitem__
        
        if is_scalar(key):
            return getitem(key)
        
        if isinstance(key, slice):
            result = getitem(key)
            return type(self)._simple_new(result, name=self.name)
        
    def __repr__(self):
        """
        Return a string representation for this object.
        """
        klass_name = type(self).__name__
        data = str([val.strftime("%Y.%m.%d") for val in self._data])
        return f"{klass_name}({data})"
    
    @property
    def values(self):
        return self._data
    
    @property
    def data(self):
        return self._data
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def len(self):
        return self.__len__()


def date_range(
    start=None,
    stop=None,
    periods=None,
    freq=None,
    name=None,
    ) -> DateIndex:
    """
    Return a fixed frequency DateIndex.
    
    Parameters
    ----------
    start : str or datetime.date
        Left bound for generating dates.
    stop : str or datetime.date
        Right bound for generating dates.
    periods : int(>0), optional
        Number of periods to generate.
    freq : str or DateOffset, default 'M'
    
    Returns
    -------
    DateIndex

    Attributes
    ----------
    name : The name of index
    len : The length of the index
    data : Raw data of index
    values : Raw data of index

    Methods
    -------
    copy : Deep copy of the index

    Examples
    --------
    Input a start date and periods.
    >>> date_range("2022.01", 3)
        DateIndex(['2022.01.31', '2022.02.28', '2022.03.31'])
    >>> date_range(date(2022, 1, 1), 3)
        DateIndex(['2022.01.01', '2022.02.28', '2022.03.31'])
    >>> idx = date_range("2022.01", 3)
    >>> idx.len
        3
    >>> idx.data
        [datetime.date(2022, 1, 1), datetime.date(2022, 2, 28), datetime.date(2022, 3, 31)]
    >>> idx.values
        [datetime.date(2022, 1, 1), datetime.date(2022, 2, 28), datetime.date(2022, 3, 31)]
    Input an stop date and periods.
    >>> date_range(stop='2022.12', periods=3)
        DateIndex(['2022.10.31', '2022.11.30', '2022.12.31'])
    Input a start date and an stop date.
    >>> date_range('2022.01', '2022.03')
        DateIndex(['2022.01.31', '2022.02.28', '2022.03.31'])
    """
    
    if freq is None and any_none(periods, start, stop):
        freq = "M"
    
    if allnot_none(start, stop, periods):
        raise ValueError("There are too many data.")
    elif allnot_none(start, periods):
        dtarr = []
        if periods > 0:
            start = str_to_date(start)
            dtarr.append(start)
            dt_next = start
        else:
            raise ValueError(
                "'periods' should be larger than 0."
            )
        for no in range(1, periods):
            dt_next = date_next(dt_next, freq=freq)
            dtarr.append(dt_next)
    elif allnot_none(stop, periods):
        stop = str_to_date(stop)
        start = stop - relativedelta(months=(periods-1))
        return date_range(start, periods=periods)
    elif allnot_none(start, stop):
        if isinstance(stop, int):
            periods = stop
            return date_range(start, periods=periods)
        else:
            dtarr = []
            start = str_to_date(start)
            stop = str_to_date(stop)
            if stop == start:
                dtarr.append(start)
            elif stop > start:
                dtarr.append(start)
                dt_next = start
                while True:
                    if dt_next >= stop:
                        break
                    dt_next = date_next(dt_next, freq=freq)
                    dtarr.append(dt_next)
            elif stop < start:
                raise ValueError("The stop date is before the start date.")
        
    subarr = DateIndex._simple_new(dtarr, name=name)
    return subarr


class Index():
    """
    Immutable sequence used for indexing.

    Parameters
    ----------
    start : int, str or datetime.date, list(date)
    stop : int, str or datetime.date
    step : int
    periods : int(>0), optional
        Number of periods to generate.
    freq : str or DateOffset, default 'M'
    name : name of index

    Returns
    -------
    RangeIndex or DateIndex

    Attributes
    ----------
    name : The name of index
    len : The length of the index
    data : Raw data of index
    values : Raw data of index

    Methods
    -------
    copy : Deep copy of the index

    Examples
    --------
    Input a start date and periods.
    >>> Index("2022.01", 3)
        DateIndex(['2022.01.31', '2022.02.28', '2022.03.31'])
    >>> Index(date(2022, 1, 1), 3)
        DateIndex(['2022.01.01', '2022.02.28', '2022.03.31'])
    >>> idx = Index("2022.01", 3)
    >>> idx.len
        3
    >>> idx.data
        [datetime.date(2022, 1, 1), datetime.date(2022, 2, 28), datetime.date(2022, 3, 31)]
    >>> idx.values
        [datetime.date(2022, 1, 1), datetime.date(2022, 2, 28), datetime.date(2022, 3, 31)]
    Input an stop date and periods.
    >>> Index(stop='2022.12', periods=3)
        DateIndex(['2022.10.31', '2022.11.30', '2022.12.31'])
    Input a start date and an stop date.
    >>> Index('2022.01', '2022.03')
        DateIndex(['2022.01.31', '2022.02.28', '2022.03.31'])
    Input one date string.
    >>> Index('2022.01')
        DateIndex(['2022.01.31'])
    >>> Index("2022-3-27")
        DateIndex(['2022.03.27'])
    Input one date type data.
    >>> Index(datetime.date(2022, 1, 1))
        DateIndex(['2022.01.01'])
    Input a list of date string.
    >>> Index(['2022.01', '2022.02', '2022.03'])
        DateIndex(['2022.01.31', '2022.02.28', '2022.03.31'])
    Input a list of date type data.
    >>> Index([date(2022, 1, 31), date(2022, 2, 28)])
        DateIndex(['2022.01.31', '2022.02.28'])
    Input one integer.
    >>> Index(10, name='IdxA')
        RangeIndex(range(0, 10))
    >>> idxa.name
        'IdxA'
    >>> idxa.copy(name='NewIdxA')
        RangeIndex(range(0, 10))
    Input a RangeIndex.
    >>> Index(idxa)
        RangeIndex(range(0, 10))
    Input a range.
    >>> Index(range(0, 20))
        RangeIndex(range(0, 20))
    Input two integer(start, stop).
    >>> Index(10, 20)
        RangeIndex(range(10, 20))
    """
    def __new__(
        cls,
        start=None,
        stop=None,
        step=None,
        periods=None,
        freq=None,
        name=None,
        ):

        # RangeIndex
        if isinstance(start, RangeIndex):
            if name is None:
                name = start.name
            return RangeIndex(start, name=name)
        if isinstance(start, range):
            return RangeIndex(start, name=name)
        if isinstance(start, int):
            return RangeIndex(start, stop, step, name)
        if start is None:
            if isinstance(stop, int):
                return RangeIndex(start, stop, step, name)

        # DateIndex
        if isinstance(start, DateIndex):
            if name is None:
                name = start.name
            return DateIndex(start, name=name)
        if isinstance(start, str):
            if all_none(stop, step, periods):
                return DateIndex(start, name=name)
        if isinstance(start, date):
            if all_none(stop, step, periods):
                return DateIndex(start, name=name)
        if isinstance(start, list):
            if all_none(stop, step, periods):
                return DateIndex(start, name=name)

        # date_range
        if isinstance(start, (str, date)):
            if isinstance(stop, (int, str, date)):
                return date_range(start, stop, periods=periods, freq=freq, name=name)
        if start is None:
            if isinstance(stop, (str, date)):
                return date_range(start, stop, periods=periods, freq=freq, name=name)

