import pandas as pd
pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
from datetime import date
from collections import namedtuple

from src.cafle import Write, WriteWS, Cell, Area, EmptyClass

#### Initial setting ####


#### Assumption Data ####


#### Input Data ####
from inputdata_land import (land_raw, area)
from assumption import case0

#### Caculation ####
from cashflow import execute_cf
astn = EmptyClass()
astn.idx, astn.equity, astn.loan, astn.loancst, astn.cost, astn.acc = execute_cf()
astn.oprtg = astn.acc.oprtg
astn.area = area
"""
#### Write Data ####
from writedata import WriteData

DATE = date.today().strftime('%y%m%d')
prtname = f"result_{DATE}.xlsx"
prtname0 = f"result_{case0.amt_ntnl/1000:.0f}_{case0.mtrt}_{case0.rate_arng*100}_{case0.rate_fee*100}_{case0.rate_IR*100}_{case0.rate_rsrv*100:.0f}.xlsx"
prtnamet = f"result_test.xlsx"

WriteData(prtnamet, astn)"""