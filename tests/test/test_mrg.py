from src.cafle import Index, Account

idx = Index("2023.01", 6)
acc = Account(idx)
acc.abc = acc.subacc("abc")
acc.bca = acc.subacc("bca")

acc.abc.addamt([idx[0], idx[4]], [10, 20])
acc.bca.addamt([idx[2], idx[5]], [100, 300])

