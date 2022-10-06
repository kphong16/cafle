from cafle import (
    Index,
    Account,
)

idx = Index('2022.10', 30)
idx.mtrt = 26
idx.loan = Index('2022.11', idx.mtrt + 1)
idx.cstrn = Index('2022.11', 24)
