from dash import html, dcc
from config import (HEADER_STYLE, LOGO_STYLE, TITLE_STYLE, BUTTON_STYLE, INPUT_DIV_STYLE)


def create_header():
    """Create the header div."""
    return html.Div(
                style=HEADER_STYLE,
                children=[
                    html.Img(src="assets/cccmtl_logo.png", style=LOGO_STYLE),
                    html.H3("Calendrier SEAO ", style=TITLE_STYLE)
                ]
            )
    
    
    
def create_filter_button():
    """Create the filter button for flagged items."""
    return html.Button(
        "Montrer les contrats en fin de vie",
        id="show-flagged-btn",
        n_clicks=0,
        style=BUTTON_STYLE,
    )
    
    
   
def create_slider_selector():
    """Create a slider selector (placeholder)."""
    return dcc.Slider(
        id='threshold-slider',
        className='slider',
        min=0,
        max=18,
        step=1,
        value=7,
        marks={
        0: {'label': 'AJD', 'style': {'color': "#ff0000"}},
        3: {'label': '3 mois', 'style': {'color': '#ff7f0e'}},
        7: {'label': '7 mois'},
        18: {'label': '18'}},
        included=False
        
    )
    
    
    
def create_input_div(filter_button, slider_selector):
    """Create the input div."""
    return html.Div(
        id="input-div",
        style=INPUT_DIV_STYLE,
        children=[
            filter_button,
            slider_selector
        ]
    )
    
    
    
    
    
    
def create_timeline_div():
    """Create the timeline div."""
    return html.Div(
        id="timeline-div",
        style={
            'padding': '20px',
            'width': '100%',
            'boxSizing': 'border-box'
        },
        children=[
            # Timeline figure will be inserted here
        ]
    )
    
    
    
    
    
def create_timeline_fig():
    
    """Create the timeline figure placeholder."""
    return html.Div(
        id="timeline-figure",
        style={
            'width': '100%',
            'height': '600px',
        }
    )
