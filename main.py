from Account import ComdirectAccount
from Plots import SankeyPlot


if __name__ == '__main__':
    first_account = ComdirectAccount()
    first_account.load_revenue('comdirect_turnover_export.csv')
    first_account.categorize('categories.json')
    test = first_account.grouped_cash_flow_month
    first_plot = SankeyPlot(first_account.grouped_cash_flow_month)
    first_plot.plot()