import plotly.graph_objects as go


class SankeyPlot:
    def __init__(self, grouped_cash_flow):
        self.label = []
        self.source = []
        self.target = []
        self.value = []


        grouped_cash_flow.reset_index(inplace=True)
        grouped_cash_flow.loc[grouped_cash_flow.turnover >= 0, 'category'] = grouped_cash_flow.category + ':Budget'
        grouped_cash_flow.loc[grouped_cash_flow.turnover < 0, 'category'] = 'Budget:' + grouped_cash_flow.category

        for index, row in grouped_cash_flow.iterrows():
            splitted_string = row.category.split(':')
            for string in splitted_string:
                if string not in self.label:
                    self.label.append(string)

        self.edge_value_dict = {}
        for index, row in grouped_cash_flow.iterrows():
            splitted_string = row.category.split(':')
            for idx in range(len(splitted_string) - 1):

                if '{0}:{1}'.format(splitted_string[idx], splitted_string[idx + 1]) in self.edge_value_dict:
                    self.edge_value_dict[
                        '{0}:{1}'.format(splitted_string[idx], splitted_string[idx + 1])] += row.turnover
                else:
                    self.edge_value_dict[
                        '{0}:{1}'.format(splitted_string[idx], splitted_string[idx + 1])] = row.turnover

        for key, value in self.edge_value_dict.items():
            self.source.append(self.label.index(key.split(':')[0]))
            self.target.append(self.label.index(key.split(':')[1]))
            self.value.append(abs(value))

    @property
    def fig(self):
        fig = go.Figure(
            layout = dict(height=1000
                          ),
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
        fig.update_layout(title_text="Basic Sankey Diagram", font_size=10)
        return fig
