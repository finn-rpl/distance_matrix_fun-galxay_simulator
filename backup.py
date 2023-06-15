# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table as dt
from aberrant_technologies.interface import default
import time

theme = {
    "accent": "#FFD15F",
    "accent_negative": "#ff2c6d",
    "accent_positive": "#33ffe6",
    "background_content": "#2d3038",
    "background_page": "#23262E",
    "border": "#53555B",
    "border_style": {
        "name": "underlined",
        "borderTopWidth": 0,
        "borderRightWidth": 0,
        "borderLeftWidth": 0,
        "borderBottomWidth": "1px",
        "borderBottomStyle": "solid",
        "borderRadius": 0,
        "inputFocus": {
            "outline": "transparent"
        }
    },
    "breakpoint_font": "1200px",
    "breakpoint_stack_blocks": "700px",
    "colorway": [
        "#ffd15f",
        "#4c78a8",
        "#f58518",
        "#e45756",
        "#72b7b2",
        "#54a24b",
        "#b279a2",
        "#ff9da6",
        "#9d755d",
        "#bab0ac"
    ],
    "colorscale": [
        "#ffd15f",
        "#eabe54",
        "#d4ab48",
        "#c0983e",
        "#ab8633",
        "#977428",
        "#84631e",
        "#715214",
        "#5e420a",
        "#4c3200"
    ],
    "font_family": "Open Sans",
    "font_size": "17px",
    "font_size_smaller_screen": "15px",
    "font_family_header": "Quattrocento Sans",
    "font_size_header": "24px",
    "font_family_headings": "Quattrocento Sans",
    "text": "#95969A",
    "report_font_family": "Computer Modern",
    "report_font_size": "12px",
    "report_background_page": "white",
    "report_background_content": "#FAFBFC",
    "report_text": "black"
}

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
# app = dash.Dash(external_stylesheets=[theme])

parameters = {'centre': '12-121',
              'map_folder': '../nbody_nested/',
              'distance': 15,
              'load': 150,
              'biomes': (),
              'planets': 50,
              'opacity': 30,
              'search_mode': 'ball_point'
              }
presses = {'search_button': None,
           'select_button': None,
           'graph_click': None}


def sm3d(centre, map_folder, distance=15, load=150, biomes=(), planets=50, opacity=30, search_mode='ball_point'):
    import plotly.graph_objects as go
    from scipy.spatial import cKDTree
    import numpy as np
    import orjson
    print('test')

    ck = default.plotly_colours

    index = np.load(map_folder+'index.npy', allow_pickle=False)

    sd = {}

    for f in index[int(centre.split('-')[0])][:load]:
        with open(map_folder+str(f)+'.json', 'rb') as jfile:
            sd.update(orjson.loads(jfile.read()))

    tree = []
    index = {}
    n = 0
    for s in sd:
        if len(sd[s]['planets']) > planets:
            continue
        test = 0
        for i in range(len(biomes)):
            for p in sd[s]['planets']:
                if biomes[i] == p['biome']:
                    test += 1
                    break
            if test < i:
                break
        if test < len(biomes):
            continue

        tree.append(sd[s]['coords'])
        index[n] = s
        n += 1
    if search_mode == 'ball_point':
        tree = cKDTree(tree)
        star_index = [index[s] for s in tree.query_ball_point(sd[centre]['coords'], distance)]
    else:
        star_index = [centre]
        found = {centre}
        for i in range(distance):
            for s in set(found):
                for link in sd[s]['links']:
                    if link['location'] not in found:
                        star_index.append(link['location'])

    points = []
    point_colour = []
    links = []
    link_colour = []
    labels = []
    load_fails = {}
    id_names = []

    for s in star_index:

        label = s + '<br>' + sd[s]['planets'][0]['biome']
        id_names.append(s)
        for t in sd[s]['tags']:
            label += '<br>' + t
        labels.append(label)
        point_colour.append(ck[sd[s]['planets'][0]['biome']])
        points.extend(sd[s]['coords'])
        for link in sd[s]['links']:
            if link['location'] in sd:
                links.extend(sd[s]['coords'])
                links.extend(sd[link['location']]['coords'])
                links.extend([None, None, None])
                link_colour.append(ck[link['type']])
                link_colour.append(ck[link['type']])
                link_colour.append(ck[link['type']])
            else:
                chunk_fail = link['location'].split('-')[0]
                load_fails[chunk_fail] = load_fails[chunk_fail] + 1 if chunk_fail in load_fails else 1
    # print(', '.join([str(load_fails[i]) for i in load_fails if load_fails[i] > 0]))

    mk = go.Scatter3d(x=points[::3], y=points[1::3], z=points[2::3], mode='markers',
                      marker=dict(symbol='diamond', color=point_colour, size=5, opacity=opacity/100,
                                  ),
                      text=labels, hoverinfo='text', customdata=id_names)

    ln = go.Scatter3d(x=links[::3], y=links[1::3], z=links[2::3], mode='lines',
                      line=dict(color=link_colour, width=0.5), hoverinfo='none')

    axes = dict(title='', showgrid=False, zeroline=False, showline=False,
                showspikes=False, showticklabels=False, showbackground=False)
    layout = go.Layout(
        title='title',
        template='plotly_dark',
        showlegend=False,
        hovermode='closest',
        paper_bgcolor=ck['background'],
        margin=dict(b=0, l=0, r=0, t=0),
        scene=dict(
            xaxis=axes,
            yaxis=axes,
            zaxis=axes),
        )
    print(len(points))

    return go.Figure(data=[mk, ln], layout=layout), dash.no_update, parameters['centre']


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "25rem",
    "padding": "2rem 1rem",
    'color': default.plotly_colours['sea'],
    'backgroundColor': default.plotly_colours['background'],
    'border': default.plotly_colours['background'],
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "25rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}


content_graph = html.Div([
        dcc.Graph(
            id='example-graph',
            figure=sm3d(**parameters)[0],
            style={'height': '100vh'}),
        # ),
    ], style=CONTENT_STYLE)


ball_point = html.Div([
    html.Hr(),
    html.H6('biome filter'),
    dcc.Dropdown(
        id='biome--dropdown',
        options=[{'label': i, 'value': i} for i in default.biomes],
        value=(),
        multi=True,
        optionHeight=20,
        placeholder='biome',
        style={'backgroundColor': default.plotly_colours['background'],
               'border': default.plotly_colours['background'],
               'color': default.plotly_colours['sea'],
               'fontColor': default.plotly_colours['sea'],
               'display': 'inline-block',
               'width': '33vw'}),
    html.Hr(),
    html.H6('number of planets in system'),
    dcc.Slider(
        id='planet--slider',
        min=0,
        max=25,
        value=25,
        marks={i: str(i) for i in range(0, 26, 5)}),
    html.H6('search range - ball query'),
    dcc.Slider(
        id='range--slider',
        min=0,
        max=100,
        value=15,
        marks={i: str(i) for i in range(0, 101, 20)}),
    html.H6('chunks to load'),
    dcc.Slider(
        id='radius--slider',
        min=0,
        max=500,
        value=150,
        marks={i: str(i) for i in range(0, 501, 100)})],
    id='ball-point')

bacon = html.Div([
    # TODO toggle this with a baconator
    html.Hr(),
    html.H6('search range - degrees of separation'),
    dcc.Slider(
        id='degrees--slider',
        min=0,
        max=100,
        value=15,
        marks={i: str(i) for i in range(0, 101, 20)}),
    html.H6('chunks to load'),
    dcc.Slider(
        id='radius--slider--bacon',
        min=0,
        max=500,
        value=150,
        marks={i: str(i) for i in range(0, 501, 100)})
], id='bacon'
)

my_edit_kit = html.Div([
], id='my-edit-kit')


tabs = html.Div([dbc.Tabs([
    dbc.Tab(id='tab-1', label="global search", active_label_style={'color': 'primary'}),
    dbc.Tab(id='tab-2', label="Tab 2", active_label_style={'color': 'primary'}),
    dbc.Tab(id='tab-3', label="Tab 3", active_label_style={'color': 'primary'}),
    ],),

    html.H6('opacity slider'),
    dcc.Slider(
        id='opacity--slider',
        min=0,
        max=100,
        value=30,
        marks={i: str(i) for i in range(0, 101, 10)}),
    html.Hr(),

    dbc.InputGroup(
    [
        dbc.InputGroupAddon(
            dbc.Button("select seed", id="select-id",  color="primary"),
            addon_type="append",
        ),
        dbc.Input(id="select-id-data", value='', placeholder=parameters['centre'],
                  style={'backgroundColor': default.plotly_colours['background'],
                         'border': default.plotly_colours['background'],
                         'color': default.plotly_colours['sea']}),
    ]),
    html.Hr(),
    dbc.Button(id='submit-button-state', children="Map from seed: " + parameters['centre'], n_clicks=0, color="primary",
               block=True, type='reset')
],
    style=SIDEBAR_STYLE,
)


app.layout = html.Div([tabs, content_graph])


@app.callback(
    Output('example-graph', 'figure'),
    Output('data-table', 'data'),
    Output('select-id-data', 'value'),
    Input('example-graph', 'figure'),
    Input('example-graph', 'clickData'),
    Input('submit-button-state', 'n_clicks'),
    Input('biome--dropdown', 'value'),
    Input('planet--slider', 'value'),
    Input('range--slider', 'value'),
    Input('radius--slider', 'value'),
    Input('opacity--slider', 'value'),
    Input('select-id', 'n_clicks'),
    Input('select-id-data', 'value'),
    Input('degrees--slider', 'value'),
    Input('radius--slider--bacon', 'value'),
    # Input('my--tabs', 'active_tab')
)
def update_search(figure, clickData, button, biomes, planet_slider, range_slider, search_radius,
                  opacity_slider, select_button, select_id, degrees_slider, radius_slider_bacon,
                  search_mode='ball_point'):
    print(figure)
    print(clickData)
    parameters['biomes'] = biomes
    parameters['planets'] = planet_slider
    parameters['opacity'] = opacity_slider
    if search_mode != 'edit_toolbar':
        parameters['mode'] = search_mode
        if search_mode == 'bacon':
            parameters['load'] = radius_slider_bacon
            parameters['distance'] = degrees_slider
        else:
            parameters['load'] = search_radius
            parameters['distance'] = range_slider
    print(time.ctime())
    print(button)
    print(select_button)
    print(clickData)

    if button != presses['search_button']:
        presses['search_button'] = button
        # TODO: change button colour on click to show loading
        # TODO: draw ball point or draw bacons
        return sm3d(**parameters)
    elif select_button != presses['select_button']:
        presses['select_button'] = select_button
        parameters['centre'] = select_id
        # TODO: change button colour on click to show loading
        # TODO: draw ball point or draw bacons
        return sm3d(**parameters)
    elif clickData != presses['graph_click']:
        # TODO: Make a subpage of the sidebar with editable readout of the selected node
        # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/input_group/
        # what things do we want to edit?
        # names
        # temperatures - would update biomes presumably?
        # biomes - would update tags ontop
        # links - but this one might need a specific function as it needs to edit for others
        # tags -
        # custom notes
        print('click update data')
        # parameters['centre'] = clickData['points'][0]['customdata']
        return dash.no_update, dash.no_update, clickData['points'][0]['customdata']
    else:
        print('button other')
        print(button)
        if figure['data'][0]['marker']['opacity'] != opacity_slider / 100:
            figure['data'][0]['marker']['opacity'] = opacity_slider / 100
            return figure, dash.no_update, parameters['centre']
        return dash.no_update


# Not using anymore but might in future
# @app.callback(
#    Output(component_id='element-to-hide', component_property='style'),
#    [Input(component_id='hide-button', component_property='n_clicks')])
# def show_hide_element(clicks):
#     print('test')
#     if clicks % 2 == 1:
#         SIDEBAR_STYLE.update({'display': 'block'})
#         return SIDEBAR_STYLE
#     if clicks % 2 == 0:
#         SIDEBAR_STYLE.update({'display': 'none'})
#         return SIDEBAR_STYLE


if __name__ == '__main__':
    app.run_server(debug=True)
