from dash import html






#! Timeline Callback
def toggle_flagged(n_clicks, threshold):
    
    show_flagged_only = (n_clicks % 2 == 1)
    
    btn_label = "Montrer tous les contrats" if show_flagged_only else "Montrer les contrats en fin de vie"

    out=f"contrats en fin de vie dans {threshold} mois" if show_flagged_only else "tous les contrats"
    
    test=html.P(
        f"{out}",
        style={'color': 'white', 'fontSize': '20px', 'marginTop': '20px'}
    )

    return test, btn_label