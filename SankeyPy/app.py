import base64
import uuid
import webbrowser
from datetime import datetime, timedelta
from threading import Timer

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import State, Input, Output
from dash.exceptions import PreventUpdate
from flask_caching import Cache

from SankeyPy.Account import ComdirectAccount
from SankeyPy.Plots import SankeyPlot, BarPlotMonthly

app = dash.Dash(__name__)
cache = Cache(app.server, config={
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
})

app.sankeyplot = None


def serve_layout():
    session_id = str(uuid.uuid4())

    return html.Div([
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

        # dcc.Graph(id='bar-plot-daily', className='pretty_container six columns', config={
        #     'displayModeBar': False
        # }),
        dcc.Graph(id='custom-graph', className='pretty_container twelve columns', config={
            'displayModeBar': False
        }),
        html.Div(session_id, id='session-id', style={'display': 'none'})

    ])


app.layout = serve_layout()


@app.callback(
    Output('upload-data', 'children'),
    [Input('upload-data', 'filename')])
def file_chosen(filename):
    if filename is not None:
        return html.A(filename)
    else:
        return html.Div(['drag and drop or ', html.A('select files')])


def get_dataframe(session_id, content, name_bank):
    @cache.memoize()
    def load_and_serialize_data(session_id, content, name_bank):
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)

        if name_bank == 'CDT':
            my_account = ComdirectAccount()
        else:
            raise NotImplementedError(str(name_bank) + 'is not Implemented')

        my_account.load_revenue(decoded)
        my_account.categorize(
            'categories2.json')  # Todo extend the dash interface so that the categories can be set in it
        return my_account.revenue.to_json()

    return pd.read_json(load_and_serialize_data(session_id, content, name_bank),
                        convert_dates=['booking_date', 'value_date'])


@app.callback(
    Output('custom-graph', 'figure'),
    [Input('button', 'n_clicks')],
    [State('session-id', 'children'),
     State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('upload-data', 'contents'),
     State('bank-dropdown', 'value')])
def create_sankey_plot(n_clicks, session_id, start_date, stop_date, content, name_bank):
    if any(arg is None for arg in [n_clicks, session_id, start_date, stop_date, content, name_bank]):
        raise PreventUpdate

    dataframe = get_dataframe(session_id, content, name_bank)
    app.sankeyplot = SankeyPlot(dataframe)
    app.sankeyplot.set_date_range(start_date, stop_date)

    return app.sankeyplot.fig


@app.callback(
    Output('bar-plot-monthly', 'figure'),
    [Input('button', 'n_clicks'),
     Input('session-id', 'children')],
    [State('date-picker-range', 'start_date'),
     State('date-picker-range', 'end_date'),
     State('upload-data', 'contents'),
     State('bank-dropdown', 'value')])
def create_bar_plot(n_clicks, session_id, start_date, stop_date, content, name_bank):
    if any(arg is None for arg in [n_clicks, session_id, start_date, stop_date, content, name_bank]):
        raise PreventUpdate

    dataframe = get_dataframe(session_id, content, name_bank)
    app.barplot = BarPlotMonthly(dataframe)
    app.barplot.set_date_range(start_date, stop_date)

    return app.barplot.fig


# @app.callback(
#     Output('bar-plot-daily', 'figure'),
#     [Input('button', 'n_clicks'),
#      Input('session-id', 'children')],
#     [State('date-picker-range', 'start_date'),
#      State('date-picker-range', 'end_date'),
#      State('upload-data', 'contents'),
#      State('bank-dropdown', 'value')])
# def create_bar_plot_daily(n_clicks, session_id, start_date, stop_date, content, name_bank):
#     if any(arg is None for arg in [n_clicks, session_id, start_date, stop_date, content, name_bank]):
#         raise PreventUpdate
#
#     dataframe = get_dataframe(session_id, content, name_bank)
#     app.barplot = BarPlotDaily(dataframe)
#     app.barplot.set_date_range(start_date, stop_date)
#
#     return app.barplot.fig


def open_browser():
    webbrowser.open_new('http://127.0.0.1:8050/')


def start_app(use_reloader=False):
    if not use_reloader:
        Timer(1, open_browser).start()
    app.run_server(debug=True, use_reloader=use_reloader)


if __name__ == '__main__':
    start_app(True)
