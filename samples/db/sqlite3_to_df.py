# -*- coding: utf-8 -*-#

# -------------------------------------------------------------------------------
# Name:         sqlite3_to_df
# Description:
# Author:       Administrator
# Date:         2021/12/9
# desc: Copyright © Administrator All rights reserved.
# -------------------------------------------------------------------------------

import sys
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List,Dict

res_path = "/Users/viviwu/Dev/data"

class DataLoader:

    def __init__(self, start_date=None, end_date=None):
        self.trading_dates: List = []
        self.data: List[List] = []
        self.stk_data: List[Dict] = []
        self.idx_data: pd.DataFrame = None
        self.data: List[List] = []

        self.start_date = '2020-12-28'      #'2020-01-02'
        self.end_date = '2020-12-28'
        if start_date is not None:
            self.start_date = start_date
        if end_date is not None:
            self.end_date = end_date

    def load_calendar_from_db(self):

        with sqlite3.connect("%s/trade_sys.db"%(res_path)) as conn:
            sql_cmd = "SELECT * FROM trading_dates where trading_date >= '%s' and trading_date <= '%s' " % (
            self.start_date, self.end_date)
            # sql_cmd = "SELECT * FROM self.trading_dates where trading_date = '2021-12-01'"
            df = pd.read_sql(sql_cmd, con=conn)
            self.trading_dates = df['trading_date'].to_list()
            # func = lambda d: datetime.strptime(d, "%Y-%m-%d")
            # self.trading_dates = df['trading_date'].map(func).to_list()
            print('self.trading_dates； ', type(self.trading_dates[0]), self.trading_dates)  # ['2020-01-02']

    def load_bars_from_db(self):

        with sqlite3.connect("%/daybars.db"%(res_path)) as conn:
            for date in self.trading_dates:
                #date_str = datetime.strftime(date, '%Y%m%d')
                date_str = date.replace('-', '')
                sql_cmd = "select * from \'{}\'".format(date_str)
                df = pd.read_sql(sql_cmd, con=conn)
                df.rename(columns={'order_book_id': 'code', 'date': 'datetime'}, inplace=True)
                xdf = df.set_index("code")  # 将指定列设置为index

                day_records = xdf.to_dict(orient='index')
                # print(list(day_records.items())[0])

        # parse data:
        for i in range(1, len(self.stk_data)):
            today_dic = self.stk_data[i]  # <class 'dict'>
            preday_dic = self.stk_data[i - 1]
            print('----------day%d---------' % (i))
            for code, bar in today_dic.items():
                if code in preday_dic:
                    bar['pre_close'] = preday_dic[code]['close']
                else:
                    # print('code:', code, len(today_dic), len(preday_dic))
                    bar['pre_close'] = 0
                    print(bar['datetime'])


    def load_bars_from_db2(self):
        # stks_df: pd.DataFrame = None
        day_list: List = []
        with sqlite3.connect("%s/daybars.db"%(res_path)) as conn:

            for date in self.trading_dates:
                #date_str = datetime.strftime(date, '%Y%m%d')
                date_str = date.replace('-', '')
                sql_cmd = "select * from \'{}\'".format(date_str)
                df = pd.read_sql(sql_cmd, con=conn)
                df.rename(columns={'order_book_id': 'code', 'date': 'datetime'}, inplace=True)
                df.set_index("code", inplace=True)  # 将指定列设置为index
                # print(df)
                # print(df.to_dict(orient='series'))
                # print(df.to_dict(orient='records'))
                dicdt = df.to_dict(orient='index')
                stks_dic:Dict = {}
                for k,v in dicdt.items():
                    stks_dic[k]=[v]
                print(len(stks_dic), list(stks_dic.values())[0])
                xdf = pd.DataFrame(data=stks_dic)
                # print(xdf)
                day_list.append(xdf)
            # stks_df = pd.DataFrame(data=day_list)
            print(day_list)


    def load_index_from_db(self):
        print(self.trading_dates)

        with sqlite3.connect("%s/idx_daybars.db"%(res_path)) as conn:
            for date in self.trading_dates:
                # print(date)
                date_str = date.replace('-', '')
                sql_cmd = "select * from \'{}\' where order_book_id=\'000300.XSHG\' or order_book_id=\'000905.XSHG\'".format(date_str)
                df = pd.read_sql(sql_cmd, con=conn)
                df.rename(columns={'order_book_id': 'code', 'date': 'datetime'}, inplace=True)
                sdf = df[['code', 'close']].set_index('code').T
                dt = sdf.to_dict(orient='list')
                xdf = pd.DataFrame(data=dt, index=[date])
                if self.idx_data is None:
                    self.idx_data = xdf         # xdf.index.name = "date"
                else:
                    self.idx_data = self.idx_data.append(xdf)
                    # self.idx_data = pd.concat([self.idx_data, xdf])
        print('--------------------------------------------------------------')
        print(self.idx_data)


loader = DataLoader()
loader.load_calendar_from_db()
loader.load_bars_from_db2()
# loader.load_index_from_db()