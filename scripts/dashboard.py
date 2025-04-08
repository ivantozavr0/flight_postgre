import dash
import os
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly
import psycopg2
import pandas as pd
from datetime import datetime, timezone
import logging

# это дашборд. здесь рисуются маршруты всех самолетов за последний час над Черным морем и гистограммы распределения самолетов по авиалиниям и моделям

logging.basicConfig(
    filename='logs/dashboard.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

#цвета для текста и фона
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

logging.info("in dash")

#-----------------------------считываем данные из часового отчета для построения точек на карте
def create_trail_figure():
# берем информацию за последний час
    global colors

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )
    
    logging.info("trail")

    cursor = conn.cursor()

    cursor.execute("SELECT model FROM hourly_report") 
    rows_m = cursor.fetchall() 
    cursor.execute("SELECT icao FROM hourly_report") 
    rows_icao = cursor.fetchall() 
    cursor.execute("SELECT trail FROM hourly_report") 
    rows_trail = cursor.fetchall() 

    cursor.close()
    conn.close()

    #------------------------------преобразовали в dataframe

    rows_summary = []

    for mod, icao, trail in zip(rows_m, rows_icao, rows_trail):
        rows_summary.append([mod[0], icao[0], trail[0]])

    df_trails = pd.DataFrame(rows_summary, columns=['model', 'icao', 'trail'])

    #----------------------------------------это граф для рисунка-карты

    fig = go.Figure()

    color_palette = plotly.colors.qualitative.Plotly
    counter = 0

    for index, row in df_trails.iterrows(): 
        latitudes = [point[0] for point in row['trail']]
        longitudes = [point[1] for point in row['trail']]

        fig.add_trace(go.Scattergeo(
            lat=latitudes,
            lon=longitudes,
            mode='lines', 
            line=dict(width=2, color=color_palette[index%len(color_palette)]),
            name=row['icao'],
            legendgroup=row['model'],
            legendgrouptitle_text=row['model']
        ))

    # добавили карту земли
    fig.update_layout(
    showlegend = True,
    geo = dict(
        scope = 'world',
        landcolor = 'rgb(255, 217, 217)',
        bgcolor = 'rgb(0, 255, 255)'
    ),
    plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'],
    title_font_color="white",
    legend_font_color="white",
    font={ 'color': colors['text'] }
)
    return fig

# гистограмма по авиалиниям
def create_airline_figure():
    global colors

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM airline_report") 
    rows_air = cursor.fetchall() 
    
    cursor.close()
    conn.close()
    
    df_air = pd.DataFrame(rows_air, columns=["Airlines", "Number_of_aircrafts"])
        
    fig = px.bar(df_air, x="Number_of_aircrafts", y="Airlines", orientation='h', color="Airlines")
    fig.update_layout(plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'], font={
                    'color': colors['text']
                })
    return fig
    
# гистограмма по моделям
def create_model_figure():
    global colors

    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "flightradardb"),
        user=os.getenv("POSTGRES_USER", "admin"),
        password=os.getenv("POSTGRES_PASSWORD", "pass"),
        port="5432"
    )

    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM model_report") 
    rows_mod = cursor.fetchall()

    cursor.close()
    conn.close()
    
    df_mod = pd.DataFrame(rows_mod, columns=["Models", "Number_of_models"])
    
    fig = px.bar(df_mod, x="Number_of_models", y="Models", orientation='h')
    fig.update_layout(plot_bgcolor=colors['background'],
    paper_bgcolor=colors['background'], font={
                    'color': colors['text']
                })
    return fig


#------------------------------------------

# обновляем информацию о последнем обновлении дашборда
def create_title():
    update_time = datetime.now(timezone.utc)
    return f"Последнее обновление: {update_time}"


app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children="Маршруты самолетов в акватории Черного моря", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    html.H2(id='title', children=create_title(), style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    html.Div(children="""Если вы не видите данные, то это значит, что они еще не загружены с сайта FlightRadar24. 
    Во избежание блокировки, парсинг займет некоторое время.\n Дашборд обновляется каждые 2.5 минуты. Вероятнее всего, через 
    этот промежуток времени на дашборде уже появятся маршруты и статистика в виде диаграмм.""", 
             style={
            'color': 'white'
        }),
    html.Div(children="""!!! По непонятной причине модуль datetime при развертывании на docker дает время по UTC+00 (минус 3 часа по сравнению с московским), исправить не получилось :(""", 
             style={
            'color': 'white'
        }),
    html.H3(children="Все обнаруженные маршруты в акватории Черного моря за последний час (или с начала работы программы)", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    dcc.Graph(id='trail-graph', figure=create_trail_figure()),
    html.H3(children="Количество самолетов в зависимости от авиалинии в акватории Черного моря за последний час (или с начала работы программы)", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    dcc.Graph(id='airline-graph', figure=create_airline_figure()),
    html.H3(children="Количество самолетов в зависимости от модели в акватории Черного моря за последний час (или с начала работы программы)", style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    dcc.Graph(id='model-graph', figure=create_model_figure()),
    dcc.Interval(
        id='interval-component',
        interval=2.5 * 60 * 1000  # обновляем дашборд каждые 2.5 минуты
    )
])

# будем периодически обновляться 
@app.callback(
    [Output('title', 'children'),
     Output('trail-graph', 'figure'),
     Output('airline-graph', 'figure'),
     Output('model-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    tit = create_title()
    trail_fig = create_trail_figure()
    airline_fig = create_airline_figure()
    model_fig = create_model_figure()
    return tit, trail_fig, airline_fig, model_fig

if __name__ == '__main__':
    logging.info("Start dash!")
    app.run(debug=False, port=8070, host='0.0.0.0')
