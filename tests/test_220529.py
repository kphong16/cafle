from src import cafle as cf
from src.cafle import (
    Account,
    SetAccount,
)

#### Assumption Index ####
class Idx:
    def __init__(self):
        self.prd_cstrn  = 30
        self.mtrt       = 33
        self.prd_fnc    = self.mtrt + 1
        self.prd_prjt   = self.mtrt + 4

        self.prjt       = cf.date_range("2022.06", periods=self.prd_prjt )
        self.loan       = cf.date_range("2022.07", periods=self.prd_fnc  )
        self.cstrn      = cf.date_range("2022.08", periods=self.prd_cstrn)
idx = Idx()
Account._index = idx.prjt

#### Assumption Loan ####
loan = cf.Loan(
    index=idx.prjt,
    idxfn=idx.loan,

    mtrt=idx.mtrt,
    rate_arng=0.015,
    title=["tra"],
    rnk=[0],
    amt_ntnl=[130_000],
    amt_intl=[0],
    rate_fee=[0.015],
    rate_IR=[0.065],
    rate_fob=[0.005],
)
for key, item in loan.dct.items():
    item.ntnl.subscd(item.idxfn[0], item.amt_ntnl)
    item.ntnl.addscd(item.idxfn[-1], item.amt_ntnl)

#### Assumption Costs ####
cost3 = SetAccount()
title, byname = "dsncst", "설계비"
acc = cost3.set_account(title, byname, ["adcstrn", "tax"])
acc.note = "일식"
acc.addscd(idx.loan[0], 1_388)

title, byname = "spvsncst", "감리비"
acc = cost3.set_account(title, byname, "adcstrn")
acc.note = "일식"
acc.amt_ttl = 2_800
acc.addscd(idx.loan[0], 2_800)

acc = cost3.set_account("abc", None, "adcstrn")
acc.amt_ttl = 2_200