import io
import json
from datetime import datetime

import numpy as np
import pandas as pd


class Account:  # Todo make it possible to merge multiple accounts (checking account, credit card, Paypal) for better categorization
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
            for keyword_dict in keyword_list:
                for key, value in keyword_dict.items():
                    self.revenue.loc[
                        self.revenue[key].str.lower().str.contains(value.lower()), 'category'] = category

    def get_grouped_cashflow_period(self, start_date, stop_date, avg_values=True):
        period_df = self.revenue[(self.revenue.booking_date > start_date) & (self.revenue.booking_date < stop_date)]
        timeperiod_month = (period_df.booking_date.iloc[0] - period_df.booking_date.iloc[-1]).days / 30.436875
        sum_by_category = period_df[['category', 'turnover']].groupby('category').sum()
        if avg_values:
            return sum_by_category / timeperiod_month
        else:
            return sum_by_category


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
        revenue_file = revenue_file.decode('cp1252')
        self.revenue = pd.read_csv(io.StringIO(revenue_file), **kwargs)
        self.revenue['client'] = [result[0] if len(result) > 0 else "" for result in self.revenue['booking_text'].str.findall('(?<=Auftraggeber: ).+(?= Buchungstext:)')]
        self.revenue['ref_number'] = [result[0] if len(result) > 0 else "" for result in
                                  self.revenue['booking_text'].str.findall('(?<=Ref. ).+')]
        self.revenue['recipient'] = [result[0] if len(result) > 0 else "" for result in self.revenue['booking_text'].str.findall('(?<=Empfänger: ).+(?=Kto\/IBAN:)')]
        self.revenue['iban'] = [result[0] if len(result) > 0 else "" for result in self.revenue['booking_text'].str.findall('(?<=Kto\/IBAN: ).+(?= BLZ\/BIC:)')]
        self.revenue['bic'] = [result[0] if len(result) > 0 else "" for result in
                                self.revenue['booking_text'].str.findall('(?<=BLZ\/BIC: ).+(?=  Buchungstext:)')]
        self.revenue['booking_text'] = [result[0] if len(result) > 0 else "" for result in
                                        self.revenue['booking_text'].str.findall('(?<=Buchungstext: ).+(?= Ref.)')]
        self.revenue.to_excel("test.xlsx")


class INGAccount(Account): #  Todo add load_revenue method for INGAccount
    def __init__(self):
        super(INGAccount, self).__init__()

    def load_revenue(self, revenue_file):
        raise NotImplementedError