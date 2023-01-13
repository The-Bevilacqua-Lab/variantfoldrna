# import dash
# from dash import html
# import plotly.graph_objects as go
# from dash import dcc
# import plotly.express as px
# from dash.dependencies import Input, Output
# import pandas as pd
# import dash_bootstrap_components as dbc
# from dash_bootstrap_templates import load_figure_template


# app = dash.Dash(external_stylesheets=[dbc.themes.LUX])
# load_figure_template('LUX')

# df1 = pd.read_csv("combined_ribosnitch_pred_37_40bp_flank_rice.txt", sep="\t", header=None)
# df = df1.iloc[:,[0,1,2,3,5,6,8,9]]
# df.columns = ["chrom", "pos", "ref", "alt", "gene", "match", "strand", "score"]

# ops = [{'label': i, 'value': i} for i in df['gene'].unique()]

# app.layout = html.Div(id = 'parent', children = [
#     html.H1(id = 'H1', children = 'SPARCS', style = {'textAlign':'center',\
#                                             'marginTop':40,'marginBottom':40}),

#         dcc.Dropdown( id = 'dropdown',
#         options = ops,
#         value = 'gene',),
#         dcc.Graph(id = 'bar_plot')
#     ])
    
    
# @app.callback(Output(component_id='bar_plot', component_property= 'figure'),
#               [Input(component_id='dropdown', component_property= 'value')])
# def graph_update(dropdown_value):
#     print(dropdown_value)
#     fig = go.Figure([go.Histogram(x = df["score"][df['gene'] == dropdown_value])])
    
#     fig.update_layout(title = 'RiboSNitch Score',
#                       xaxis_title = 'Score',
#                       yaxis_title = '# of SNPs'
#                       )
#     return fig  


# dbc.Row(
#      [dbc.Col(sidebar),
#       dbc.Col(dcc.Graph(id = 'graph1', figure = fig1), width = 9, style = {'margin-left':'15px', 'margin-top':'7px', 'margin-right':'15px'})
#       ])

# if __name__ == '__main__': 
#     app.run_server()

from dash import Dash, html, dcc, Input, Output
import numpy as np
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import json
import urllib.request as urlreq
import dash_bio as dashbio
import base64


app = Dash(__name__, external_stylesheets=[dbc.themes.CERULEAN])

df1 = pd.read_csv("../../test1.txt", sep="\t", header=None)
df = df1.iloc[:,[0,1,2,3,5,6,8,9]]
df.columns = ["chrom", "pos", "ref", "alt", "gene", "match", "strand", "score"]
ops = [{'label': 'All', 'value': 'All'}]
ops += [{'label': i, 'value': i} for i in df['gene'].unique()]

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "1rem 1rem",
}

def get_data(df, drop_value):
    if drop_value == "All":
        return df["score"]
    else:
        return df["score"][df['gene'] == drop_value]

gene = html.Div(dbc.Row(
    [   html.Img(src="assets/sparcs.png"),
        
        dbc.Label("Gene", html_for="gene"),
        dcc.Dropdown( id = 'dropdown',
        options = ops,
        value = 'gene',),
    ]),
    className="mt-2", style=SIDEBAR_STYLE
)

# control_panel = dbc.Card(
#     dbc.CardBody(
#         [gene],
#         className="bg-light",
#     ), style=SIDEBAR_STYLE,
# )

# graph = dbc.Card(
#     [html.Div(id="gene_s", className="text-danger"),dcc.Graph(id="gene_struct_plot"), dcc.Graph(id="bar_plot")]
# )

# gene_struct = dbc.Card(
#     [html.Div(id="error_mss", className="text-danger")]
# )

data = urlreq.urlopen(
    'https://git.io/needle_PIK3CA.json'
).read().decode('utf-8')

mdata = json.loads(data)
print(mdata)

def get_needle_data(df, gene, file_name):
    df = df[df['gene'] == gene]
    snp_locs = df['pos'].tolist()
    snp_scores = df['score'].tolist()
    utrs = pd.read_csv(file_name, sep="\t", header=None)
    utrs.columns = ["gene", "start", "end", "five_start", "five_end", "three_start", "three_end"]
    utrs = utrs[utrs['gene'] == gene]
    five_coords = str(float(utrs['five_start'].tolist()[0])) + "-" +  str(float(utrs['five_end'].tolist()[0]))
    print(five_coords)
    three_coords = str(float(utrs['three_start'].tolist()[0])) + "-" + str(float(utrs['three_end'].tolist()[0]))
    cds_coords = str(float(utrs['five_end'].tolist()[0])) + "-" + str(float(utrs['three_start'].tolist()[0]))

    data = {'x': [str(round(x, 4)) for x in snp_locs], 'y': [str(x) for x in snp_scores],
    "domains": [{'name': '5_prime_UTR', 'coord': five_coords},{'name': 'CDS', 'coord': cds_coords},{'name': '3_UTR', 'coord': three_coords}]}
    print(data)
    return data

other = get_needle_data(df, "Os01g0100100", "../../gene_locs.txt")

content = html.Div(dbc.Row([dashbio.NeedlePlot(
        id='dashbio-default-needleplot',
        mutationData=other, height=300,width=800,
    ), dcc.Graph(id = 'bar_plot')]), style=CONTENT_STYLE)


# the styles for the main content position it to the right of the sidebar and
# add some padding.

# Layout for the entire page
app.layout = html.Div([gene, content])

@app.callback(Output(component_id='bar_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
def graph_update(dropdown_value):
    print(dropdown_value)
    fig = go.Figure([go.Histogram(x = get_data(df, dropdown_value))])
    
    fig.update_layout(title = 'RiboSNitch Score',
                      xaxis_title = 'Score',
                      yaxis_title = '# of SNPs'
                      )
    return fig


# @app.callback(Output(component_id='gene_struct_plot', component_property= 'figure'),
#               [Input(component_id='dropdown', component_property= 'value')])
# def graph_update(dropdown_value):
#     data = urlreq.urlopen(
#         'https://git.io/needle_PIK3CA.json'
#     ).read().decode('utf-8')

#     mdata = json.loads(data)

#     fig = dashbio.NeedlePlot(
#         mutationData=mdata,
#         needleStyle={
#             'stemColor': '#FF8888',
#             'stemThickness': 2,
#             'stemConstHeight': True,
#             'headSize': 10,
#             'headColor': ['#FFDD00', '#000000']
#         }
#     )
#     return fig


if __name__ == "__main__":
    app.run_server(debug=True)