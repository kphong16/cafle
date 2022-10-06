from cafle import (
    Account,
    round_up,
    log10,
    limited,
)
from functools import partial

from astn0_index import idx
from astn1_account import acc

loan = Account(idx)
with loan as l:
    l.mtrt = idx.mtrt
    l.idxfn = idx.loan
    l.is_repaid_all = False

loan.tra = loan.subacc('tra')
with loan.tra as l:
    l.rank = 0
    l.is_wtdrbl = False
    l.is_repaid = False

    l.ntnl = l.subacc('ntnl')
    with l.ntnl as n:
        n.amt = 70_000
        n.intlamt = 10_000
        n.subscd(loan.idxfn[0], n.amt)
        n.addscd(loan.idxfn[-1], n.amt)

    l.IR = l.subacc('IR')
    with l.IR as i:
        i.rate = 0.06
        i.cycle = 1
        i.rate_cycle = i.rate / 12 * i.cycle

    l.fee = l.subacc('fee')
    with l.fee as f:
        f.rate = 0.02

loan.trb = loan.subacc('trb')
with loan.trb as l:
    l.rank = 1
    l.is_wtdrbl = False
    l.is_repaid = False

    l.ntnl = l.subacc('ntnl')
    with l.ntnl as n:
        n.amt = 25_000
        n.intlamt = 15_000
        n.subscd(loan.idxfn[0], n.amt)
        n.addscd(loan.idxfn[-1], n.amt)

    l.IR = l.subacc('IR')
    with l.IR as i:
        i.rate = 0.09
        i.cycle = 1
        i.rate_cycle = i.rate / 12 * i.cycle

    l.fee = l.subacc('fee')
    with l.fee as f:
        f.rate = 0.06

#Decorator
class set_attr:
    def __init__(self, loan):
        self.loan = loan
    def __call__(self, func):
        if isinstance(self.loan, Account):
            setattr(self.loan, func.__name__, partial(func, self.loan))
        elif isinstance(self.loan, dict):
            for item in self.loan.values():
                setattr(item, func.__name__, partial(func, item))

#Rank Iterator
@set_attr(loan)
def getloan(loan, reverse=False, by='rank'):
    lst = list(loan.dct.values())
    if by == 'rank':
        fn = lambda x: x.rank
    else:
        fn = None
    lst.sort(key = fn, reverse=reverse)
    for ln in lst:
        yield ln

#Estimate Loan Cost
@set_attr(loan.dct)
def estimate_fee_amt(loan, idxno):
    if idxno == idx.loan[0]:
        feeamt = loan.ntnl.amt * loan.fee.rate
        loan.fee.addscd(idxno, feeamt, note='fee_amt')
        return feeamt
    return 0

@set_attr(loan.dct)
def estimate_IR_amt(loan, idxno):
    if loan.is_wtdrbl is False:
        return 0
    if loan.is_repaid is True:
        return 0
    ntnlbal = -loan.ntnl.bal_strt[idxno]
    IRamt = ntnlbal * loan.IR.rate_cycle
    if IRamt > 0.0:
        loan.IR.addscd(idxno, IRamt, note='IR_amt')
        return IRamt
    return 0

#Withdraw Loan Amount
@set_attr(loan.dct)
def set_loan_withdrawable(loan, idxno):
    if idxno == idx.loan[0]:
        loan.is_wtdrbl = True

@set_attr(loan.dct)
def withdraw_ntnl_fixed(loan, acc, idxno):
    if idxno != idx.loan[0]:
        return 0
    amt_wtdrw = loan.ntnl.intlamt
    loan.ntnl.send(idxno, amt_wtdrw, acc, "withdraw loan")
    return amt_wtdrw

@set_attr(loan.dct)
def withdraw_ntnl_flexible(loan, acctmp, acc, idxno):
    if idxno < idx.loan[0]:
        return 0
    if loan.is_wtdrbl is False:
        return 0
    if loan.is_repaid is True:
        return 0
    amttopay = acctmp.scd_out[idxno] - acctmp.bal_end[idxno]
    amttopay = limited(round_up(amttopay, -log10(100)), lower=0)
    amtscd_out = loan.ntnl.rsdl_out_cum[idxno]
    amt_wtdrw = limited(amttopay, upper=amtscd_out, lower=0)
    loan.ntnl.send(idxno, amt_wtdrw, acc, "withdraw loan")
    return amt_wtdrw

#Pay Loan Costs
@set_attr(loan.dct)
def pay_fee_amt(loan, acc, idxno):
    feeamt = loan.fee.scd_in[idxno]
    acc.send(idxno, feeamt, loan.fee, f"pay fee amt at {idxno}")
    return feeamt

@set_attr(loan.dct)
def pay_IR_amt(loan, acc, idxno):
    IRamt = loan.IR.scd_in[idxno]
    acc.send(idxno, IRamt, loan.IR, f"pay IR amt at {idxno}")
    return IRamt

#Repay Loan Amount
@set_attr(loan.dct)
def repay_ntnl_amt(loan, acc, idxno):
    #at maturity
    if idxno >= idx.loan[-1]:
        amt_scd_in = loan.ntnl.rsdl_in_cum[idxno]
        acc.send(idxno, amt_scd_in, loan.ntnl, "repay loan")
        return amt_scd_in
    return 0

@set_attr(loan.dct)
def setback_loan_unwithdrawable(loan, idxno):
    if idxno >= idx.loan[-1]:
        loan.is_wtdrbl = False