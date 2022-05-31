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

        title, byname = "arngfee", "주관수수료"
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
        ## 토지비
        sgmnt           = Name("lnd", "토지비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname   = "lndprchs", "토지매입비"
        acc             = self.set_account(title, byname, sgmnt.title)
        acc.amt_ttl     = 54_170.8#백만원
        acc.area        = area.land.py
        acc.note        = f"{acc.area:,.0f}평 x {acc.amt_ttl * 1000 / acc.area:,.0f}천원/평"
        acc.addscd(idx.loan[0], acc.amt_ttl)

        #title, byname   = "aqstntx", "취등록세"
        #title, byname   = "jdclscvn", "법무사"
        #title, byname   = "brkrg", "중개수수료"

        ## 도급공사비
        sgmnt = Name("cstrn", "공사비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)
        _rate_rsrv = case0.rate_rsrv #0.20
        _prcrate = read_standard_process_rate_table(len(idx.cstrn), tolist=True)

        title, byname = "cvleng", "토목공사비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_unt = 1_890 # 백만원/홀
        acc.num_hole = 27 # 홀
        acc.amt_ttl = acc.amt_unt * acc.num_hole

        acc.rate_rsrv = _rate_rsrv
        acc.amt_prd = acc.amt_ttl * (1 - acc.rate_rsrv)
        acc.amt_rsrv = acc.amt_ttl * acc.rate_rsrv

        acc.prcrate = _prcrate
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note = f"{acc.num_hole:,.0f}홀 x {acc.amt_unt * 1000:,.0f}천원/홀"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.prjt[-1], acc.amt_rsrv)

        title, byname = "clubhs", "클럽하우스"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_unt = 7.0  #백만원/홀
        acc.area = 2_800  #평
        acc.amt_ttl = acc.amt_unt * acc.area

        acc.rate_rsrv = _rate_rsrv
        acc.amt_prd = acc.amt_ttl * (1 - acc.rate_rsrv)
        acc.amt_rsrv = acc.amt_ttl * acc.rate_rsrv

        acc.prcrate = _prcrate
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note = f"{acc.area:,.0f}평 x {acc.amt_unt * 1000:,.0f}천원/평"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.prjt[-1], acc.amt_rsrv)

        title, byname = "lightetc", "조명공사기타"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_ttl = 9_000  # 백만원/홀
        acc.note = f"조명공사, 철탑공사, 기타"

        acc.rate_rsrv = _rate_rsrv
        acc.amt_prd = acc.amt_ttl * (1 - acc.rate_rsrv)
        acc.amt_rsrv = acc.amt_ttl * acc.rate_rsrv

        acc.prcrate = _prcrate
        acc.prcrate_cml = np.cumsum(acc.prcrate).tolist()
        acc.note = f"전체 {acc.amt_ttl * 1000:,.0f}천원/평"
        acc.addscd(
            idx.cstrn,
            [acc.amt_prd * rt for rt in acc.prcrate]
        )
        acc.addscd(idx.prjt[-1], acc.amt_rsrv)

        ## 간접공사비
        sgmnt = Name("adcstrn", "간접공사비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "dsncst", "설계비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "일식"
        acc.addscd(idx.loan[0], 1_388)

        title, byname = "spvsncst", "감리비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "일식"
        acc.addscd(idx.loan[0], 2_800)

        ## 인허가비용 및 분부담금
        sgmnt = Name("consent", "인허가 및 분부담금")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "cnsntcst", "인허가비용"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 4_271
        acc.amt_prd = 3_544
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "일식"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "techsrvc", "기술용역비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 1_979
        acc.amt_prd = 700
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "일식"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "txetc", "제세공과금"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 8_097.4
        acc.amt_prd = 1_000
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "일식"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "rgstrtnfee", "보존등기비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "직간접공사비 등 x 약 3.4%"
        # 취득세 2.8%, 농특세 0.2%, 교육세 0.16%, 법무사 0.24%
        acc.addscd(idx.loan[-1], 4_500)

        ## 기타운영비
        sgmnt = Name("oprtgcst", "기타운영비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "birdeyeview", "조감도제작"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_injctd = 171.4
        acc.amt_prd = 700
        acc.amt_ttl = acc.amt_injctd + acc.amt_prd
        acc.note = "일식"
        acc.addscd(idx.prjt[0], acc.amt_injctd)
        acc.addscd(idx.loan[0], acc.amt_prd)

        title, byname = "civilcomplaint", "민원처리비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "일식"
        acc.addscd(idx.loan[0], 500)

        title, byname = "trustfee", "신탁수수료"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "일식"
        acc.addscd(idx.loan[0], 500)

        title, byname = "srvcetc", "기타용역수수료"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "일식"
        acc.addscd(idx.loan[0], 1_000)

        title, byname = "oprtgcpn", "시행사운영비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.amt_unt = 70
        acc.amt_ttl = len(idx.cstrn) * acc.amt_unt
        acc.note = f"{acc.amt_unt * 1000:,.0f}천원/월, {len(idx.cstrn)}개월"
        acc.addscd(idx.cstrn, [acc.amt_unt] * len(idx.cstrn))

        title, byname = "rsrvfnd", "예비비"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.addscd(idx.loan[-1], 2_000)

        ## 운영설비비
        sgmnt = Name("oprtgfclt", "운영설비비")
        self.names.append(sgmnt)
        self.key_main.append(sgmnt.title)

        title, byname = "fcltetc", "운영설비 등"
        acc = self.set_account(title, byname, sgmnt.title)
        acc.note = "일식"
        acc.addscd(idx.prjt[-1], 8_000)
cost = Cost()

#### Assumption Accounts ####
class Acc(SetAccount):
    def __init__(self):
        super().__init__()

        title, byname = "oprtg", "운영계좌"
        acc = self.set_account(title, byname)

        title, byname = "repay", "상환계좌"
        acc = self.set_account(title, byname)
acc = Acc()