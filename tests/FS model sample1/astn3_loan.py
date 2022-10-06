from cafle import Account
from functools import partial

from astn0_index import idx
from astn1_account import acc

loan = Account(idx)
with loan as l:
    l.mtrt = idx.mtrt
    l.idxfn = idx.loan
    l.is_wtdrbl = False
    l.is_repaid = False

loan.ntnl = loan.subacc('ntnl')
with loan.ntnl as l:
    l.amt = 65_000
    l.subscd(loan.idxfn[0], l.amt)
    l.addscd(loan.idxfn[-1], l.amt)

loan.IR = loan.subacc('IR')
with loan.IR as l:
    l.rate = 0.08
    l.cycle = 1
    l.rate_cycle = l.rate / 12 * l.cycle

loan.fee = loan.subacc('fee')
with loan.fee as l:
    l.rate = 0.02

#Estimate Loan Cost
def estimate_fee_amt(loan, idxno):
    if idxno == loan.idxfn[0]:
        feeamt = loan.ntnl.amt * loan.fee.rate
        loan.fee.addscd(idxno, feeamt, note='fee_amt')
        return feeamt
    return 0
loan.estimate_fee_amt = partial(estimate_fee_amt, loan)

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
loan.estimate_IR_amt = partial(estimate_IR_amt, loan)

#Withdraw Loan Amount
def set_loan_withdrawable(loan, idxno):
    if idxno == loan.idxfn[0]:
        loan.is_wtdrbl = True
loan.set_loan_withdrawable = partial(set_loan_withdrawable, loan)

def withdraw_ntnl_fixed(loan, acc, idxno):
    amt_wtdrw = loan.ntnl.scd_out[idxno]
    loan.ntnl.send(idxno, amt_wtdrw, acc, "withdraw loan")
loan.withdraw_ntnl_fixed = partial(withdraw_ntnl_fixed, loan)

#Pay Loan Costs
def pay_fee_amt(loan, acc, idxno):
    feeamt = loan.fee.scd_in[idxno]
    acc.send(idxno, feeamt, loan.fee, f"pay fee amt at {idxno}")
    return feeamt
loan.pay_fee_amt = partial(pay_fee_amt, loan)

def pay_IR_amt(loan, acc, idxno):
    IRamt = loan.IR.scd_in[idxno]
    acc.send(idxno, IRamt, loan.IR, f"pay IR amt at {idxno}")
    return IRamt
loan.pay_IR_amt = partial(pay_IR_amt, loan)

#Repay Loan Amount
def repay_ntnl_amt(loan, acc, idxno):
    #at maturity
    if idxno >= idx.loan[-1]:
        amt_scd_in = loan.ntnl.rsdl_in_cum[idxno]
        acc.send(idxno, amt_scd_in, loan.ntnl, "repay loan")
loan.repay_ntnl_amt = partial(repay_ntnl_amt, loan)

def setback_loan_unwithdrawable(loan, idxno):
    if idxno >= idx.loan[-1]:
        loan.is_wtdrbl = False
loan.setback_loan_unwithdrawable = partial(setback_loan_unwithdrawable, loan)