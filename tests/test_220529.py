from src import cafle2 as cf
from src.cafle2 import (
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