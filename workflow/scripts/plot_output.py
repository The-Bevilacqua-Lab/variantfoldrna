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

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

heading = html.H4(
    html.Img(src="/Users/lab/Desktop/snakemake/SPARCS/static/SPARCS.png", style={"height": "50px"}),
    "SPARCS Ouput Analysis", className="bg-primary text-white p-2"
)

df1 = pd.read_csv("../../combined_ribosnitch_pred_37_40bp_flank_rice.txt", sep="\t", header=None)
df = df1.iloc[:,[0,1,2,3,5,6,8,9]]
df.columns = ["chrom", "pos", "ref", "alt", "gene", "match", "strand", "score"]
ops = [{'label': 'All', 'value': 'All'}]
ops += [{'label': i, 'value': i} for i in df['gene'].unique()]

def get_data(df, drop_value):
    if drop_value == "All":
        return df["score"]
    else:
        return df["score"][df['gene'] == drop_value]

gene = html.Div(
    [   dbc.Label("Gene", html_for="gene"),
        dcc.Dropdown( id = 'dropdown',
        options = ops,
        value = 'gene',),
    ],
    className="mt-2",
)

control_panel = dbc.Card(
    dbc.CardBody(
        [gene],
        className="bg-light",
    )
)

graph = dbc.Card(
    [html.Div(id="error_msg", className="text-danger"), dcc.Graph(id="bar_plot")]
)

gene_struct = dbc.Card(
    [html.Div(id="error_msg", className="text-danger"), dcc.Graph(id="gene_struct_plot")]
)

app.layout = html.Div(
    [heading, dbc.Row([dbc.Col(control_panel, md=4), dbc.Col(graph, md=8)]), dbc.Row([dbc.Col(gene_struct, md=8)])]
)

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


@app.callback(Output(component_id='gene_struct_plot', component_property= 'figure'),
              [Input(component_id='dropdown', component_property= 'value')])
def graph_update(dropdown_value):
    fig = go.Figure(go.Scatter(x=[3,3,5,5,3], y=[0.5,1.5,1.5,0.5,0.5], fill="toself"))
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)