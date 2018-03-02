# -*- coding: utf-8 -*-
import dash
import flask
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import plotly.graph_objs as go
from scipy.io import wavfile
import numpy as np

import base64
import io

#==================================
#   constant
#==================================
AMPLITUDE = 2**15
INIT_SPEC_BOUNDS = [18*10**3-AMPLITUDE, 48*10**3-AMPLITUDE]
INIT_TIME_BOUNDS = [0, 2]

INIT_SMR, INIT_DATA = wavfile.read('input/wave400.wav')

#==================================
#   server
#==================================
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)

#==================================
#   style config
#==================================
colors = {
    'paper_bg': '#ffffff',
    'plot_bg': '#ffffff'
}

style_config_dict = {
    'general': {
        'text': {},
        'object': {
            'width': '100%',
            'height': '100%',
            'backgroundColor': '#ffffff'
        }
    },
    'header': {
        'text': {
            'textAlign': 'center',
            'color': '#009999'
        },
        'object': {
            'display': 'inline-block',
            'width': '100%',
            'height': '10%'
        }
    },

    'work-panel': {
        'upload-file': {
            'text': {
                'textAlign': 'center',
                'lineHeight': '1.0'
            },
            'object': {
                'display': 'inline-block',
                'width': '90%',
                'height': '10%',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'borderColor': 'black',
                'margin': '2%',
                'backgroundColor': '#ccccff'
            }
        },
        'rangeslider-fild': {
            'object': {
                'display': 'inline-block',
                'width': '90%',
                'height': '40%',
                'minHeight': '250px',
                'margin': '2%',
                'backgroundColor': '#ffffff'
            },
            'text': {}
        },
        'rangeslider-time-wrap': {
            'object': {
                'display': 'inline-block',
                'width': '100%',
                'height': '350px',
            },
            'text': {}
        },
        'radioitem-fild': {
            'object': {
                'display': 'inline-block',
                'width': '90%',
                'height': '25%',
                'minHeight': '150px',
                'margin': '2%',
                'backgroundColor': '#ffffff'
            },
            'text': {
                'display': 'inline-block'
            }
        },
        'tl-time-wrap': {
            'object':{
                'display': 'inline-block',
                'width': '90%',
                'height': '25%',
                'minHeight': '150px',
                'margin': '2%',
                'backgroundColor': '#ffffff'
            },
            'text': {}
        },
        'tl-param': {
            'object':{
                'display': 'inline-block',
                'width': '48%',
                'height': '140px',
            },
            'text': {}
        },
        'tg-time-wrap': {
            'object':{
                'display': 'inline-block',
                'width': '90%',
                'height': '25%',
                'minHeight': '150px',
                'margin': '2%',
                'backgroundColor': '#ffffff'
            },
            'text': {}
        },
        'tg-param': {
            'object':{
                'display': 'inline-block',
                'width': '48%',
                'height': '140px',
            },
            'text': {}
        },
        'text': {},
        'object': {
            'display': 'inline-block',
            'width': '22%',
            'height': '80%',
            'minHeight': '950px',
            'float': 'left',
            'backgroundColor': '#ffffff'
        }
    },

    'graphic-fild': {
        'spectr-fild': {
            'text': {},
            'object': {
                'display': 'inline-block',
                'width': '95%',
                'margin': '2%'
            }
        },
        'time-fild': {
            'text': {},
            'object': {
                'display': 'inline-block',
                'width': '95%',
                'margin': '2%'
            }
        },
        'line1': {
            'color': '#9999ff'
        },
        'line2': {
            'color': '#99ff99'
        },
        'line3': {
            'color': '#ff9999'
        },
        'text': {},
        'object': {
            'display': 'inline-block',
            'width': '78%',
            'height': '80%',
            'minHeight': '950px',
            'float': 'right',
            'backgroundColor': '#ffffff'
        }
    },

    'footer': {
        'author': {
            'text': {
                'textAlign': 'center',
                'color': '#009999'
            },
            'object': {
                'height': '100%',
                'width': '10%',
                'float': 'right'
            }
        },
        'text': {},
        'object': {
            'display': 'inline-block',
            'bottom': '0',
            'width': '100%',
            'height': '10%',
            'backgroundColor': '#ffffff'
        }
    }
}

#=================================
#   util.func.
#=================================
def avg_filter(arr, L, G=0):
    length = len(arr)
    filt_arr = [a for a in arr]
    for i in range(length-L-G):
        for j in range(L-1):
            filt_arr[i] += arr[i+G+j+1]
        filt_arr[i] /= L
    for i in range(length-L-G, L+G):
        filt_arr[i] = 0
    return np.array(filt_arr)

def trap_filter(arr, L, G=10):
    arr_avg1 = avg_filter(arr, L, G=0)
    arr_avg2 = avg_filter(arr, L, G=G)
    return  arr_avg2-arr_avg1

def time2spectr(data):
    lim = 65536
    spec = [0 for i in range(lim)]
    for a in data:
        a += 32768
        if a < lim:
            spec[int(a)] += 1
    return spec

def get_spectr_graphic(arr, smr, title='', name='', bound=None):
    spec_lim = INIT_SPEC_BOUNDS
    if bound is not None:
        time_lim = bound
    else:
        time_lim = [0, len(arr)]
    return dcc.Graph(
                id='spectr-graphic',
                figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=[i-int(AMPLITUDE) for i in range(2*AMPLITUDE)],
                                    y=time2spectr(arr[int(time_lim[0]): int(time_lim[1])]),
                                    line=style_config_dict['graphic-fild']['line1'],
                                    opacity=0.8,
                                    name=name
                                )
                            ],
                            layout=go.Layout(
                                title='Spectr '+str(title),
                                paper_bgcolor=colors['paper_bg'],
                                plot_bgcolor=colors['plot_bg'],
                                xaxis=dict(
                                    rangeslider={},
                                    range=spec_lim
                                )
                            )
                        )
                    )


def get_time_graphic(arr, smr, L, G, title='', name='', bound=None):
    if bound is None:
        lim = INIT_TIME_BOUNDS
    else:
        lim = bound
    if lim[1]>len(arr)/smr:
        lim[1]=len(arr)/smr

    elif lim[0]>len(arr)/smr:
        lim[0]=len(arr)/smr
    print('get time graphic')
    return dcc.Graph(
                id='time-graphic',
                figure=go.Figure(
                            data=[
                                go.Scatter(
                                    x=[(smr*lim[0]+i)/smr for i in range(int(smr*(lim[1]-lim[0])))],
                                    y=arr[int(smr*lim[0]):int(smr*lim[1])],
                                    line=style_config_dict['graphic-fild']['line1'],
                                    opacity=0.8,
                                    name = 'obt. data'
                                ),
                                go.Scatter(
                                    x=[(smr*lim[0]+i)/smr for i in range(int(smr*(lim[1]-lim[0])))],
                                    y=avg_filter(arr[int(smr*lim[0]):int(smr*lim[1])], L=L),
                                    line=style_config_dict['graphic-fild']['line2'],
                                    opacity=0.8,
                                    name = 'avg. filter'
                                ),
                                go.Scatter(
                                    x=[(smr*lim[0]+i)/smr for i in range(int(smr*(lim[1]-lim[0])))],
                                    y=trap_filter(arr[int(smr*lim[0]):int(smr*lim[1])], L=L, G=G),
                                    line=style_config_dict['graphic-fild']['line3'],
                                    opacity=0.8,
                                    name = 'trap. filter'
                                )
                            ],
                            layout=go.Layout(
                                title='Time Series '+str(title),
                                paper_bgcolor=colors['paper_bg'],
                                plot_bgcolor=colors['plot_bg'],
                                xaxis=dict(
                                    rangeslider={},
                                    range=[lim[0], lim[1]]
                                )
                            )
                        )
                    )

#=================================
#   Canva
#=================================
app.layout = html.Div(
    id='general',
    children=[
        html.Div(
            id='header',
            children=[
                html.H1(
                    id='header-text',
                    children='Visualization Time Series',
                    style=style_config_dict['header']['text']
                )
            ],
            style=style_config_dict['header']['object']
        ),
        # upload elemet &
        # elements for work
        html.Div(
            id='work-panel',
            children=[
                dcc.Upload(
                    id='upload-file',
                    children=[
                        html.Div([
                            'Drag and Drop or',
                            html.A('Select one *.wave or *.txt file')
                            ],
                            style=style_config_dict['work-panel']['upload-file']['text']
                        )
                    ],
                    style=style_config_dict['work-panel']['upload-file']['object'],
                    multiple=False
                ),
                html.Div(
                    id='rangeslider-fild',
                    children=[
                        html.H5(
                            id='rangeslider-header',
                            children='Vis. TS region'
                        ),
                        html.Div(
                            id='rangeslider-time-wrap',
                            children=[
                                dcc.RangeSlider(
                                    id='rangeslider-time',
                                    marks={
                                        i:'{}s'.format(i) for i in range(0, int(len(INIT_DATA)/float(INIT_SMR)), 5)
                                    },
                                    value=INIT_TIME_BOUNDS,
                                    min=0,
                                    max=int(len(INIT_DATA)/float(INIT_SMR)),
                                    dots=True,
                                    step=0.1,
                                    vertical=True
                                )
                            ],
                            style=style_config_dict['work-panel']['rangeslider-time-wrap']['object']
                        )
                    ],
                    style=style_config_dict['work-panel']['rangeslider-fild']['object']
                ),
                html.Div(
                    id='radioitem-fild',
                    children=[
                        html.H5(
                            id='radioitem-header',
                            children='Part time series for calc. spectr',
                            style=style_config_dict['work-panel']['radioitem-fild']['text']
                        ),
                        dcc.RadioItems(
                            id='radioitem-spec',
                            options=[
                                {'label': '100%', 'value': 1.},
                                {'label': '75%', 'value': 0.75},
                                {'label': '50%', 'value': 0.5},
                                {'label': '25%', 'value': 0.25},
                                {'label': '12%', 'value': 0.12},
                                {'label': '6%', 'value': 0.06},
                                {'label': '3%', 'value': 0.03},
                                {'label': 'use TS region', 'value': None},
                            ],
                            value=0.06,
                            labelStyle={'display': 'inline-block'}
                        )
                    ],
                    style=style_config_dict['work-panel']['radioitem-fild']['object']
                ),
                html.Div(
                    id='filter-param',
                    children=[
                        html.Div(
                            id='tl-param',
                            children=[
                                html.H5(
                                    id='tl-param-header',
                                    children='Tl, num.points'
                                ),
                                html.Div(
                                    id='tl-time-wrap',
                                    children=[
                                        dcc.RangeSlider(
                                            id='tl-time',
                                            marks={
                                                i*10:'{}s'.format(i*10) for i in range(0, 10, 1)
                                            },
                                            value=[0, 10],
                                            min=0,
                                            max=100,
                                            dots=True,
                                            step=1,
                                            vertical=True
                                        )
                                    ],
                                    style=style_config_dict['work-panel']['tl-time-wrap']['object']
                                )
                            ],
                            style=style_config_dict['work-panel']['tl-param']['object']
                        ),
                        html.Div(
                            id='tg-param',
                            children=[
                                html.H5(
                                    id='tg-param-header',
                                    children='Tg, num.points'
                                ),
                                html.Div(
                                    id='tg-time-wrap',
                                    children=[
                                        dcc.RangeSlider(
                                            id='tg-time',
                                            marks={
                                                i*10:'{}s'.format(i*10) for i in range(0, 10, 1)
                                            },
                                            value=[0, 10],
                                            min=0,
                                            max=100,
                                            dots=True,
                                            step=1,
                                            vertical=True
                                        )
                                    ],
                                    style=style_config_dict['work-panel']['tg-time-wrap']['object']
                                )
                            ],
                            style=style_config_dict['work-panel']['tg-param']['object']
                        )
                    ]
                )
            ],
            style=style_config_dict['work-panel']['object']
        ),
        # graph
        html.Div(
            id='graphic-fild',
            children=[
                html.Div(
                    id='spectr-fild',
                    style=style_config_dict['graphic-fild']['spectr-fild']['object']
                ),
                html.Div(
                    id='time-fild',
                    style=style_config_dict['graphic-fild']['time-fild']['object']
                )
            ],
            style=style_config_dict['graphic-fild']['object']
        ),
        # footer
        html.Div(
            id='footer',
            children=[
                html.Div(
                    id='author',
                    children=[
                        html.P(
                            'Miklgr500',
                            style=style_config_dict['footer']['author']['text']
                        )
                    ],
                    style=style_config_dict['footer']['author']['object']
                )
            ],
            style=style_config_dict['footer']['object']
        )

    ],
    style=style_config_dict['general']['object']
)

#=================================
#   reaction
#=================================
def parse_content_type(s):
    s = s.split(';')[-2].split('-')[-1]
    return s


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    content_format = parse_content_type(content_type)
    decoded = base64.b64decode(content_string)
    try:
        if content_format == 'wav':
            samplerate, data = wavfile.read(
                                io.BytesIO(decoded)
                               )
        elif content_format != 'wav':
            data = np.loadtxt(io.BytesIO(decoded))
            samplerate = 10**8
    except Exception as e:
        print(e)
        return None
    name = '' if filename is None else str(filename)
    return samplerate, data, name


@app.callback(Output('spectr-fild', 'children'),
              [Input('upload-file', 'contents'),
               Input('upload-file', 'filename'),
               Input('rangeslider-time', 'value'),
               Input('radioitem-spec', 'value')])
def update_spec_graphic(list_of_contents, list_of_names, time_value, spec_value):
    if list_of_contents is not None:
        samplerate, data, title = parse_contents(list_of_contents, list_of_names)
    else:
        samplerate, data, title = INIT_SMR, INIT_DATA, 'init.'

    if spec_value is None:
        value = [int(time_value[0]*samplerate), int(time_value[1]*samplerate)]
    else:
        value = [0, int(len(data)*spec_value)]

    children = [
        get_spectr_graphic(data, samplerate, name='obt. data', title=title, bound=value)
    ]
    return children


@app.callback(Output('time-fild', 'children'),
              [Input('upload-file', 'contents'),
               Input('upload-file', 'filename'),
               Input('rangeslider-time', 'value'),
               Input('tl-time', 'value'),
               Input('tg-time', 'value')])
def update_time_graphic(list_of_contents, list_of_names, time_value, tl, tg):
    if list_of_contents is not None:
        samplerate, data, title = parse_contents(list_of_contents, list_of_names)
    else:
        samplerate, data, title = INIT_SMR, INIT_DATA, 'init.'
    l = tl[1]
    g = tg[1]
    children = [
            get_time_graphic(data, samplerate,L=l, G=g, title=title, bound=time_value)
        ]
    return children


if __name__ == '__main__':
    app.server.run(debug=True)
