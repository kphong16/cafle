import pandas as pd
pd.set_option('display.max_row', 200)
pd.set_option('display.max_columns', 200)

from src.cafle import (
    Area,
    EmptyClass,
)

__all__ = ['land_raw', 'area']

#### Land Data ####
land_raw = pd.read_excel("data/1. 양양 샤르망 편입토지조서 (version 1) 2022-03-24.xlsx",
                         sheet_name = "인허가 기준",
                         header = 1,
                         usecols = "A:X"
                         )
land_raw.columns = ['연번', '소재지', '지번', '지목', '공부면적', '편입면적', '허가면적',
       '원형보전면적', '관광시설면적', '콘도1_면적', '호텔_면적',
       '콘도2_면적', '콘도3_면적', '콘도4_면적', '판매시설_면적',
       '근생_면적', '체육시설면적', '소유자', '소유자_주소', '관계인',
       '관계인_주소', '관계인_권리', '관계인_신탁원부', '비고']

list_drop = [1]
land_raw.drop(labels    = list_drop,
              axis      = 0,
              inplace   = True,)
land_raw = land_raw.loc[-pd.isna(land_raw.연번)]


area = EmptyClass()
area.land = Area(2_055_084)
area.공부 = Area(land_raw['공부면적'].sum())
area.편입 = Area(land_raw['편입면적'].sum())
area.허가 = Area(land_raw['허가면적'].sum())
area.원형보전 = Area(land_raw['원형보전면적'].sum())
area.관광시설 = Area(land_raw['관광시설면적'].sum())
area.콘도1 = Area(land_raw['콘도1_면적'].sum())
area.콘도2 = Area(land_raw['콘도2_면적'].sum())
area.콘도3 = Area(land_raw['콘도3_면적'].sum())
area.콘도4 = Area(land_raw['콘도4_면적'].sum())
area.호텔 = Area(land_raw['호텔_면적'].sum())
area.판매시설 = Area(land_raw['판매시설_면적'].sum())
area.근생 = Area(land_raw['근생_면적'].sum())
area.체육시설 = Area(land_raw['체육시설면적'].sum())

def rate(val):
    ttlsum = land_raw.편입면적.sum()
    return sum(val) / ttlsum
area.편입피봇 = land_raw.pivot_table('편입면적', '소유자', aggfunc=['sum', 'count', rate])
area.편입피봇.columns = ['Sum', 'Count', 'Rate']
#################