from collections import namedtuple
import numpy as np

from src import cafle as cf
from src.cafle import (
    Account,
    SetAccount,
)
from src.cafle.standarddata import read_standard_process_rate_table
from inputdata_land import (area)

#### Initial Setting ####
Name = namedtuple('Name', ['title', 'byname'])
untamt = 1_000_000

#### Case Study ####
Case = namedtuple('Case', ['mtrt', 'rate_arng', 'amt_ntnl', 'rate_fee', 'rate_IR', 'rate_rsrv'])
case1 = Case(33, 0.015, 130_000, 0.015, 0.060, 0.15)
case2 = Case(33, 0.015, 130_000, 0.015, 0.065, 0.15)
case3 = Case(33, 0.015, 125_000, 0.015, 0.065, 0.20)
case4 = Case(33, 0.015, 134_000, 0.015, 0.065, 0.10)
case0 = case3

#### Assumption Index ####
class Idx:
    def __init__(self):
        self.prd_cstrn  = 30
        self.mtrt       = case0.mtrt #33
        self.prd_fnc    = self.mtrt + 1
        self.prd_prjt   = self.mtrt + 4

        self.prjt       = cf.date_range("2022.06", periods=self.prd_prjt )
        self.loan       = cf.date_range("2022.07", periods=self.prd_fnc  )
        self.cstrn      = cf.date_range("2022.08", periods=self.prd_cstrn)
idx = Idx()
Account._index = idx.prjt

#### Assumption Financing ####
class Equity:
    def __new__(cls):
        equity = cf.Loan(
            title       = "equity",
            index       = idx.prjt,
            amt_ntnl    = 46_500,
            amt_intl    = 46_500,
        ).this
        equity.ntnl.subscd(idx.prjt[0], equity.amt_ntnl)
        return equity
equity = Equity()

class Loan:
    def __new__(cls):
        loan = cf.Loan(
            index       = idx.prjt,
            idxfn       = idx.loan,

            mtrt        = idx.mtrt,
            rate_arng   = case0.rate_arng, # 0.015,
            title       = [  "tra"],
            rnk         = [      0],
            amt_ntnl    = [case0.amt_ntnl], # 130_000
            amt_intl    = [      0],
            rate_fee    = [case0.rate_fee], # 0.015
            rate_IR     = [case0.rate_IR], # 0.065
            rate_fob    = [  0.005],
        )
        for key, item in loan.dct.items():
            item.ntnl.subscd(item.idxfn[0], item.amt_ntnl)
            item.ntnl.addscd(item.idxfn[-1], item.amt_ntnl)
        return loan
loan = Loan()

class LoanCst(SetAccount):
    def __init__(self, fnc_loan):
        super().__init__()
        self.fnc_loan = fnc_loan

        title, byname = "arngfee", "???????????????"
        acc = self.set_account(title, byname)
        acc.addscd(
            idxval  = idx.loan[0],
            amt     = fnc_loan.amt_arng,
        )
loancst = LoanCst(loan)

#### Assumption Costs ####
class Cost(SetAccount):
    def __init__(self):
        super().__init__()
        self.names = []
        self.key_main = []
        self._set_initial_data()

    def _set_initial_data(self):
        ## ?????????
        sgmnt           = Name("lnd", "?????????")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "lndprchs", "???????????????"
        acc             = self.set_account(title, byname, sgmnt.title)
        acc.amt_ttl     = 54_170.8#?????????
        acc.area        = area.land.py
        acc.note        = f"{acc.area:,.0f}??? x {acc.amt_ttl * 1000 / acc.area:,.0f}??????/???"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        #title, byname   = "aqstntx", "????????????"
        #title, byname   = "jdclscvn", "?????????"
        #title, byname   = "brkrg", "???????????????"

        ## ???????????????
        sgmnt = Name("cstrn", "?????????")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)
        _rate_rsrv = case0.rate_rsrv #0.20
        _prcrate = read_standard_process_rate_table(len(idx.cstrn), tolist=True)

        title, byname = "cvleng", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_unt = 1_890 # ?????????/???
        acc.num_hole = 27 # ???
        acc.amt_ttl = acc.amt_unt * acc.num_hole

        acc.rate_rsrv = _rate_rsrv
        acc.amt_prd = acc.amt_ttl * (1 - acc.rate_rsrv)
        acc.amt_rsrv = acc.amt_ttl * acc.rate_rsrv

        acc.prcrate = _prcrate
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note = f"{acc.num_hole:,.0f}??? x {acc.amt_unt * 1000:,.0f}??????/???"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.prjt[-1], acc.amt_rsrv)

        title, byname = "clubhs", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_unt = 7.0  #?????????/???
        acc.area = 2_800  #???
        acc.amt_ttl = acc.amt_unt * acc.area

        acc.rate_rsrv = _rate_rsrv
        acc.amt_prd = acc.amt_ttl * (1 - acc.rate_rsrv)
        acc.amt_rsrv = acc.amt_ttl * acc.rate_rsrv

        acc.prcrate = _prcrate
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note = f"{acc.area:,.0f}??? x {acc.amt_unt * 1000:,.0f}??????/???"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.prjt[-1], acc.amt_rsrv)

        title, byname = "lightetc", "??????????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_ttl = 9_000  # ?????????/???
        acc.note = f"????????????, ????????????, ??????"

        acc.rate_rsrv = _rate_rsrv
        acc.amt_prd = acc.amt_ttl * (1 - acc.rate_rsrv)
        acc.amt_rsrv = acc.amt_ttl * acc.rate_rsrv

        acc.prcrate = _prcrate
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note = f"?????? {acc.amt_ttl * 1000:,.0f}??????/???"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.prjt[-1], acc.amt_rsrv)

        ## ???????????????
        sgmnt = Name("adcstrn", "???????????????")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "dsncst", "?????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "??????"
        acc.addscd(idx.loan[0], 1_388)

        title, byname = "spvsncst", "?????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "??????"
        acc.addscd(idx.loan[0], 2_800)

        ## ??????????????? ??? ????????????
        sgmnt = Name("consent", "????????? ??? ????????????")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "cnsntcst", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 4_271
        acc.amt_prd = 3_544
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "??????"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "techsrvc", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 1_979
        acc.amt_prd = 700
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "??????"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "txetc", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 8_097.4
        acc.amt_prd = 1_000
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "??????"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "rgstrtnfee", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "?????????????????? ??? x ??? 3.4%"
        # ????????? 2.8%, ????????? 0.2%, ????????? 0.16%, ????????? 0.24%
        acc.addscd(idx.loan[-1], 4_500)

        ## ???????????????
        sgmnt = Name("oprtgcst", "???????????????")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "birdeyeview", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 171.4
        acc.amt_prd = 700
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "??????"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "civilcomplaint", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "??????"
        acc.addscd(idx.loan[0], 500)

        title, byname = "trustfee", "???????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "??????"
        acc.addscd(idx.loan[0], 500)

        title, byname = "srvcetc", "?????????????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "??????"
        acc.addscd(idx.loan[0], 1_000)

        title, byname = "oprtgcpn", "??????????????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_unt = 70
        acc.amt_ttl = len(idx.cstrn) * acc.amt_unt
        acc.note = f"{acc.amt_unt * 1000:,.0f}??????/???, {len(idx.cstrn)}??????"
        acc.addscd(idx.cstrn, [acc.amt_unt] * len(idx.cstrn))

        title, byname = "rsrvfnd", "?????????"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.addscd(idx.loan[-1], 2_000)

        ## ???????????????
        sgmnt = Name("oprtgfclt", "???????????????")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "fcltetc", "???????????? ???"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "??????"
        acc.addscd(idx.prjt[-1], 8_000)
cost = Cost()

#### Assumption Accounts ####
class Acc(SetAccount):
    def __init__(self):
        super().__init__()

        title, byname = "oprtg", "????????????"
        acc = self.set_account(title, byname)

        title, byname = "repay", "????????????"
        acc = self.set_account(title, byname)
acc = Acc()