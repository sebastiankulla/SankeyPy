import pandas as pd
import numpy as np
import json
from datetime import datetime


class Account:
    def __init__(self):
        self.old_account_balance = 0
        self.new_account_balance = 0
        self.revenue = None

    def load_revenue(self, revenue_file):
        raise NotImplementedError

    def categorize(self, category_json_file):
        with open(category_json_file, 'r') as json_file:
            categories = json.load(json_file)
        self.revenue.loc[self.revenue.turnover > 0, 'category'] = 'Other Income'
        self.revenue.loc[self.revenue.turnover < 0, 'category'] = 'Other Expenses'

        for category, keyword_list in categories.items():
            for keyword in keyword_list:
                self.revenue.loc[
                    self.revenue['booking_text'].str.lower().str.contains(keyword.lower()), 'category'] = category

    @property
    def grouped_cash_flow(self):
        return self.revenue[['category', 'turnover']].groupby('category').sum()

    @property
    def grouped_cash_flow_month(self):
        return self.grouped_cash_flow / self.timeperiod_month

    @property
    def timeperiod_days(self):
        return (self.revenue.booking_date.iloc[0] - self.revenue.booking_date.iloc[-1]).days

    @property
    def timeperiod_month(self):
        return self.timeperiod_days / 30.436875


class ComdirectAccount(Account):
    def __init__(self):
        super(ComdirectAccount, self).__init__()

    def _convert_dates(self, date_string):
        return datetime.strptime(date_string, r'%d.%m.%Y')

    def _convert_turnover(self, string):
        return np.float(string.replace('.', '').replace(',', '.'))

    def load_revenue(self, revenue_file):
        usecols = [0, 1, 2, 3, 4]
        names = ['booking_date', 'value_date', 'procedure', 'booking_text', 'turnover']
        converters = {'booking_date': self._convert_dates, 'value_date': self._convert_dates,
                      'turnover': self._convert_turnover}
        kwargs = {'skiprows': 4, 'skipfooter': 2, 'sep': ';', 'encoding': 'cp1252', 'header': 0, 'usecols': usecols,
                  'names': names, 'engine': 'python', 'converters': converters}
        self.revenue = pd.read_csv(revenue_file, **kwargs)


