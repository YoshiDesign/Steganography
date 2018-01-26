import plotly.plotly as py
import plotly.offline as po
import plotly.graph_objs as go

# Copied from Pset6 with added annotations + donut, nom
def pie(red, green, blue):
    figure = {
        "data": [
            {
            "labels": [
                "red",
                "green",
                "blue",
            ],
            "hoverinfo": "none",
            "name" : "Pixel Distrobution",
            "domain" : {"x" : [0, 1]},
            "hole" : .7,
            "marker": {
                "colors": ["rgb(255,0,0)","rgb(0,255,0)","rgb(0,0,255)"]
            },
            "type": "pie",
            "values": [red, green, blue]
            }
        ],
        "layout": {
            "annotations" : [
                {
                    "font" : {
                        "color" : "white",
                        "size" : 25
                    },
                    "showarrow": False,
                    "text" : "Pixel Ratio"
                }
            ],
            "showlegend": False,
            "paper_bgcolor" : 'rgba(0,0,0,0)',
            "plot_bgcolor": 'rgba(0,0,0,0)'},
    }

    return po.plot(figure, output_type="div", show_link=False, link_text=False)

# Group Bar
def bar_comp(ra, ga, ba, rb, gb, bb):
    trace1 = go.Bar(
    x=['red', 'green', 'blue'],
    y=[rb, gb, bb],
    name='Before',
    marker={'color' : 'rgb(8, 216, 57)'}
    )
    trace2 = go.Bar(
        x=['red', 'green', 'blue'],
        y=[ra, ga, ba],
        name='After',
        marker={'color' : 'rgb(53, 1, 117)'}
    )

    data = [trace1, trace2]
    layout = go.Layout(
        barmode='group',
        title = 'Average Pixel-Color Value',
        paper_bgcolor = 'rgba(0,0,0,0)',
        plot_bgcolor = 'rgba(0,0,0,0)',
        font=dict(family='Courier New, monospace', size=18, color='#ffffff')

    )

    fig = go.Figure(data=data, layout=layout)
    return po.plot(fig, filename='grouped-bar', output_type="div", show_link=False, link_text=False)