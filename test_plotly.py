import dash
from dash.dependencies import Output, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import random
import plotly.graph_objs as go
from collections import deque
import webbrowser
from threading import Event
import math

X, Y, Z = deque(maxlen=50), deque(maxlen=50), deque(maxlen=50)
X.append(0)
Y.append(0)
Z.append(0)

app = dash.Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id='live-graph', animate=True,
            figure=dict(
                data=[go.Scatter3d(x=list(X), y=list(Y), z=list(Z), mode='markers')],
                layout=dict(
                    scene = dict(
                        xaxis=dict(range=[-1, 1]),
                        yaxis=dict(range=[-1, 1]),
                        zaxis=dict(range=[0, 5]),
                        )
                    )
                )
            ),
        html.Button("Next", id='button')
    ]
)

@app.callback(Output('live-graph', 'figure'),
              [Input('button', 'n_clicks')])
def update_graph_scatter(n):

    Z.append(Z[-1]+0.1)
    X.append(math.cos(Z[-1]))
    Y.append(math.sin(Z[-1]))

    data = go.Scatter3d(x=list(X), y=list(Y), z=list(Z), mode='markers')


    # X.append(X[-1]+1)
    # Y.append(Y[-1]+Y[-1]*random.uniform(-0.1,0.1))

    # data = plotly.graph_objs.Scatter(
    #         x=list(X),
    #         y=list(Y),
    #         name='Scatter',
    #         mode= 'lines+markers'
    #         )
    #
    return {'data': [data]}


def open_browser():
	webbrowser.open_new("http://localhost:{}".format(8050))

if __name__ == '__main__':

    app.run_server(debug=True)
    print("bla")
