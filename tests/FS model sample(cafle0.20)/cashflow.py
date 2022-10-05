from cafle import Account

from astn0_index import idx
from astn1_account import acc
from astn2_equity import equity
from astn3_loan import loan
from astn4_costs import cost

def execute_cf():
    global idxno
    global amt_rqrd
    global amt_wtdrw
    for idxno in idx:
        #Withdraw Equity Amount
        equity.withdraw_equity_amount(idxno, acc.oprtg)

        #Estimate Loan and Operating Costs
        lncst_estmtd = 0
        lncst_estmtd += loan.estimate_fee_amt(idxno)
        lncst_estmtd += loan.estimate_IR_amt(idxno)

        oprtg_estmtd = 0
        oprtg_estmtd += cost.estimate_cost_amt(idxno)

        #Withdraw Loan Amount
        loan.set_loan_withdrawable(idxno)
        loan.withdraw_ntnl_fixed(acc.oprtg, idxno)

        #Pay Loan and Operating Costs
        loan.pay_fee_amt(acc.oprtg, idxno)
        loan.pay_IR_amt(acc.oprtg, idxno)

        cost.pay_cost_amt(acc.oprtg, idxno)

        #Repay Loan Amount
        loan.repay_ntnl_amt(acc.oprtg, idxno)
        loan.setback_loan_unwithdrawable(idxno)
execute_cf()