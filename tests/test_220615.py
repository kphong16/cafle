import sys, os
iprtdrtry = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(iprtdrtry)

from src import cafle as cf
from src.cafle import (
    Account,
    SetAccount,
    EmptyClass,
    Merge,
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

##Initial setting
def cost_set_account(key_main, key_local, byname, tag=None):
    global cost
    tmp = cost.set_account(key_local, byname, tag)
    attr_main = getattr(cost, key_main)
    setattr(attr_main, key_local, tmp)
    attr_main.dct[key_local] = tmp
    return tmp

##Cost2
Account._index = idx.prjt
cost2 = SetAccount('cost2', '사업운영비')
cost2.dct_main = {}
##Land
cost2.land = SetAccount('land', '토지비')
cost2.dct_main['land'] = cost2.land
_ = cost2.set_account('lndprchs', '토지매입비')
_.amt = 14_000
_.area = 9_000
_.addscd(idx.loan[0], _.amt)
cost2.land.get_account(_)

##Cost
Account._index = idx.prjt
cost = SetAccount()
cost.dct_main = {}

##Land
cost.land = EmptyClass()
cost.dct_main["land"] = cost.land
cost.land.dct = {}

#토지매입비
_ = cost.set_account("lndprchs", "토지매입비")
_.amt           = 14_000
_.amt_ttl       = _.amt
_.area          = 9_000#평
_.note          = f"{_.area:,.0f}평 x {_.amt * 1000 / _.area:,.0f}천원/평"
_.addscd(idx.loan[0], _.amt)
cost.land.lndprchs = _
cost.land.dct['lndprchs'] = _
#취등록세
_ = cost.set_account("aqstntx", "취등록세")
_.amt           = 726
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
cost.land.aqstntx = _
cost.land.dct["aqstntx"] = _
#법무사
_ = cost.set_account("jdclscvn", "법무사")
_.amt           = 12
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
cost.land.jdclscvn = _
cost.land.dct["jdclscvn"] = _
#중개수수료
_ = cost.set_account("lndbrkrg", "중개수수료")
_.amt           = 100
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
cost.land.lndbrkrg = _
cost.land.dct["lndbrkrg"] = _
#Set amount of Loan
_ = sum([item.amt for item in cost.land.dct.values()])
cost.land.amt = _
cost.land.amt_ttl = _
cost.land.mrg = Merge(cost.land.dct)


##Operating costs
cost.oprtgcst = EmptyClass()
cost.dct_main["oprtgcst"] = cost.oprtgcst
cost.oprtgcst.dct = {}
cost.oprtgcst.title = "oprtgcst"
cost.oprtgcst.byname = "기타사업비"
#시행사운영비
_ = cost_set_account("oprtgcst", "oprtgcpn", "시행사운영비", tag=["tforaqstntx"])
_.amt_unt       = 30
_.amt           = len(idx.cstrn) * _.amt_unt
_.amt_ttl       = _.amt
_.note          = f"{_.amt_unt * 1000:,.0f}천원/월, {len(idx.cstrn)}개월"
_.addscd(idx.cstrn, [_.amt_unt] * len(idx.cstrn))
#관리신탁수수료
_ = cost_set_account("oprtgcst", "trustfee", "관리신탁수수료", tag=["tforaqstntx"])
_.amt           = 1_000
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
#대리금융기관
_ = cost_set_account("oprtgcst", "dptybnk", "대리금융기관수수료", tag=["tforaqstntx"])
_.amt_unt       = 30
_.amt           = _.amt_unt * 2
_.amt_ttl       = _.amt
_.note          = f"{_.amt_unt * 1000:,.0f}천원, 2년"
_.addscd(idx.loan[0], _.amt_unt)
_.addscd(idx.loan[13], _.amt_unt)
#법무/약정/사평/감평"
_ = cost_set_account("oprtgcst", "lawncstg", "법무/약정/사평/감평", tag=["tforaqstntx"])
_.amt           = 190
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
#유동화비용
_ = cost_set_account("oprtgcst", "spccst", "유동화비용", tag=["tforaqstntx"])
_.amt           = 66
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
#재산세/종부세
_ = cost_set_account("oprtgcst", "prptytx", "재산세/종부세", tag=["tforaqstntx"])
_.amt           = 75
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
#PM수수료
_ = cost_set_account("oprtgcst", "pmfee", "PM수수료", tag=["tforaqstntx"])
_.amt           = 200
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
#보존등기비
_ = cost_set_account("oprtgcst", "rgstrtnfee", "보존등기비", tag=["tforaqstntx"])
_.amt           = 2_456
_.amt_ttl       = _.amt
_.note          = "직간접공사비 등 x 약 3.4%"
# 취득세 2.8%, 농특세 0.2%, 교육세 0.16%, 법무사 0.24%
_.addscd(idx.loan[0], _.amt)
#예비비
_ = cost_set_account("oprtgcst", "rsrvfnd", "예비비", tag=["tforaqstntx"])
_.amt           = 1_000
_.amt_ttl       = _.amt
_.note          = "일식"
_.addscd(idx.loan[0], _.amt)
#Set amount
_ = sum([item.amt for item in cost.oprtgcst.dct.values()])
cost.oprtgcst.amt = _
cost.oprtgcst.amt_ttl = _
cost.oprtgcst.mrg = Merge(cost.oprtgcst.dct)