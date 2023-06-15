# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_html_components as html
from aberrant_technologies.interface import default
import time
print(time.ctime())

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
              'map_folder': '../nbody_nested_test/',
              'distance': 5,
              'load': 30,
              'biomes': (),
              'planets': [0, 50],
              'opacity': 30,
              'search_mode': 'ball_point',
              'path_id': 'None',
              'save': False,
              }
presses = {'search_button': 0,
           'select_button': None,
           'graph_click': None,
           'path_button': None}

max_planets = 50


def find_predecessors(array, past):
    array = array.tolist()
    while past != -9999:
        next = array[past]
        array[past] = 'path'
        past = next
    return array


def sm3d(centre, map_folder, distance=15, load=150, biomes=(), planets=(0, 50), opacity=30, search_mode='ball_point',
         path_id='None', save=False):
    import plotly.graph_objects as go
    from scipy.spatial import cKDTree
    from scipy.sparse import dok_matrix
    from scipy.sparse.csgraph import shortest_path
    import numpy as np
    import orjson

    ck = default.plotly_colours
    sd = {}
    index = np.load(map_folder + 'index.npy', allow_pickle=False)

    if path_id != 'None':
        cc = int(centre.split('-')[0])
        pc = int(path_id.split('-')[0])
        if cc != pc:
            dm = np.load(map_folder + 'dist_matrix.npy', allow_pickle=False)
            pre = shortest_path(dok_matrix(dm), directed=False, return_predecessors=True)[1]
            pth = find_predecessors(pre[cc], pc)
            for j in [i for i in range(len(pth)) if pth[i] == 'path']:
                for k in index[j][:7]:
                    with open(map_folder + str(k) + '.json', 'rb') as jfile:
                        sd.update(orjson.loads(jfile.read()))
        else:
            for i in index[cc][:7]:
                with open(map_folder + str(i) + '.json', 'rb') as jfile:
                    sd.update(orjson.loads(jfile.read()))
        print(len(sd))
        sd_list = list(sd.keys())
        dm = dok_matrix((len(sd), len(sd)))
        for star in range(len(sd)):
            for connection in sd[sd_list[star]]['links']:
                if connection['location'] not in sd:
                    continue
                dm[star, sd_list.index(connection['location'])] = connection['dist']

        path_len, pre = shortest_path(dm, directed=False, return_predecessors=True)
        pth = find_predecessors(pre[sd_list.index(centre)], sd_list.index(path_id))
        star_index = [sd_list[i] for i in range(len(pth)) if pth[i] == 'path']
    else:

        for f in index[int(centre.split('-')[0])][:int(load)]:
            with open(map_folder + str(f) + '.json', 'rb') as jfile:
                sd.update(orjson.loads(jfile.read()))

        tree = []
        index = {}
        n = 0
        for s in sd:
            if planets[0] > len(sd[s]['planets']) or len(sd[s]['planets']) > planets[1]:
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
            print(s)
            print(test)
            tree.append(sd[s]['extraplanar_coords'])
            index[n] = s
            n += 1
        if search_mode == 'ball_point':
            tree = cKDTree(tree)
            star_index = [index[s] for s in tree.query_ball_point(sd[centre]['extraplanar_coords'], distance)]
        else:
            star_index = {centre}
            for i in range(int(distance)):
                for s in set(star_index):
                    for link in sd[s]['links']:
                        if link['location'] not in star_index:
                            star_index.update({link['location']})

    points = []
    point_colour = []
    links = []
    link_colour = []
    labels = []
    load_fails = {}
    id_names = []
    symbol = []

    for s in star_index:
        if s == centre:
            symbol.append('x')
        else:
            symbol.append('diamond')

        label = s + '<br>' + sd[s]['biome_mode']
        id_names.append(s)
        for t in sd[s]['tags']:
            label += '<br>' + t
        labels.append(label)
        point_colour.append(ck[sd[s]['biome_mode']])
        points.extend(sd[s]['extraplanar_coords'])
        for link in sd[s]['links']:
            if link['location'] in sd:
                links.extend(sd[s]['extraplanar_coords'])
                links.extend(sd[link['location']]['extraplanar_coords'])
                links.extend([None, None, None])
                link_colour.append(ck[link['type']])
                link_colour.append(ck[link['type']])
                link_colour.append(ck[link['type']])
            else:
                chunk_fail = link['location'].split('-')[0]
                load_fails[chunk_fail] = load_fails[chunk_fail] + 1 if chunk_fail in load_fails else 1
    # print(', '.join([str(load_fails[i]) for i in load_fails if load_fails[i] > 0]))

    print(len(points))

    mk = go.Scatter3d(x=points[::3], y=points[1::3], z=points[2::3], mode='markers',
                      marker=dict(symbol=symbol, color=point_colour, size=5, opacity=opacity/100,
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
        scene_aspectmode='cube',
        scene=dict(
            xaxis=axes,
            yaxis=axes,
            zaxis=axes),
        )

    data = [dbc.Card(str(i), body=True) for i in range(15)]
    figure = go.Figure(data=[mk, ln], layout=layout)

    if save:
        figure.write_html(str(map_folder) + str(save) + '.html')

    return figure, parameters['centre'], dash.no_update, parameters['path_id'], dash.no_update

dark_style = {'background-color': default.plotly_colours['background'],
                               'border': default.plotly_colours['background'],
                               'color': default.plotly_colours['sea'],
                               'fontColor': default.plotly_colours['sea']}

def edit_pane(node, map_folder):
    import orjson
    ck = default.plotly_colours
    chunk = node.split('-')[0]

    with open(map_folder + str(chunk) + '.json', 'rb') as jfile:
         sd = orjson.loads(jfile.read())
    print(sd[node])
    # QOL TODO make links be a tooltip
    pane = [dbc.Card(dbc.Button(children=sd[node]['name'], id='edit-button-root', color='primary'),
                     id='edit-pane-root',
                     body=True, color=ck[sd[node]['biome_mode']],
                     style={'border': '1px solid #00001a'}),
            dbc.Tooltip(sd[node]['biome_mode'], target='edit-pane-root', placement='left'),
            html.Hr()]
    pane_buttons = [('edit-button-root', 'n_clicks')]
    n = 0
    for planet in sd[node]['planets']:
        pane.append(dbc.Card(dbc.Button(children=planet['name'], id='edit-button-'+str(n), color='primary'),
                             id='edit-pane-'+str(n),
                             body=True,
                             color=ck[planet['biome']],
                             style={'border': '1px solid #00001a'}))
        pane.append(dbc.Tooltip(planet['biome'], target='edit-pane-'+str(n), placement='left'))
        pane_buttons.append(('edit-button-'+str(n), 'n_clicks'))
        n += 1

    modal = dbc.Modal(
        [
            dbc.ModalHeader("placeholder label", id='modal_title', style=dark_style),
            dbc.ModalBody(
                [
                    dbc.Input(id="modal_input_name", type="text", debounce=True, style=dark_style),
                    dcc.Dropdown(
                        id='modal_input_biome',
                        options=[{'label': i, 'value': i} for i in default.biomes],
                        value=(),
                        placeholder='biome',
                        disabled=True,
                        style=dark_style),
                ], style=dark_style
            ),
            dbc.ModalFooter(
                [
                    dbc.Button("OK", color="primary", id="modal_ok_button"),
                    # dbc.Button("Cancel", id="modal_cancel_button"),
                ], style=dark_style
            ),
        ], style=dark_style,
        id="test_modal", is_open=False,
    ),
    pane.append(*modal)
    print(pane)

    return dbc.Card(pane, body=True, color=ck[sd[node]['biome_mode']]), \
        [Output(*i) for i in pane_buttons], \
        [Input(*i) for i in pane_buttons]


# the style arguments for the sidebar. We use position:fixed and a fixed width
# width_units = 'vw'
# width_amount = '35'
width_units = 'rem'
width_amount = '28'

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": width_amount + width_units,
    "padding": '2' + width_units + ' 1' + width_units,
    'color': default.plotly_colours['sea'],
    'backgroundColor': default.plotly_colours['background'],
    'border': default.plotly_colours['background'],
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": width_amount + width_units,
    "margin-right": "2" + width_units,
    "padding": '2' + width_units + ' 1' + width_units,
}

content = sm3d(**parameters)


content_graph = html.Div([
        dcc.Graph(
            id='example-graph',
            figure=content[0],
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
        optionHeight=25,
        placeholder='biome',
        style={'backgroundColor': default.plotly_colours['background'],
               'border': default.plotly_colours['background'],
               'color': default.plotly_colours['sea'],
               'fontColor': default.plotly_colours['sea']}),
    html.Hr(),
    html.H6('number of planets in system'),
    dcc.RangeSlider(
        id='planet--slider',
        min=0,
        max=25,
        value=[0, 25],
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
        id='chunk--slider',
        min=0,
        max=500,
        value=150,
        marks={i: str(i) for i in range(0, 501, 100)})])

bacon = html.Div([
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
        id='chunk--slider--bacon',
        min=0,
        max=500,
        value=150,
        marks={i: str(i) for i in range(0, 501, 100)})
]
)
path = html.Div([
    html.Hr(),
    dbc.InputGroup(
    [
        dbc.InputGroupAddon(
            dbc.Button("draw path from seed to: ", id="select-path",  color="primary"),
            addon_type="append",
        ),
        dbc.Input(id="select-path-data", value='', placeholder=parameters['path_id'],
                  autoComplete=False, persistence=False, debounce=True,
                  style={'backgroundColor': default.plotly_colours['background'],
                         'border': default.plotly_colours['background'],
                         'color': default.plotly_colours['sea']}),
    ]),
    html.Hr()

])

pane_cards, pane_outputs, pane_inputs, = edit_pane(parameters['centre'], parameters['map_folder'])



my_edit_kit = html.Div(pane_cards, id='edit-this', style={"maxHeight": "50vh", "overflow-y": "scroll"})


tabs = html.Div([dbc.Tabs([
    dbc.Tab(ball_point, tab_id='ball_point', label="global search", active_label_style={'color': 'primary'}),
    dbc.Tab(bacon, tab_id='bacon', label="local search", active_label_style={'color': 'primary'}),
    dbc.Tab(path, tab_id='path', label="path to", active_label_style={'color': 'primary'}),
    dbc.Tab(my_edit_kit, tab_id='edit_tools', label="edit kit", active_label_style={'color': 'primary'}),
    ], id='my--tabs'),

    html.H6('opacity slider'),
    dcc.Slider(
        id='opacity--slider',
        min=0,
        max=100,
        value=30,
        marks={i: str(i) for i in range(0, 101, 10)}),
    html.Hr(),
    dbc.Checklist(
        options=[{"label": "show axes", "value": 1}, {"label": "save map", "value": 2}],
        value=[],
        id="checklist-input",
        style={'backgroundColor': default.plotly_colours['background'],
               'border': default.plotly_colours['background'],
               'color': default.plotly_colours['sea']}
    ),
    html.Hr(),
    dbc.InputGroup(
    [
        dbc.InputGroupAddon(
            dbc.Button("select seed", id="select-id",  color="primary"),
            addon_type="append",
        ),
        dbc.Input(id="select-id-data", value='', placeholder=parameters['centre'],
                  autoComplete=False, persistence=False, debounce=True,
                  style=dark_style),
    ]),
    html.Hr(),
    dbc.Button(id='submit-button-state', children="Map from seed: " + parameters['centre'], n_clicks=0, color="primary",
               block=True, type='reset')
],
    style=SIDEBAR_STYLE,
)

app.layout = html.Div([tabs, content_graph])
# TODO  turn off output validaion,  via this -
app.config.suppress_callback_exceptions = True

@app.callback(
    Output('example-graph', 'figure'),
    Output('select-id-data', 'value'),
    Output('submit-button-state', 'children'),
    Output('select-path-data', 'value'),
    Output('edit-this', 'children'),
    Input('example-graph', 'figure'),
    Input('example-graph', 'clickData'),
    Input('submit-button-state', 'n_clicks'),
    Input('biome--dropdown', 'value'),
    Input('planet--slider', 'value'),
    Input('range--slider', 'value'),
    Input('chunk--slider', 'value'),
    Input('opacity--slider', 'value'),
    Input('checklist-input', 'value'),
    Input('select-id', 'n_clicks'),
    Input('select-id-data', 'value'),
    Input('degrees--slider', 'value'),
    Input('chunk--slider--bacon', 'value'),
    Input('select-path', 'n_clicks'),
    Input('select-path-data', 'value'),
    Input('my--tabs', 'active_tab'),
)
def update_search(figure, clickData, button, biomes, planet_slider, range_slider, chunk_slider,
                  opacity_slider, checklist_input, select_button, select_id, degrees_slider, chunk_slider_bacon,
                  path_button, path_id, search_mode):
    parameters['biomes'] = biomes
    parameters['planets'] = planet_slider
    parameters['opacity'] = opacity_slider
    if search_mode != 'edit_tools':
        parameters['search_mode'] = search_mode
        if search_mode == 'bacon':
            parameters['distance'] = degrees_slider
            parameters['load'] = chunk_slider_bacon
        else:
            parameters['distance'] = range_slider
            parameters['load'] = chunk_slider
    if search_mode != 'path':
        parameters['path_id'] = 'None'

    print(parameters)
    print(time.ctime())
    print(button)
    print(select_button)
    print(clickData)

    # QOL TODO: local group view

    if button != presses['search_button']:
        presses['search_button'] = button
        # QOL TODO: spinner on click to show loading
        print('search button')
        print(checklist_input)
        if 2 in checklist_input:
            parameters['save'] = str(parameters['centre']) + '_' + str(parameters['search_mode'])
        else:
            parameters['save'] = False
        print(parameters)
        return sm3d(**parameters)
    elif select_button != presses['select_button']:
        presses['select_button'] = select_button
        print(select_id)
        parameters['centre'] = select_id
        # QOL TODO: change button colour on click to show biome of selection
        global pane_outputs
        global pane_inputs
        pane_cards, pane_outputs, pane_inputs, = edit_pane(parameters['centre'], parameters['map_folder'])
        return dash.no_update, parameters['centre'], "Map from seed: " + parameters['centre'],\
            parameters['path_id'], pane_cards
    elif path_button != presses['path_button']:
        presses['path_button'] = path_button
        print(path_id)
        parameters['path_id'] = path_id
        return sm3d(**parameters)
    elif clickData != presses['graph_click']:
        presses['graph_click'] = clickData
        print('click update data')
        # parameters['centre'] = clickData['points'][0]['customdata']
        return dash.no_update, clickData['points'][0]['customdata'], dash.no_update, \
               clickData['points'][0]['customdata'], dash.no_update
    else:
        print('button other')
        print(button)
        if figure['data'][0]['marker']['opacity'] != opacity_slider / 100:
            figure['data'][0]['marker']['opacity'] = opacity_slider / 100
            return figure,  parameters['centre'], dash.no_update, parameters['path_id'], dash.no_update
        if 1 in checklist_input:
            axis_setting = True
        else:
            axis_setting = False
        if figure['layout']['scene']['xaxis']['showgrid'] != axis_setting:
            figure['layout']['scene']['xaxis']['showgrid'] = axis_setting
            figure['layout']['scene']['yaxis']['showgrid'] = axis_setting
            figure['layout']['scene']['zaxis']['showgrid'] = axis_setting
            figure['layout']['scene']['xaxis']['showticklabels'] = axis_setting
            figure['layout']['scene']['yaxis']['showticklabels'] = axis_setting
            figure['layout']['scene']['zaxis']['showticklabels'] = axis_setting
            return figure, parameters['centre'], dash.no_update, parameters['path_id'], dash.no_update
        return dash.no_update, dash.no_update , dash.no_update, parameters['path_id'], dash.no_update


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

def define_modal(node, button):
    import orjson
    parameters['modal_button'] = button
    chunk = node.split('-')[0]
    with open(parameters['map_folder']+chunk+'.json', 'rb') as f:
        sd = orjson.loads(f.read())
    if button == 0:
        return True, sd[node]['name'], True, sd[node]['biome_mode']
    else:
        n = 1
        for planet in sd[node]['planets']:
            if n == button:
                return True, planet['name'], False, planet['biome']
            else:
                n += 1


@app.callback(
    *pane_outputs,
    Output('test_modal', 'is_open'),
    Output('modal_input_name', 'value'),
    Output('modal_input_biome', 'disabled'),
    Output('modal_input_biome', 'value'),
    Output('modal_ok_button', 'n_clicks'),
    Output('select-id', 'n_clicks'),
    Input('modal_ok_button', 'n_clicks'),
    Input('modal_input_name', 'value'),
    Input('modal_input_biome', 'value'),
    *pane_inputs,
)
def show_modal(*args):
    """Show modal for adding a label."""
    import orjson
    # if any button hit, use the current seed and the button hit to define the modal
    # show taht modal
    modal_buttons = [i for i in range(len(args[3:])) if args[i+3]]
    if len(modal_buttons) == 0 and not args[0]:
        return dash.no_update
    # hit
    print('modal')
    print(len(args))
    print(modal_buttons)
    print(args)

    # TODO change to pattern matching callbacks
    # https://dash.plotly.com/pattern-matching-callbacks


    c = parameters['centre']
    chunk = c.split('-')[0]
    with open(parameters['map_folder'] + chunk + '.json', 'rb') as f:
        sd = orjson.loads(f.read())
    if args[0]:
        if parameters['modal_button'] == 0:
            sd[c]['name'] = args[1]
        else:
            sd[c]['planets'][parameters['modal_button']-1]['name'] = args[1]
            sd[c]['planets'][parameters['modal_button']-1]['biome'] = args[2]
        with open(parameters['map_folder']+chunk+'.json', 'wb') as f:
            print('wrote it')
            f.write(orjson.dumps(sd))
        return *[0 for _ in args[3:]], False, args[1], parameters['modal_button'] == 0, args[2], 0,\
               presses['select_button']+1 if type(presses['select_button']) == int else 1

    return *[0 for _ in args[3:]], *define_modal(parameters['centre'], *modal_buttons), 0, dash.no_update

# app.callback(
#     Input()
# )


if __name__ == '__main__':
    # TODO stress test and cleanup
    print('test')
    app.run_server(debug=True)
