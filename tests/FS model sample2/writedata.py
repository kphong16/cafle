from datetime import date
import pandas as pd
from pandas import DataFrame, Series
from cafle import Write, WriteWS, Cell

from cashflow import idx, acc, equity, loan, cost

class WriteData:
    def __init__(self, prtname):
        self.prtname = prtname
        self.wb = Write(self.prtname)

        self._writeastn()

        self.wb.close()

    #Write Assumption
    def _writeastn(self):
        wb = self.wb
        ws = wb.add_ws('assumption')
        ws.set_column("A:K", 12)
        wd = WriteWS(ws, Cell(0, 0))

        #Format
        fmtt = [wb.bold, wb.nml]
        fmtn = [wb.bold, wb.num]
        fmtp = [wb.bold, wb.pct]

        #Write Head
        wd('ASSUMPTION', wb.bold)
        wd('Written at: ' + wb.now)
        wd(self.prtname)
        wd.nextcell(2)

        wd('[Business Overview]', wb.bold)
        wd(['사업명', '복합물류센터 개발사업'], fmtt)
        wd(['사업자명', '안골개발'], fmtt)
        wd(['지역/지구', '계획관리지역'], fmtt)
        wd.nextcell(1)

        wd('[Index]', wb.bold)
        fmtd = [wb.bold, wb.month, wb.date, wb.date]
        wd(['사업기간', len(idx) - 1, idx[0], idx[-1]], fmtd)
        wd(['대출기간', idx.mtrt, idx.loan[0], idx.loan[-1]], fmtd)
        wd(['건축기간', len(idx.cstrn) - 1, idx.cstrn[0], idx.cstrn[-1]], fmtd)
        wd.nextcell(1)

        wd('[Equity]', wb.bold)
        vallst = [
            ('구분', 'name', wb.bold, wb.nml),
            ('출자금액', 'amt', wb.bold, wb.num),
        ]
        for byname, key, fmtkey, fmt in vallst:
            tmplst = [getattr(eqt, key) for eqt in equity.dct.values()]
            wd({byname: tmplst}, fmtkey=fmtkey, fmt=fmt, valdrtn='col')
        wd.nextcell(1)

        wd('[Loan]', wb.bold)
        wd({'구분': [_.name for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.nml, valdrtn='col')
        wd({'순위': [_.rank for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.nml, valdrtn='col')
        wd({'대출금액': [_.ntnl.amt for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.num, valdrtn='col')
        wd({'최초인출': [_.ntnl.intlamt for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.num, valdrtn='col')
        wd({'한도인출': [(_.ntnl.amt - _.ntnl.intlamt) for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.num, valdrtn='col')
        wd({'수수료율': [_.fee.rate for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.pct, valdrtn='col')
        wd({'금리': [_.IR.rate for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.pct, valdrtn='col')
        wd.nextcell(1)

DATE = date.today().strftime('%y%m%d')
prtname = f"Example_{DATE}.xlsx"
WriteData(prtname)