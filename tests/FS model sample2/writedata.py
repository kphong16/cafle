from datetime import date
import pandas as pd
from pandas import DataFrame, Series
#from cafle import Write, WriteWS, Cell, extnddct
from src.cafle import Write, Cell, WriteWS, extnddct
from cashflow import idx, acc, equity, loan, cost

class WriteData:
    def __init__(self, prtname):
        self.prtname = prtname
        self.wb = Write(self.prtname)

        self._writeastn()
        self._writecf()
        self._writeloan()

        self.wb.close()

    #Write Assumption
    def _writeastn(self):
        wb = self.wb
        ws = wb.add_ws('assumption')
        wb.ws['assumption'].set_column("A:K", 12)
        #wd = WriteWS(ws, Cell(0, 0))

        #Format
        fmtt = [wb.bold, wb.nml]
        fmtn = [wb.bold, wb.num]
        fmtp = [wb.bold, wb.pct]

        #Write Head
        ws('ASSUMPTION', wb.bold)
        ws('Written at: ' + wb.now)
        ws(self.prtname)
        ws.nextcell(2)

        ws('[Business Overview]', wb.bold)
        ws(['사업명', '복합물류센터 개발사업'], fmtt)
        ws(['사업자명', '안골개발'], fmtt)
        ws(['지역/지구', '계획관리지역'], fmtt)
        ws.nextcell(1)

        ws('[Index]', wb.bold)
        fmtd = [wb.bold, wb.month, wb.date, wb.date]
        ws(['사업기간', len(idx) - 1, idx[0], idx[-1]], fmtd)
        ws(['대출기간', idx.mtrt, idx.loan[0], idx.loan[-1]], fmtd)
        ws(['건축기간', len(idx.cstrn) - 1, idx.cstrn[0], idx.cstrn[-1]], fmtd)
        ws.nextcell(1)

        ws('[Equity]', wb.bold)
        vallst = [
            ('구분', 'name', wb.bold, wb.nml),
            ('출자금액', 'amt', wb.bold, wb.num),
        ]
        for byname, key, fmtkey, fmt in vallst:
            tmplst = [getattr(eqt, key) for eqt in equity.dct.values()]
            ws({byname: tmplst}, fmtkey=fmtkey, fmt=fmt, valdrtn='col')
        ws.nextcell(1)

        ws('[Loan]', wb.bold)
        ws({'구분': [_.name for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.nml, valdrtn='col')
        ws({'순위': [_.rank for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.nml, valdrtn='col')
        ws({'대출금액': [_.ntnl.amt for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.num, valdrtn='col')
        ws({'최초인출': [_.ntnl.intlamt for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.num, valdrtn='col')
        ws({'한도인출': [(_.ntnl.amt - _.ntnl.intlamt) for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.num, valdrtn='col')
        ws({'수수료율': [_.fee.rate for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.pct, valdrtn='col')
        ws({'금리': [_.IR.rate for _ in loan.dct.values()]}, fmtkey=wb.bold, fmt=wb.pct, valdrtn='col')
        ws.nextcell(1)

        ws(['만기', idx.mtrt], [wb.bold, wb.month])
        ws(['총 대출금액', sum([ln.ntnl.amt for ln in loan.dct.values()])], [wb.bold, wb.num])
        ws.nextcell(1)

    #Write Cashflow
    def _writecf(self):
        wb = self.wb
        ws = wb.add_ws('cashflow')
        wb.ws['cashflow'].set_column("A:A", 12)
        #wd = WriteWS(ws, Cell(0, 0))

        #Write Head
        ws('CASH FLOW', wb.bold)
        ws('Written at: ' + wb.now)
        ws(self.prtname)
        cell = ws.nextcell(2)

        #Write Index
        ws.nextcell(2)
        ws(idx, wb.date, valdrtn='col', drtn='col')
        ws('합계', wb.nml)

        ws.setcell(cell)
        ws.nextcell(1, drtn='col')

        #Write Operating Account Balance
        tmpdct = {
            '운영_기초': extnddct(
                {'기초잔액': acc.oprtg.df.bal_strt},
            ),
            '현금유입': extnddct(
                {'Equity_'+key: list(item.amt_out) for key, item in equity.dct.items()},
                {'Loan_'+key: list(item.ntnl.df.amt_out) for key, item in loan.dct.items()},
            ),
            '상환_loan': extnddct(
                {'상환'+key: list(item.ntnl.df.amt_in) for key, item in loan.dct.items()},
            ),
            '운영_유입': extnddct(
                {'현금유입': list(acc.oprtg.df.amt_in)},
            ),
            '금융비용': extnddct(
                {'Fee_'+key: list(item.fee.df.amt_in) for key, item in loan.dct.items()},
                {'IR_' + key: list(item.IR.df.amt_in) for key, item in loan.dct.items()},
            ),
            '사업비': extnddct(
                {key: list(item.df.amt_in) for key, item in cost.dct.items()},
            ),
            '상환_equity': extnddct(
                {'Equity_'+key: list(item.df.amt_in) for key, item in equity.dct.items()},
            ),
            '운영_유출': extnddct(
                {'현금유출': acc.oprtg.df.amt_out},
            ),
            '운영_기말': extnddct(
                {'기말잔액': acc.oprtg.df.bal_end},
            ),
        }

        #Add Sum
        dctsum = {}
        for key, dct in tmpdct.items():
            dctsum[key] = {}
            for key2, srs in dct.items():
                if key2 in ['기초잔액', '기말잔액']:
                    tmpval = '-'
                else:
                    tmpval = sum(srs)
                dctsum[key][key2] = pd.concat([Series(srs), Series([tmpval], index=['합계'])])

        #Write Dictionary
        ws(dctsum, fmtkey=wb.bold, fmt=wb.num, valdrtn='row', drtn='col')

    #Write Loan
    def _writeloan(self):
        wb = self.wb
        ws = wb.add_ws('financing')
        wb.ws['financing'].set_column("A:A", 12)
        #wd = WriteWS(ws, Cell(0, 0))

        #Write Head
        ws('FINANCING', wb.bold)
        ws('Written at: ' + wb.now)
        ws(self.prtname)
        cell = ws.nextcell(2)

        #Write Index
        ws.nextcell(3)
        ws(idx, wb.date, valdrtn='col', drtn='col')
        ws('합계', wb.nml)

        ws.setcell(cell)
        ws.nextcell(1, drtn='col')

        tmpdct = {}
        #Write Loan
        for key, ln in loan.dct.items():
            tmpdct['Loan_'+key] = wb.dctprt_loan(ln)
        #Write Equity
        _ = {}
        for key, eqt in equity.dct.items():
            _['Equity_' + key] = {
                '인출한도': eqt._df.scd_out,
                '상환예정': eqt._df.scd_in,
                '인출금액': eqt._df.amt_out,
                '상환금액': eqt._df.amt_in,
                '대출잔액': eqt._df.bal_end,
            }
        tmpdct['Equity'] = _
        #Add Sum
        dctsum = {}
        for key, dct in tmpdct.items():
            dctsum[key] = {}
            for key2, dct2 in dct.items():
                dctsum[key][key2] = {}
                for key3, srs in dct2.items():
                    if key3 in ['대출잔액', '누적이자', '누적수수료', '누적미인출']:
                        tmpval = '-'
                    else:
                        tmpval = sum(srs)
                    dctsum[key][key2][key3] = pd.concat([srs, Series([tmpval], index=['합계'])])
        #Write Dictionary
        ws(dctsum, fmtkey=wb.bold, fmt=wb.num, valdrtn='row', drtn='col')

DATE = date.today().strftime('%y%m%d')
prtname = f"Example_{DATE}.xlsx"
WriteData(prtname)