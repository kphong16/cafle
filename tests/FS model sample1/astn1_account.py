from cafle import Account

from astn0_index import idx

acc = Account(idx)
acc.oprtg = acc.subacc("oprtg")
acc.repay = acc.subacc("repay")
