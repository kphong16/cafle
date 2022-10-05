from cafle import Account
from functools import partial

from astn0_index import idx
from astn1_account import acc

equity = Account(idx)
equity.sj = equity.subacc("sj")
with equity.sj as e:
    e.amt = 5_000
    e.subscd(idx[0], e.amt, note="Initial amount")

equity.sb = equity.subacc("sb")
with equity.sb as e:
    e.amt = 3_000
    e.subscd(idx[0], e.amt, note="Initial amount")

def withdraw_equity_amount(equity, idxno, oprtg):
    amt_wtdrw = 0
    for key, val in equity.dct.items():
        _df = val.jnlscd.loc[val.jnlscd.index == idxno]
        for index, row in _df.iterrows():
            val.send(idxno, row.amt_out, oprtg, f'자기자본 납입({key})')
            amt_wtdrw += row.amt_out
    return amt_wtdrw
equity.withdraw_equity_amount = partial(withdraw_equity_amount, equity)

