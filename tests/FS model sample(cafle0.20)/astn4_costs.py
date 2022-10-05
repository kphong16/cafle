from cafle import Account
from functools import partial

from astn0_index import idx
from astn3_loan import loan

cost = Account(idx)
cost.토지비 = cost.subacc('토지비')
with cost.토지비 as c:
    c.amt = 20_000
    c.note = "토지비"
    c.addscd(loan.idxfn[0], c.amt)

cost.공사비 = cost.subacc('공사비')
with cost.공사비 as c:
    c.amt = 70_000
    c.note = "공사비"
    c.amtunt = [c.amt / len(idx.cstrn)] * len(idx.cstrn)
    c.addscd(idx.cstrn, c.amtunt)


def estimate_cost_amt(cost, idxno):
    cst = cost.mrg
    return cst.scd_in[idxno]
cost.estimate_cost_amt = partial(estimate_cost_amt, cost)

def pay_cost_amt(cost, acc, idxno):
    amtttl = 0
    for key, item in cost.dct.items():
        amt = item.scd_in[idxno]
        acc.send(idxno, amt, item, note=f"operating cost: {key}")
        amtttl += amt
    return amtttl
cost.pay_cost_amt = partial(pay_cost_amt, cost)

