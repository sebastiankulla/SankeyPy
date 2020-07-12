import dash
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
from SankeyPy.Account import ComdirectAccount
from SankeyPy.Plots import SankeyPlot, BarPlotMonthly, BarPlotDaily
import webbrowser
from threading import Timer
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__)
app.sankeyplot = None

app.layout = html.Div([

    html.Div([
        html.Div([
            html.Label('Select your revenue export'),
            dcc.Upload(
                id='upload-data',
                children=html.Div([
                    'drag and drop or ',
                    html.A('select files')
                ]),
                style={
                    'height': '60px',
                    'lineHeight': '60px',
                    'borderWidth': '1px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px'
                },
                className="dcc_control"),

            html.Label('Name of the bank'),
            dcc.Dropdown(
                id='bank-dropdown',
                options=[
                    {'label': 'Comdirect', 'value': 'CDT'},
                    {'label': 'ING', 'value': 'ING'}
                ],
                value='CDT',
                className="dcc_control"

            ),

            html.Label('Period to be evaluated'),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=datetime.now() - timedelta(days=365),
                end_date=datetime.now(),
                display_format='DD.MM.YYYY',
                className="dcc_control"),
            html.Button('Create Plot', id='button')

        ], className="pretty_container four columns"
        ),
        dcc.Graph(id='bar-plot-monthly', className='pretty_container eight columns', config={
            'displayModeBar': False
        })
    ], className='row flex-display'
    ),

    dcc.Graph(id='bar-plot-daily', className='pretty_container six columns', config={
        'displayModeBar': False
    }),
    dcc.Graph(id='custom-graph', className='pretty_container twelve columns', config={
        'displayModeBar': False
    })

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
    dash.dependencies.Output('custom-graph', 'figure'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('bank-dropdown', 'value'),
     dash.dependencies.State('date-picker-range', 'start_date'),
     dash.dependencies.State('date-picker-range', 'end_date')])
def create_sankey_plot(n_clicks, filename, name_bank, start_date, stop_date):
    if any([arg is None for arg in [n_clicks, filename, name_bank, start_date, stop_date]]):
        raise PreventUpdate

    if name_bank == 'CDT':
        my_account = ComdirectAccount()
    else:
        raise NotImplementedError(str(name_bank) + 'is not Implemented')

    my_account.load_revenue(filename)
    my_account.categorize('categories2.json')  # Todo extend the dash interface so that the categories can be set in it

    app.sankeyplot = SankeyPlot(my_account)
    app.sankeyplot.set_date_range(start_date, stop_date)

    return app.sankeyplot.fig


@app.callback(
    dash.dependencies.Output('bar-plot-monthly', 'figure'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('bank-dropdown', 'value'),
     dash.dependencies.State('date-picker-range', 'start_date'),
     dash.dependencies.State('date-picker-range', 'end_date')])
def create_bar_plot(n_clicks, filename, name_bank, start_date, stop_date):
    if any([arg is None for arg in [n_clicks, filename, name_bank, start_date, stop_date]]):
        raise PreventUpdate

    if name_bank == 'CDT':
        my_account = ComdirectAccount()
    else:
        raise NotImplementedError(str(name_bank) + 'is not Implemented')

    my_account.load_revenue(filename)
    my_account.categorize('categories2.json')  # Todo extend the dash interface so that the categories can be set in it

    app.barplot = BarPlotMonthly(my_account)
    app.barplot.set_date_range(start_date, stop_date)

    return app.barplot.fig


@app.callback(
    dash.dependencies.Output('bar-plot-daily', 'figure'),
    [dash.dependencies.Input('button', 'n_clicks')],
    [dash.dependencies.State('upload-data', 'filename'),
     dash.dependencies.State('bank-dropdown', 'value'),
     dash.dependencies.State('date-picker-range', 'start_date'),
     dash.dependencies.State('date-picker-range', 'end_date')])
def create_bar_plot_daily(n_clicks, filename, name_bank, start_date, stop_date):
    if any([arg is None for arg in [n_clicks, filename, name_bank, start_date, stop_date]]):
        raise PreventUpdate

    if name_bank == 'CDT':
        my_account = ComdirectAccount()
    else:
        raise NotImplementedError(str(name_bank) + 'is not Implemented')

    my_account.load_revenue(filename)
    my_account.categorize('categories2.json')  # Todo extend the dash interface so that the categories can be set in it

    app.barplot = BarPlotDaily(my_account)
    app.barplot.set_date_range(start_date, stop_date)

    return app.barplot.fig


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')


def start_app(use_reloader=False):
    if not use_reloader:
        Timer(1, open_browser).start()
    app.run_server(debug=True, use_reloader=use_reloader)


if __name__ == '__main__':
    start_app(True)
