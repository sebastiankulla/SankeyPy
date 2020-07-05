import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
from SankeyPy.Account import ComdirectAccount
from SankeyPy.Plots import SankeyPlot
import webbrowser
from threading import Timer

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    html.Label('Select your revenue export'),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'drag and drop or ',
            html.A('select files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    ),

    html.Div([
        html.Label('Name of the bank'),
        dcc.Dropdown(
            id='bank-dropdown',
            options=[
                {'label': 'Comdirect', 'value': 'CDT'},
                {'label': 'ING', 'value': 'ING'}
            ],
            value='CDT'
        ),
    ],
        style={'width': "40%", 'display': 'inline-block'}
    ),

    html.Div([
        html.Label('Type of Plot'),
        dcc.Dropdown(
            id='plottype-dropdown',
            options=[
                {'label': 'Sankey diagram', 'value': 'SKEY'}
            ],
            value='SKEY'
        )
    ],
        style={'width': "40%", 'display': 'inline-block'}
    ),

    dcc.Checklist(
        id='avg-checklist',
        options=[
            {'label': 'Show averaged values?', 'value': 'AVG'}
        ],
        value=['AVG']
    ),

    html.Div([
        html.Label('Period to be evaluated'),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=datetime.now() - timedelta(days=365),
            end_date=datetime.now(),
            display_format='DD.MM.YYYY'
        ),
        html.Button('Create Plot', id='button')
    ]),

    html.Div(id='insert_plot')

])


@app.callback(
    dash.dependencies.Output('upload-data', 'children'),
    [dash.dependencies.Input('upload-data', 'filename')])
def file_chosen(filename):
    if filename is not None:
        return html.A(filename)
    else:
        return html.Div(['drag and drop or ', html.A('select files')])


@app.callback(
    dash.dependencies.Output('insert_plot', 'children'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('bank-dropdown', 'value'),
     dash.dependencies.State('plottype-dropdown', 'value'),
     dash.dependencies.State('date-picker-range', 'start_date'),
     dash.dependencies.State('date-picker-range', 'end_date'),
     dash.dependencies.State('avg-checklist', 'value')])
def create_sankey_plot(n_clicks, filename, name_bank, name_plot, start_date, stop_date, method):
    if all([arg is not None for arg in [n_clicks, filename, name_bank, start_date, stop_date]]):
        if name_bank == 'CDT':
            my_account = ComdirectAccount()
        else:
            raise NotImplementedError(str(name_bank) + 'is not Implemented')

        my_account.load_revenue(filename)
        my_account.categorize('categories.json')  # Todo extend the dash interface so that the categories can be set in it

        if name_plot == 'SKEY':
            my_plot = SankeyPlot(my_account.get_grouped_cashflow_period(start_date, stop_date, method))
        else:
            raise NotImplementedError(str(name_plot) + 'is not Implemented')

        return dcc.Graph(figure=my_plot.fig)
    else:
        return ''


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')


def start_app(use_reloader=False):
    if not use_reloader:
        Timer(1, open_browser).start()
    app.run_server(debug=True, use_reloader=use_reloader)


if __name__ == '__main__':
    start_app()
