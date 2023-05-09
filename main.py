import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import matplotlib.pyplot as plt
import dash
from dash import Dash, html, dcc
# import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from flask import Flask

#bootstrap styling
bs = "https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css"


server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',
    external_stylesheets=[bs]
)



## GRAPHS
df = pd.read_csv('population_by_region_combined_en.csv')
df.drop('Index.1', axis=1, inplace=True)
df['location'] = df['province'].apply(lambda x: x.lower())

# map chart
provinces = gpd.read_file('https://raw.githubusercontent.com/ppatrzyk/polska-geojson/master/wojewodztwa/wojewodztwa-max.geojson')
provinces = provinces.set_index('nazwa')

mapa = px.choropleth(data_frame=df, geojson=provinces, locations=df.groupby('location', as_index=False)['overall overall'].agg(sum)['location'],
                     color=df.groupby('location', as_index=False)['overall overall'].agg(sum)['overall overall'],
                           color_continuous_scale="Redor",
                             projection='mercator'
                          )
mapa.update_geos(fitbounds='locations', visible=False)
mapa.update_layout(paper_bgcolor='rgba(0,0,0,0)', title_text='Population by voivodeship', title_x=0.5,width=650, height=650)

#pie chart
pie = px.pie(values = [df['overall man'].sum(),df['overall woman'].sum()], names=['Men','Women'],
            title='Population per Gender', color_discrete_sequence=px.colors.sequential.RdBu)
pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', title_x=0.5,width=350, height=350)

#line plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.groupby('year').sum().index, y=df.groupby('year').sum()['pre-working age'],
                    mode='lines',
                    name='Pre-working age'))
fig.add_trace(go.Scatter(x=df.groupby('year').sum().index, y=df.groupby('year').sum()['working age'],
                    mode='lines',
                    name='Working age'))
fig.add_trace(go.Scatter(x=df.groupby('year').sum().index, y=df.groupby('year').sum()['post-working age'],
                    mode='lines',
                    name='Post-working age'))
fig.update_layout(title='Population over years by economic age groups',
                  title_x=0.5, width=700, height=300,
                    paper_bgcolor='rgba(0,0,0,0)',
                   xaxis_title='Year',
                   yaxis_title='Population')

#population counter
population = f"{float(df['overall overall'].sum()/1000000):.2f} mln"


#DASHBOARD LAYOUT
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.H1(
                            children="Poland Population in Years",
                            style={'textAlign':'center'},
                            className='header-title'
                        ),
                        html.H3(
                            children="Population per Voivodeship between 2002 and 2021",
                            className='header-description',
                            style={'textAlign': 'center'}
                        )
                        ],
                    style={'display':'inline-block'},
                    className='head-text'
                ),
                html.Div(
                    children=[
                        html.H4(
                            id='population',
                            children=population
                        ),
                        html.H6(
                            children="Population",
                            style={'textAlign': 'center'}
                        )
                    ],
                    style={'border-radius':'15px','background-color':'white', 'display':'inline-block'},
                    className='pop-nr'
                ),
                # menu filter
                html.Div(
                    children=[
                        html.Div(children='Year',
                                 style={'fontSize': '18px'},
                                 className='menu-title'),
                        dcc.Dropdown(
                            id='year-filter',
                            clearable=False,
                            searchable=False,
                            value=2021,
                            options=[{'label': year, 'value': year} for year in df['year'].unique()]
                        )
                    ], className='year-selector',
                    style={'display':'inline-block'}
                ),
            ],
            className='header',
        ),

        html.Div(
            html.Tr(
            children=[
                html.Td(
                    children=dcc.Graph(
                        id='map',
                        figure=mapa,
                        className='map_chart container-fluid',
                        config={"displayModeBar": False},
                        style={ 'display':'inline-block', 'border-radius':'15px', 'background-color':'white'}
                    ),
                ),
                html.Td(
                    children=[
                        html.Tr(
                        dcc.Graph(
                        id='pie',
                        figure=pie,
                        className='pie_chart container-fluid',
                        config={"displayModeBar": False},
                        style={'border-radius':'15px', 'background-color':'white', 'width': '30%'}
                        )
                    ),
                        html.Tr(children=[
                            dcc.Graph(
                            id='line',
                            figure=fig,
                            className='line_chart container-fluid',
                            config={"displayModeBar": False},
                            #style={'border-radius':'15px', 'background-color':'white', 'width': '30%'}
                            ),
                            dcc.RangeSlider(2002, 2021, updatemode='drag', marks={i: '{}'.format(i) for i in range(2002,2022)}, value=[2002,2021], id='slider')
                            ],
                            style={'border-radius':'15px', 'background-color':'white'},
                            className='line-box'
                    )
                    ], style={'display':'inline-block'}
                )
            ]
            ), className='row1 my-auto'
        )


    ], className='box container-fluid'
)

@app.callback(
    Output('map','figure'),
    Output('pie','figure'),
    Output('population','children'),
    [Input('year-filter','value')]
)
def update_chart(year):
    filtered_data = df[df['year'] == int(year)]
    mapa = px.choropleth(data_frame=filtered_data, geojson=provinces,
                         locations=filtered_data.groupby('location', as_index=False)['overall overall'].agg(sum)['location'],
                         color=filtered_data.groupby('location', as_index=False)['overall overall'].agg(sum)['overall overall'],
                         color_continuous_scale="Redor",
                         projection='mercator'
                         )
    mapa.update_geos(fitbounds='locations', visible=False)
    mapa.update_layout(paper_bgcolor='rgba(0,0,0,0)', title_text='Population by voivodeship', title_x=0.5, width=650,
                       height=650)

    pie = px.pie(values=[filtered_data['overall man'].sum(), filtered_data['overall woman'].sum()], names=['Men', 'Women'],
                 title='Population per Gender', color_discrete_sequence=px.colors.sequential.RdBu)
    pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', title_x=0.5, width=350, height=350)

    population = f"{float(filtered_data['overall overall'].sum()/1000000):.2f} mln"
    return mapa, pie, population

@app.callback(
    Output('line','figure'),
    [Input('slider','value')]
)
def update_line_chart(year):
    data_range = df[(df['year'] >= int(year[0])) & (df['year'] <= int(year[1]))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data_range.groupby('year').sum().index, y=data_range.groupby('year').sum()['pre-working age'],
                             mode='lines',
                             name='Pre-working age'))
    fig.add_trace(go.Scatter(x=data_range.groupby('year').sum().index, y=data_range.groupby('year').sum()['working age'],
                             mode='lines',
                             name='Working age'))
    fig.add_trace(go.Scatter(x=data_range.groupby('year').sum().index, y=data_range.groupby('year').sum()['post-working age'],
                             mode='lines',
                             name='Post-working age'))
    fig.update_layout(title='Population over years by economic age groups',
                      title_x=0.5, width=700, height=300,
                      paper_bgcolor='rgba(0,0,0,0)',
                      xaxis_title='Year',
                      yaxis_title='Population')
    return fig


@server.route('/dash/')
def my_dash_app():
    return app.index()

if __name__ == '__main__':
    app.run_server(debug = True)