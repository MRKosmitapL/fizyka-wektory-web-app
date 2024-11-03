import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

dash_app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app = dash_app.server

dash_app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Form([
                        dbc.Label('Ilość równań:'),
                        dbc.Input(id='rownania', type='number', value=1),
                    ]),
                    dbc.Form([
                        dbc.Label('Ostatnia wartość "t" do obliczenia:'),
                        dbc.Input(id='points-limit', type='number', value=10),
                    ]),
                    dbc.Form([
                        dbc.Label('Co ile ma obliczać:'),
                        dbc.Input(id='step', type='number', value=0.1,),
                    ],  style={"margin-bottom": "10px"}),
                    dbc.Form([
                        dbc.Label('Szybkość animacji (ms):'),
                        dbc.Input(id='interval', type='number', value=100),
                    ],  style={"margin-bottom": "10px"}),
                    html.Hr(style={'width': '100%', 'borderTop': '3px solid #000', 'margin-top': '10px '}),
                    dbc.Form([html.Div(id='czastki-inputs')]),
                    dbc.Row([
                        dbc.Col([
                            dbc.Button('Start', id='start-button', color='success', n_clicks=0, className='mt-3'),
                            dbc.Button('Stop', id='stop-button', color='danger', n_clicks=0, className='mt-3', style={'margin-left': '10px'}),
                            dbc.Button('Pokaż wszystkie punkty', id='show-all-button', color='primary', n_clicks=0, className='mt-3', style={'margin-left': '10px'}),
                        ], width={"size": 12}, style={"text-align": "center"})
                    ]),
                ])
            ], className='mb-4')
        ], width=4),
        dbc.Col([
            dcc.Graph(id='graph', style={'border': '1px solid #ddd', 'border-radius': '5px'}),
            dcc.Interval(id='interval-component', interval=100, n_intervals=0, disabled=True),
        ], width=8),
        dbc.Form([
            dbc.Label('Made by Jakub Pietras'),
        ], style={'margin-top': '20px', 'text-align': 'right'}),
    ])
], fluid=True, className='p-4')

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .dbc-card:hover {
                transform: scale(1.05);
            }
            @media (max-width: 768px) {
                .dbc-card {
                    margin-bottom: 20px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

@dash_app.callback(
    Output('czastki-inputs', 'children'),
     Input('rownania', 'value')
)
def update_czastki_inputs(rownania):
    return [
        dbc.Row([
            dbc.Label(f'Podaj wartość A dla czastki {i+1}:'),
            dbc.Input(id={'type': 'czastka-input', 'index': f'A-{i}'}, type='text', value='t'),
            dbc.Label(f'Podaj wartość B dla czastki {i+1}:'),
            dbc.Input(id={'type': 'czastka-input', 'index': f'B-{i}'}, type='text', value='t'),
            html.Hr(style={'width': '100%', 'borderTop': '3px solid #000', 'margin-top': '10px '})
        ], style={'margin_bottom':'10px','padding-left':'10px','padding-right':'10px'}) for i in range(rownania)
    ]

dash_app.clientside_callback(
    """
    function(start_n, stop_n, interval_value, disabled) {
        const ctx = window.dash_clientside.callback_context;
        if (!ctx.triggered.length) {
            return window.dash_clientside.no_update;
        }
        const button_id = ctx.triggered[0].prop_id.split('.')[0];
        if (button_id === 'start-button') {
            return [false, interval_value];
        } else if (button_id === 'stop-button') {
            return [true, interval_value];
        }
        return [disabled, interval_value];
    }
    """,
    [Output('interval-component', 'disabled'), Output('interval-component', 'interval')],
    [Input('start-button', 'n_clicks'), Input('stop-button', 'n_clicks')],
    [State('interval', 'value'), State('interval-component', 'disabled')]
)

dash_app.clientside_callback(
    """
    function(n_intervals, show_all_n_clicks, rownania, points_limit, step, czastki_values) {
        function calculate_points(A, B, points_limit, step) {
            const t_values = Array.from({length: Math.ceil(points_limit / step) + 1}, (_, i) => i * step);
            const x_values = t_values.map(t => eval(A));
            const y_values = t_values.map(t => eval(B));
            return t_values.map((t, i) => [t, x_values[i], y_values[i]]);
        }

        const czastki = [];
        for (let i = 0; i < rownania; i++) {
            const A = czastki_values[i * 2];
            const B = czastki_values[i * 2 + 1];
            czastki.push(calculate_points(A, B, points_limit, step));
        }

        const all_x_values = czastki.flat().map(point => point[1]);
        const all_y_values = czastki.flat().map(point => point[2]);
        const max_x = Math.max(...all_x_values);
        const min_x = Math.min(...all_x_values);
        const max_y = Math.max(...all_y_values);
        const min_y = Math.min(...all_y_values);

        const ctx = window.dash_clientside.callback_context;
        const button_id = ctx.triggered.length ? ctx.triggered[0].prop_id.split('.')[0] : 'No clicks yet';

        const fig = {
            data: [],
            layout: {
                xaxis: {range: [min_x, max_x], title: 'x[m]'},
                yaxis: {range: [min_y, max_y], title: 'y[m]'}
            }
        };

        if (button_id === 'show-all-button') {
            czastki.forEach((czastka, i) => {
                fig.data.push({
                    x: czastka.map(point => point[1]),
                    y: czastka.map(point => point[2]),
                    mode: 'markers',
                    name: `Czastka ${i + 1}`,
                    text: czastka.map(point => `t: ${point[0]}`),
                    hoverinfo: 'text+x+y'
                });
            });
        } else {
            const t_steps = Math.ceil(points_limit / step);
            const current_index = n_intervals % (t_steps + 1);
            czastki.forEach((czastka, i) => {
                if (current_index < czastka.length) {
                    const [t, x, y] = czastka[current_index];
                    fig.data.push({
                        x: [x],
                        y: [y],
                        mode: 'markers',
                        name: `Czastka ${i + 1}`,
                        text: [`t: ${t}`],
                        hoverinfo: 'text+x+y'
                    });
                }
            });
        }

        return fig;
    }
    """,
    Output('graph', 'figure'),
    [Input('interval-component', 'n_intervals'), Input('show-all-button', 'n_clicks')],
    [State('rownania', 'value'), State('points-limit', 'value'), State('step', 'value'), State({'type': 'czastka-input', 'index': dash.ALL}, 'value')]
)

if __name__ == '__main__':
    dash_app.run_server()
