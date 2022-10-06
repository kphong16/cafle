from astn0_index import idx
from astn1_account import acc
from astn2_equity import equity
from astn3_loan import loan
from astn4_costs import cost

def execute_cf():
    for idxno in idx:
        #Check Account Balance
        _ = acc.oprtg.bal_strt[idxno]
        acc.tmp.addamt(idxno, _, note="Initial Balance")

        #Withdraw Equity Amount
        _ = equity.withdraw_equity_amount(idxno, acc.oprtg)
        acc.tmp.addamt(idxno, _, note="Withdraw Equity")

        #Estimate Loan and Operating Costs
        lncst_estmtd = 0
        for ln in loan.getloan(reverse=True):
            lncst_estmtd += ln.estimate_fee_amt(idxno)
            lncst_estmtd += ln.estimate_IR_amt(idxno)

        oprtg_estmtd = 0
        oprtg_estmtd += cost.estimate_cost_amt(idxno)

        acc.tmp.subscd(idxno, (lncst_estmtd + oprtg_estmtd), note="Cost Estimated")

        #Withdraw Loan Amount
        for ln in loan.getloan(reverse=True):
            #breakpoint()
            ln.set_loan_withdrawable(idxno)
            _ = ln.withdraw_ntnl_fixed(acc.oprtg, idxno)
            acc.tmp.addamt(idxno, _, note=f"Withdraw Loan Fixed({ln.name})")

        for ln in loan.getloan(reverse=True):
            _ = ln.withdraw_ntnl_flexible(acc.tmp, acc.oprtg, idxno)
            acc.tmp.addamt(idxno, _, note=f"Withdraw Loan Flexible({ln.name})")

        #Pay Loan and Operating Costs
        for ln in loan.getloan(reverse=False):
            fee = ln.pay_fee_amt(acc.oprtg, idxno)
            IR = ln.pay_IR_amt(acc.oprtg, idxno)
            acc.tmp.subamt(idxno, (fee + IR), note=f"Pay Loan and Fee({ln.name})")

        oprtg = cost.pay_cost_amt(acc.oprtg, idxno)
        acc.tmp.subamt(idxno, oprtg, note="Pay Operating Cost")

        #Repay Loan Amount
        for ln in loan.getloan(reverse=False):
            rpy = ln.repay_ntnl_amt(acc.oprtg, idxno)
            acc.tmp.subamt(idxno, rpy, note=f"Repay Loan Amount({ln.name})")
            ln.setback_loan_unwithdrawable(idxno)

        #Cash Adjustment
        acc.tmp.subamt(idxno, acc.tmp.bal_end[idxno], note="Cash Adjustment")

execute_cf()