"""
Created on Sun Dec 19 17:41:35 2021
Editted on Jul 24 2022

@author: KP_Hong
"""

import xlsxwriter
from datetime import datetime
from pandas import DataFrame
from cafle.genfunc import is_iterable, is_scalar
from collections import namedtuple #, OrderedDict

__all__ = ['Write', 'WriteWS', 'Cell']

class Cell:
    def __new__(cls, row, col):
        cell = namedtuple('Cell', ['row', 'col'])
        return cell(row, col)

def depth_dct(dct):
    tlen = 0
    for item in dct.values():
        if type(item) is dict:
            tlen = max(depth_dct(item), tlen)
        elif is_iterable(item):
            tlen = max(len(item), tlen)
        else:
            tlen = max(1, tlen)
    return 1 + tlen
# 왜 1일 더 높게 책정이 되지??????????

class Write:
    def __init__(self, file_adrs):
        self.file_adrs = file_adrs
        self.wb = xlsxwriter.Workbook(file_adrs)
        self.ws = {}

    def close(self):
        self.wb.close()
        return True

    def write_val(self, cell, val, ws, fmt=None, nxtcell='col'):
        ws = self.return_ws(ws)
        ws.write(cell.row, cell.col, val, fmt)
        row = cell.row
        col = cell.col

        if nxtcell == 'col':
            row += 1
        elif nxtcell == 'row':
            col += 1
        return Cell(row, col)

    def write_row(self, cell, data, ws, fmt=None, nxtcell='col'):
        ws = self.return_ws(ws)
        row = cell.row
        col = cell.col
        dlen = 0

        if not is_iterable(fmt):
            fmt = [fmt] * len(data)

        if not is_iterable(data[0]):
            _col = col
            for val, _fmt in zip(data, fmt):
                ws.write(row, _col, val, _fmt)
                _col += 1
            dlen = max(len(data), dlen)
            row += 1
        elif is_iterable(data[0]):
            for val in data:
                self.write_row(Cell(row, col), val, ws, fmt, nxtcell)
                dlen = max(len(val), dlen)
                row += 1

        if nxtcell == 'row':
            row = cell.row
            col = cell.col + dlen
        return Cell(row, col)

    def write_col(self, cell, data, ws, fmt=None, nxtcell='row'):
        ws = self.return_ws(ws)
        row = cell.row
        col = cell.col
        dlen = 0

        if not is_iterable(fmt):
            fmt = [fmt] * len(data)

        if not is_iterable(data[0]):
            _row = row
            for val, _fmt in zip(data, fmt):
                ws.write(_row, col, val, _fmt)
                _row += 1
            dlen = max(len(data), dlen)
            col += 1
        elif is_iterable(data[0]):
            for val in data:
                self.write_col(Cell(row, col), val, ws, fmt, nxtcell)
                dlen = max(len(val), dlen)
                col += 1

        if nxtcell == 'col':
            row = cell.row + dlen
            col = cell.col
        return Cell(row, col)

    def write_dct_col(self, cell, data, ws, fmt=None, fmtkey=None):
        ws = self.return_ws(ws)
        row = cell.row
        col = cell.col

        for key, item in data.items():
            if isinstance(fmt, dict):
                _fmt = fmt[key]
            else:
                _fmt = fmt
            if not isinstance(item, dict):
                self.write_val(Cell(row, col), key, ws, fmtkey)
                if is_iterable(item):
                    self.write_row(Cell(row, col + 1), item, ws, _fmt)
                    row += 1
                else:
                    self.write_val(Cell(row, col + 1), item, ws, _fmt)
                    row += 1
            elif isinstance(item, dict):
                self.write_val(Cell(row, col), key, ws, fmtkey)
                _cell = self.write_dct_col(Cell(row, col + 1), item, ws, _fmt, fmtkey)
                row = _cell.row
        return Cell(row, col)

    def write_dct_row(self, cell, data, ws, fmt=None, fmtkey=None):
        ws = self.return_ws(ws)
        row = cell.row
        col = cell.col

        for key, item in data.items():
            if isinstance(fmt, dict):
                _fmt = fmt[key]
            else:
                _fmt = fmt
            if not isinstance(item, dict):
                self.write_val(Cell(row, col), key, ws, fmtkey)
                if is_iterable(item):
                    self.write_col(Cell(row + 1, col), item, ws, _fmt)
                    col += 1
                else:
                    self.write_val(Cell(row + 1, col), item, ws, _fmt)
                    col += 1
            elif isinstance(item, dict):
                self.write_val(Cell(row, col), key, ws, fmtkey)
                _cell = self.write_dct_row(Cell(row + 1, col), item, ws, _fmt, fmtkey)
                col = _cell.col
        return Cell(row, col)

    def write_df_row(self, cell, data, ws, fmt=None, fmtkey=None):
        ws = self.return_ws(ws)
        dfdict = data.to_dict()
        idx = data.index
        row = cell.row
        col = cell.col

        self.write_col(Cell(row + 1, col), idx, ws, fmtkey)
        col += 1

        for key, item in dfdict.items():
            if isinstance(fmt, dict):
                _fmt = fmt[key]
            else:
                _fmt = fmt

            self.write_val(Cell(row, col), key, ws, fmtkey)
            for i, val in enumerate(idx, 1):
                self.write_val(Cell(row + i, col), item[val], ws, _fmt)
            col += 1
        return Cell(row, col)

    def write_df_col(self, cell, data, ws, fmt=None, fmtkey=None):
        ws = self.return_ws(ws)
        dfdict = data.to_dict()
        idx = data.index
        row = cell.row
        col = cell.col

        self.write_row(Cell(row, col + 1), idx, ws, fmtkey)
        row += 1

        for key, item in dfdict.items():
            if isinstance(fmt, dict):
                _fmt = fmt[key]
            else:
                _fmt = fmt

            self.write_val(Cell(row, col), key, ws, fmtkey)
            for i, val in enumerate(idx, 1):
                self.write_val(Cell(row, col + i), item[val], ws, _fmt)
            row += 1
        return Cell(row, col)

    #Make Dictionary of Loan
    def dct_loan(self, ln):
        tmpdct = {} #OrderedDict()
        tmpdct["Notional_" + ln.name] = \
            {"scd_out": ln.ntnl._df.scd_out,
             "scd_in": ln.ntnl._df.scd_in,
             "amt_out": ln.ntnl._df.amt_out,
             "amt_in": ln.ntnl._df.amt_in,
             "bal_end": ln.ntnl._df.bal_end}

        if 'IR' in ln.dct.keys():
            tmpdct["IR_" + ln.name] = \
                {"amt_in": ln.IR._df.amt_in,
                 "bal_end": ln.IR._df.bal_end}
        if 'fee' in ln.dct.keys():
            tmpdct["Fee_" + ln.name] = \
                {"amt_in": ln.fee._df.amt_in,
                 "bal_end": ln.fee._df.bal_end}
        if 'fob' in ln.dct.keys():
            tmpdct["Fob_" + ln.name] = \
                {"amt_in": ln.fob._df.amt_in,
                 "bal_end": ln.fob._df.bal_end}
        return tmpdct

    # Make Dictionary of Loan
    def dctprt_loan(self, ln):
        tmpdct = {} #OrderedDict()
        tmpdct["Notional_" + ln.name] = \
            {"인출한도": ln.ntnl._df.scd_out,
             "상환예정": ln.ntnl._df.scd_in,
             "인출금액": ln.ntnl._df.amt_out,
             "상환금액": ln.ntnl._df.amt_in,
             "대출잔액": ln.ntnl._df.bal_end}

        if 'IR' in ln.dct.keys():
            tmpdct["IR_" + ln.name] = \
                {"이자금액": ln.IR._df.amt_in,
                 "누적이자": ln.IR._df.bal_end}
        if 'fee' in ln.dct.keys():
            tmpdct["Fee_" + ln.name] = \
                {"수수료금액": ln.fee._df.amt_in,
                 "누적수수료": ln.fee._df.bal_end}
        if 'fob' in ln.dct.keys():
            tmpdct["미인출_" + ln.name] = \
                {"미인출수수료": ln.fob._df.amt_in,
                 "누적미인출": ln.fob._df.bal_end}
        return tmpdct

    def add_ws(self, wsname):
        self.ws[wsname] = self.wb.add_worksheet(wsname)
        return self.ws[wsname]

    def return_ws(self, wsname):
        if isinstance(wsname, str):
            return self.ws[wsname]
        elif isinstance(wsname, xlsxwriter.worksheet.Worksheet):
            return wsname

    # Text Format
    def fmtnum(self, fmt, **kwargs):
        """
        example of fmt: 'yyyy-mm-dd', '#,##0', '#,##0.0', '0.0%'
        kwargs example: bold=True
        """
        tmpdct = dict({'num_format': fmt, **kwargs})
        return self.wb.add_format(tmpdct)

    @property
    def nml(self):
        return self.wb.add_format({'bold': False})

    @property
    def bold(self):
        return self.wb.add_format({'bold': True})

    @property
    def num(self):
        return self.wb.add_format({'num_format': '#,##0'})

    @property
    def numb(self):
        return self.wb.add_format({'num_format': '#,##0', 'bold': True})

    @property
    def pct(self):
        return self.wb.add_format({'num_format': '0.0%'})

    @property
    def pct2(self):
        return self.wb.add_format({'num_format': '0.00%'})

    @property
    def date(self):
        return self.wb.add_format({'num_format': 'yyyy-mm-dd'})

    @property
    def month(self):
        return self.wb.add_format({'num_format': '#,##0"개월"'})

    @property
    def now(self):
        return datetime.now().strftime('%Y.%m.%d %H:%M:%S')


class WriteWS(Write):
    def __init__(self, ws, cell=Cell(0,0)):
        self.ws = ws
        self.cell = cell

    def __call__(self, data, fmt=None, fmtkey=None, valdrtn='row', drtn='col'):
        if not is_iterable(data):
            self.cell = self.write_val(self.cell, data, self.ws, fmt=fmt, nxtcell=drtn)
        elif isinstance(data, DataFrame):
            if valdrtn == 'row':
                if drtn == 'row':
                    self.cell = self.write_df_row(self.cell, data, self.ws, fmt, fmtkey)
                elif drtn == 'col':
                    _cell = self.write_df_row(self.cell, data, self.ws, fmt, fmtkey)
                    _len = len(data)
                    self.cell = Cell(self.cell.row + _len + 1, self.cell.col)
            elif valdrtn == 'col':
                if drtn == 'col':
                    self.cell = self.write_df_col(self.cell, data, self.ws, fmt, fmtkey)
                elif drtn == 'row':
                    _cell = self.write_df_col(self.cell, data, self.ws, fmt, fmtkey)
                    _len = len(data)
                    self.cell = Cell(self.cell.row, self.cell.col + _len + 1)
        elif is_iterable(data) and not isinstance(data, dict):
            if valdrtn == 'row':
                self.cell = self.write_row(self.cell, data, self.ws, fmt=fmt, nxtcell=drtn)
            if valdrtn == 'col':
                self.cell = self.write_col(self.cell, data, self.ws, fmt=fmt, nxtcell=drtn)
        elif isinstance(data, dict):
            if valdrtn == 'row':
                if drtn == 'row':
                    self.cell = self.write_dct_row(self.cell, data, self.ws, fmt=fmt, fmtkey=fmtkey)
                elif drtn == 'col':
                    _cell = self.write_dct_row(self.cell, data, self.ws, fmt=fmt, fmtkey=fmtkey)
                    _len = self.dctdatalen(data)
                    self.cell = Cell(self.cell.row + _len + 1, self.cell.col)
            if valdrtn == 'col':
                if drtn == 'col':
                    self.cell = self.write_dct_col(self.cell, data, self.ws, fmt=fmt, fmtkey=fmtkey)
                elif drtn == 'row':
                    _cell = self.write_dct_col(self.cell, data, self.ws, fmt=fmt, fmtkey=fmtkey)
                    _len = self.dctdatalen(data)
                    self.cell = Cell(self.cell.row, self.cell.col + _len + 1)
        return self.cell

    def setcell(self, row=None, col=None):
        if isinstance(row, tuple):
            self.cell = row
            return None
        _row = self.cell.row
        _col = self.cell.col
        if row is not None:
            _row = row
        if col is not None:
            _col = col
        self.cell = Cell(_row, _col)
        return None

    def nextcell(self, no=1, drtn='row'):
        _row = self.cell.row
        _col = self.cell.col
        if drtn == 'row':
            _row += no
        elif drtn == 'col':
            _col += no
        self.cell = Cell(_row, _col)
        return self.cell

    def dctdatalen(self, dct):
        _len = 0
        for key, item in dct.items():
            if not isinstance(item, dict):
                if is_iterable(item):
                    _len = max(_len, len(item))
                else:
                    _len = max(_len, 1)
            elif isinstance(item, dict):
                _len = max(_len, 1 + self.dctdatalen(item))
        return _len
