import subprocess
import sys


#Verifie si dash et plotly sont installés et les installe sinon
def ensure_package(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
ensure_package("dash")
ensure_package("plotly")


from dash import Dash, Output, Input, State, html


#from data_processing import import_raw_data, get_timeline_data
from config import BACKGROUND_COLOR
from ui import create_header, create_filter_button,create_timeline_fig, create_slider_selector, create_input_div
from callbacks import toggle_flagged


## =============================== LOAD ============================== ##
#df = import_raw_data()
#data_timeline = get_timeline_data(df)

app = Dash(__name__)
app.title = "Calendrier SEAO"



## =============================== DEFINE ============================== ##
filter_button= create_filter_button()
slider_selector= create_slider_selector()





## =============================== LAYOUT ============================== ##
app.layout =  html.Div(
    style={'backgroundColor': BACKGROUND_COLOR, 'minHeight': '100vh'},
    children=[
        create_header(),
        create_input_div(filter_button, slider_selector),
        create_timeline_fig()
    ]
)

    



## ======================== CALLBACKS FUNCTIONS ======================== ##

#! Timeline Callback
@app.callback(
    Output("timeline-figure", "children"),
    Output("show-flagged-btn", "children"),
    Input("show-flagged-btn", "n_clicks"),
    Input("threshold-slider", "value")
)
def toggle_flagged_callback(n_clicks, threshold):
    return toggle_flagged(n_clicks, threshold)











## ======================== MAIN ======================== ##
if __name__ == '__main__':
    app.run(debug=True)


