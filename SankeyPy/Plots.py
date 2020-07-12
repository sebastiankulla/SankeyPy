import plotly.graph_objects as go
import plotly.express as px


class BasePlot:
    def set_date_range(self, start_date, stop_date):
        self.start_date = start_date
        self.stop_date = stop_date


class SankeyPlot(BasePlot):
    def __init__(self, account, start_date=None, stop_date=None, focus=None, depth_level=None):
        self.account = account
        self.label = []
        self.source = []
        self.target = []
        self.value = []
        self.start_date = start_date
        self.stop_date = stop_date
        self.focus = focus
        self.depth_level = depth_level
        self._figure = None
        self.bool_avg_values = True

    def _create_grouped_df(self):
        if self.start_date is not None and self.stop_date is not None:
            period_df = self.account.revenue[(self.account.revenue.booking_date > self.start_date) & (
                    self.account.revenue.booking_date < self.stop_date)]
        else:
            period_df = self.account.revenue.copy()

        timeperiod_month = (period_df.booking_date.iloc[0] - period_df.booking_date.iloc[-1]).days / 30.436875
        sum_by_category = period_df[['category', 'turnover']].groupby('category').sum()

        if self.bool_avg_values:
            return sum_by_category / timeperiod_month
        else:
            return sum_by_category

    def _calc_edge_values(self, grouped_cash_flow):
        grouped_cash_flow.reset_index(inplace=True)
        grouped_cash_flow.loc[
            grouped_cash_flow.turnover >= 0, 'category'] = grouped_cash_flow.category + ':Budget'  # Append "Budget" depending on value positive/negative
        grouped_cash_flow.loc[grouped_cash_flow.turnover < 0, 'category'] = 'Budget:' + grouped_cash_flow.category

        for index, row in grouped_cash_flow.iterrows():  # Read all labels
            splitted_string = row.category.split(':')
            for string in splitted_string:
                if string not in self.label:
                    self.label.append(string)

        self.edge_value_dict = {}
        for index, row in grouped_cash_flow.iterrows():  # calculate the values for each edge
            splitted_string = row.category.split(':')
            for idx in range(len(splitted_string) - 1):
                if '{0}:{1}'.format(splitted_string[idx], splitted_string[idx + 1]) in self.edge_value_dict:
                    self.edge_value_dict[
                        '{0}:{1}'.format(splitted_string[idx], splitted_string[idx + 1])] += row.turnover
                else:
                    self.edge_value_dict[
                        '{0}:{1}'.format(splitted_string[idx], splitted_string[idx + 1])] = row.turnover

        for key, value in self.edge_value_dict.items():  #
            self.source.append(self.label.index(key.split(':')[0]))
            self.target.append(self.label.index(key.split(':')[1]))
            self.value.append(abs(value))

    @property
    def fig(self):
        grouped_cash_flow = self._create_grouped_df()
        self._calc_edge_values(grouped_cash_flow)

        figure = go.Figure(
            layout=dict(height=800),
            data=[go.Sankey(
                arrangement='perpendicular',
                valuesuffix='€',
                valueformat=".2f",
                node=dict(
                    pad=15,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=self.label,
                    color="blue"
                ),
                link=dict(
                    source=self.source,
                    target=self.target,
                    value=self.value
                ))])
        figure.update_layout(font_size=10, margin=dict(l=20, r=20, t=10, b=10))
        return figure

    def set_avg_values(self, bool_avg_value):
        self.bool_avg_values = bool_avg_value


class BarPlotMonthly(BasePlot):
    def __init__(self, account):
        self.account = account
        self.label = []
        self.source = []
        self.target = []
        self.value = []

        self._figure = None

    @property
    def fig(self):
        if self.start_date is not None and self.stop_date is not None:
            df = self.account.revenue[(self.account.revenue.booking_date > self.start_date) & (
                    self.account.revenue.booking_date < self.stop_date)]
        else:
            df = self.account.revenue.copy()

        df.loc[df.turnover >= 0, 'income'] = df.turnover
        df.loc[df.turnover < 0, 'expense'] = abs(df.turnover)
        df.set_index('booking_date', inplace=True)
        df = df.resample('MS').sum()

        figure = go.Figure(data=[
            go.Bar(name='Income', x=df.index, y=df.income),
            go.Bar(name='Expense', x=df.index, y=df.expense)])

        figure.update_layout(barmode='group', margin=dict(l=20, r=20, t=10, b=10))

        return figure


class BarPlotDaily(BasePlot):
    def __init__(self, account):
        self.account = account
        self.label = []
        self.source = []
        self.target = []
        self.value = []
        self._figure = None

    @property
    def fig(self):
        if self.start_date is not None and self.stop_date is not None:
            df = self.account.revenue[(self.account.revenue.booking_date > self.start_date) & (
                    self.account.revenue.booking_date < self.stop_date)]
        else:
            df = self.account.revenue.copy()

        df.loc[df.turnover < 0, 'expense'] = abs(df.turnover)
        df = df.groupby(df['booking_date'].dt.weekday).mean()
        df.rename(index={0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday'}, inplace=True)

        figure = go.Figure(data=[
            go.Bar(name='Expense', x=df.index, y=df.expense)])

        figure.update_layout(barmode='group', margin=dict(l=20, r=20, t=10, b=10))

        return figure
