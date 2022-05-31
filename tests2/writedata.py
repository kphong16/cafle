import pandas as pd
from pandas import DataFrame, Series
pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', 200)
from datetime import date
from collections import namedtuple

from src.cafle import Write, WriteWS, Cell, Area, EmptyClass

class WriteData:
    idx = None
    oprtg = None
    equity = None
    loan = None
    loancst = None
    cost = None
    area = None
    acc = None

    def __init__(self, prtname, astn):
        self.prtname = prtname
        self.astn = astn
        self.wb = Write(self.prtname)

        # Setting Variables
        global idx, oprtg, equity, loan, loancst, cost, area, acc
        idx = self.astn.idx
        oprtg = self.astn.oprtg
        equity = self.astn.equity
        loan = self.astn.loan
        loancst = self.astn.loancst
        cost = self.astn.cost
        acc = self.astn.acc
        area = self.astn.area

        self._writeastn()
        self._writecf()
        self._writeloan()
        self._writefbal()
        # _writecstrn()

        self.wb.close()

    #### Write assumption ####
    def _writeastn(self):
        global idx, oprtg, equity, loan, loancst, cost, prtname, area
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("assumption")
        wd = WriteWS(ws, Cell(0,0))

        ## Write loan astn
        fmt = [wb.bold, wb.month, wb.date, wb.date]
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]

        # Write Head
        ws.set_column("A:K", 12)
        wd("ASSUMPTION", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.prtname)
        wd.nextcell(2)

        wd("[Business Overview]", wb.bold)
        wd(["사업명", "양양 샤르망 골프리조트 조성사업(대중제)"], [wb.bold, wb.nml])
        wd(["사업자명", "리건종합건설"], [wb.bold, wb.nml])
        wd(["위치", "강원도 양양군 현남면 임호정리 산107번지 일원"], [wb.bold, wb.nml])
        wd(["지역/지구", "계획관리지역"], [wb.bold, wb.nml])
        wd(["용도", "계획관리지역 / 체육관광휴양지구(제2종지구단위계획구역"], [wb.bold, wb.nml])
        wd(["대지면적", f"{area.land.m2:,.0f}㎡ ({area.land.py:,.0f}평)"], [wb.bold, wb.nml])
        wd(["법률사항", "국토의 계획 및 이용에 관한 법률 제25조 및 제26조"], [wb.bold, wb.nml])
        wd.nextcell(1)

        wd('[Index]', wb.bold)
        _idx = idx
        wd(['사업기간', _idx.prd_prjt, _idx.prjt[0], _idx.prjt[-1]], fmt)
        wd(['대출기간', _idx.mtrt, _idx.loan[0], _idx.loan[-1]], fmt)
        wd(['건설기간', _idx.prd_cstrn, _idx.cstrn[0], _idx.cstrn[-1]], fmt)
        wd.nextcell(1)

        wd('[Cost: 도급공사비]', wb.bold)
        cstrnttl = cost.cvleng.amt_ttl + cost.clubhs.amt_ttl + cost.lightetc.amt_ttl
        wd(['총 공사비', cstrnttl], [wb.bold, wb.num])
        wd(['토목공사비', cost.cvleng.amt_ttl], [wb.bold, wb.num])
        wd(['클럽하우스', cost.clubhs.amt_ttl], [wb.bold, wb.num])
        wd(['조명공사기타', cost.lightetc.amt_ttl], [wb.bold, wb.num])
        wd.nextcell(1)

        wd('[Equity]', wb.bold)
        vallst = [
            ('title', '구분', fmt1),
            ('amt_ntnl', '대출금액', fmt1),
            ('amt_intl', '최초인출', fmt1),
        ]
        for _key, _byname, _fmt in vallst:
            tmplst = [getattr(_eqt, _key) for _eqt in equity.dct.values()]
            wd({_byname: tmplst}, _fmt)
        wd.nextcell(1)

        wd('[Loan]', wb.bold)
        vallst = [
            ('title', '구분', fmt1),
            ('rnk', '순위', fmt1),
            ('amt_ntnl', '대출금액', fmt1),
            ('amt_intl', '최초인출', fmt1),
            ('rate_fee', '수수료율', fmt2),
            ('rate_IR', '금리', fmt2),
            ('rate_fob', '미인출수수료', fmt2),
            ('allin', 'All_in', fmt2),
        ]
        for _key, _byname, _fmt in vallst:
            tmplst = [getattr(_loan, _key) for _loan in loan.dct.values()]
            wd({_byname: tmplst}, _fmt)
        wd.nextcell(1)

        wd(['만기', _idx.mtrt], [wb.bold, wb.month])
        wd(['총 대출금액', loan.ttl_ntnl], fmt1)
        wd(['주관수수료', loan.rate_arng], fmt2)
        allin_ttl = loan.allin_ttl() + loan.rate_arng / loan.mtrt * 12
        wd(['총괄 All_in', allin_ttl], fmt2)

    #### Write cashflow ####
    def _writecf(self):
        global idx, oprtg, equity, loan, loancst, cost, prtname

        # new worksheet
        wb = self.wb
        ws = wb.add_ws("cashflow")
        wd = WriteWS(ws, Cell(0, 0))

        ## Write head
        ws.set_column(0, 0, 12)
        wd("CASH FLOW", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.prtname)
        cell = wd.nextcell(2)

        ## Write index
        wd.nextcell(2)
        wd(idx.prjt, wb.date, valdrtn='col', drtn='row')
        wd("sum", wb.nml)

        wd.setcell(cell)
        wd.nextcell(1, drtn='col')

        ## Write operating account balance
        tmpfmt = [wb.bold, wb.bold, wb.num]
        tmpdct = {
            "운영_기초": wb.extnddct(
                {"기초잔액": oprtg.df.bal_strt},
            ),
            "현금유입": wb.extnddct(
                {"Equity": equity.ntnl.df.amt_out},
                {"Loan_" + key: item.ntnl.df.amt_out for key, item in loan.dct.items()},
                #{"매출_" + item.byname: item.df.amt_out for key, item in sales.dct.items()},
            ),
            "상환_loan": wb.extnddct(
                {"상환_" + key: item.ntnl.df.amt_in for key, item in loan.dct.items()},
            ),
            "운영_유입": wb.extnddct(
                {"현금유입": oprtg.df.amt_in},
            ),
            "조달비용": wb.extnddct(
                {item.byname: item.df.amt_in for key, item in loancst.dct.items()},
            ),
            "금융비용": wb.extnddct(
                {"Fee_" + key: item.fee.df.amt_in for key, item in loan.dct.items()},
                {"IR_" + key: item.IR.df.amt_in for key, item in loan.dct.items()},
                {"미인출_" + key: item.fob.df.amt_in for key, item in loan.dct.items() if item.rate_fob > 0},
            ),
        }

        ## Write operating costs
        tmpdct = wb.extnddct(
            tmpdct,
            {name.byname: {item.byname: item.df.amt_in for key, item in cost.dctsgmnt[name.title].items()}
             for name in cost.names}
        )

        tmpdct = wb.extnddct(
            tmpdct, {
                "상환_equity":
                    {"Equity": equity.ntnl.df.amt_in},
                "운영_유출":
                    {"현금유출": oprtg.df.amt_out},
                "운영_기말":
                    {"기말잔액": oprtg.df.bal_end},
            })

        ## Add sum
        dctsum = {}
        for key, dct in tmpdct.items():
            dctsum[key] = {}
            for key2, srs in dct.items():
                if key2 in ['기초잔액', '기말잔액']:
                    tmpval = "-"
                else:
                    tmpval = sum(srs)
                dctsum[key][key2] = pd.concat([srs, Series([tmpval], index=['합계'])])

        ## Write dictionary
        wd(dctsum, tmpfmt, valdrtn='col', drtn='row')


    #### Write Loan ####
    def _writeloan(self):
        global idx, oprtg, equity, loan, loancst, cost, prtname

        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("financing")
        wd = WriteWS(ws, Cell(0, 0))

        # Write Head
        ws.set_column("A:A", 12)
        wd("FINANCING", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.prtname)
        cell = wd.nextcell(2)

        # Write Index
        wd.nextcell(3)
        wd(idx.prjt, wb.date, valdrtn='col', drtn='row')
        wd("sum", wb.nml)

        wd.setcell(cell)
        wd.nextcell(1, drtn='col')

        tmpfmt = [wb.bold, wb.bold, wb.bold, wb.num]
        tmpdct = {}
        # Write Loan
        for rnk in loan.rnk:
            tmpdct["Loan_" + loan.by_rnk(rnk).title] = wb.dctprt_loan(loan.by_rnk(rnk))
        # Write Equity
        tmpdct["Equity_" + equity.title] = wb.dctprt_loan(equity)

        ## Add sum
        dctsum = {}
        for key, dct in tmpdct.items():
            dctsum[key] = {}
            for key2, dct2 in dct.items():
                dctsum[key][key2] = {}
                for key3, srs in dct2.items():
                    if key3 in ['대출잔액', '누적이자', '누적수수료', '누적미인출']:
                        tmpval = "-"
                    else:
                        tmpval = sum(srs)
                    dctsum[key][key2][key3] = pd.concat([srs, Series([tmpval], index=['sum'])])

        # Write Dictionary
        wd(dctsum, tmpfmt, valdrtn='col', drtn='row')
        # wb.write_dct_col("financing", row, col, tmpdct, tmpfmt)

    #### Write Financial Balance Table ####
    def _writefbal(self):
        global idx, oprtg, equity, loan, loancst, cost, prtname
        idx = idx.prjt

        # new worksheet
        wb = self.wb
        ws = wb.add_ws("financial_balance")
        wd = WriteWS(ws, Cell(0, 0))
        amt_lst = []

        ## Write head
        ws.set_column("A:A", 16)
        ws.set_column("B:B", 22)
        ws.set_column("C:D", 14)
        ws.set_column("E:E", 40)
        wd("Financial Balance Table", wb.bold)
        wd("Written at:" + wb.now)
        wd(self.prtname)
        cell = wd.nextcell(2)

        ## Write financial balance table
        fmt1 = [wb.bold, wb.num]
        fmt2 = [wb.bold, wb.pct]
        fmt3 = [wb.bold, wb.num, wb.date, wb.date]
        fmt4 = [wb.bold, wb.nml, wb.num]

        ## Costs
        wd('Costs', wb.bold)
        cell = wd(['구분1', '구분2', '금액', '비율', '비고'], wb.bold)
        ttl_costs = 0

        # Write operating costs
        for name in cost.names:
            wd(name.byname, wb.bold, drtn='col')
            keym = name.title

            sum_balend = 0
            for key, item in cost.dctsgmnt[keym].items():
                _val = item.bal_end[-1]
                if 'note' in item.__dict__.keys():
                    wd([item.byname, _val, "", item.note], [wb.nml, wb.num, wb.nml, wb.nml])
                else:
                    wd([item.byname, _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            ttl_costs += sum_balend
            wd(["subtotal", sum_balend], [wb.bold, wb.num])
            amt_lst.append(sum_balend)
            wd.nextcell(-1, 'col')

        # Write financing costs
        for rnk in loan.rnk:
            ln = loan.by_rnk(rnk)
            wd("대출_" + ln.title, wb.bold, drtn='col')

            sum_balend = 0
            if ln.rate_fee > 0:
                _val = ln.fee.bal_end[-1]
                wd(["fee", _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            if ln.rate_IR > 0:
                _val = ln.IR.bal_end[-1]
                wd(["IR", _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            if ln.rate_fob > 0:
                _val = ln.fob.bal_end[-1]
                wd(["미인출", _val], [wb.nml, wb.num])
                sum_balend += _val
                amt_lst.append(_val)
            ttl_costs += sum_balend
            wd(["subtotal", sum_balend], [wb.bold, wb.num])
            amt_lst.append(sum_balend)
            wd.nextcell(-1, 'col')

        for key, item in loancst.dct.items():
            wd(item.byname, wb.bold, drtn='col')

            wd(["", item.bal_end[-1]], [wb.nml, wb.num])
            amt_lst.append(item.bal_end[-1])
            ttl_costs += item.bal_end[-1]
            wd.nextcell(-1, 'col')

        wd(["Total", "", ttl_costs], [wb.bold, wb.nml, wb.num])
        amt_lst.append(ttl_costs)

        # Write ratio
        wb.write_col(
            Cell(cell.row, cell.col + 3),
            [val / ttl_costs for val in amt_lst],
            fmt=wb.pct,
            wsname=ws)

        wd.setcell(Cell(cell.row + len(amt_lst), cell.col))
        wd.nextcell(2)
        ## Profit
        wd('Funding', wb.bold)
        wd(['자기자본', '', equity.amt_ntnl], [wb.bold, wb.num, wb.num])
        wd(['PF대출', '', loan.amt_ntnl[0]], [wb.bold, wb.num, wb.num])
        wd(['총사업비', '', ttl_costs], [wb.bold, wb.num, wb.num])
        amt_reserved = ttl_costs - equity.amt_ntnl - loan.amt_ntnl[0]
        wd(['유보사업비', '', amt_reserved], [wb.bold, wb.num, wb.num])

        #wd(['사업이익', '', equity.amt_ntnl + ttl_sales - ttl_costs], [wb.bold, wb.num, wb.numb])


    """#### Write Construction ####
    def _writecstrn(self):
        global idx, oprtg, equity, loan, loancst, cost, prtname
    
        # New Worksheet
        wb = self.wb
        ws = wb.add_ws("construction")
        wd = WriteWS(ws, Cell(0, 0))
    
        # Write Head
        ws.set_column("A:E", 13)
        wd("CONSTRUCTION", wb.bold)
        wd("Written at: " + wb.now)
        wd(self.prtname)
    
        # Write Note
        wd(['총 공사비', cost.drtcstrn.amt_ttl], [wb.bold, wb.num])
        wd(['기성공사비', cost.drtcstrn.amt_prd], [wb.bold, wb.num])
        wd(['유보공사비', cost.drtcstrn.amt_rsrv], [wb.bold, wb.num])
        wd(['유보비율', cost.drtcstrn.rate_rsrv], [wb.bold, wb.pct])
        wd(['총 면적', cost.drtcstrn.area_ttl], [wb.bold, wb.num])
        wd(['단위공사비', cost.drtcstrn.amt_unt * 1_000], [wb.bold, wb.num])
        wd(['비고', cost.drtcstrn.note], [wb.bold, wb.nml])
    
        # Write index and data
        wd.nextcell(2)
        wd(['Index', '공정률', '누적공정률', '공사비', '누적공사비'], wb.bold)
        wd(idx.cstrn, wb.date, 'col', 'col')
        wd(cost.drtcstrn.prcrate, wb.pct, 'col', 'col')
        wd(cost.drtcstrn.prcrate_cml, wb.pct, 'col', 'col')
    
        _amt = [cost.drtcstrn.amt_prd * val for val in cost.drtcstrn.prcrate]
        _amt[-1] = _amt[-1] + cost.drtcstrn.amt_rsrv
        wd(_amt, wb.num, 'col', 'col')
    
        _amt_cml = np.cumsum(_amt).tolist()
        cell = wd(_amt_cml, wb.num, 'col', 'row')
        wd.setcell(cell.row, 0)"""



