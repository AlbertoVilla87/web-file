from dash import html, dcc, Dash
from dash.dependencies import Input, State, Output

from modeling.haystack import DocumentStore, Retriever
from scraper.twitter import Twitter

from preparation.data_manager import DataManager

manager = DataManager()
document_store = DocumentStore("", manager)
retriever = Retriever(document_store)

app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            children="Pregunta a los candidatos",
            style={"textAlign": "center", "font-family": "Open Sans, sans-serif"},
        ),
        html.Div(
            dcc.Input(
                id="query",
                type="text",
                placeholder="",
                className="input",
                style={
                    "margin-left": "37%",
                    "width": "450px",
                    "height": "20px",
                    "padding": "10px",
                    "margin-top": "10px",
                    "font-size": "16px",
                },
            )
        ),
        html.Div(
            html.Button(
                "Responder",
                id="search",
                n_clicks=0,
                style={
                    "margin-left": "12%",
                    "width": "100px",
                    "height": "30px",
                    "font-size": "16px",
                },
            ),
            style={"margin-left": "40%", "padding-top": "20px"},
        ),
        html.Div(id="output", children=""),
    ]
)

@app.callback(
    Output("output", "children"),
    State("query", "value"),
    Input("search", "n_clicks"),
)
def update_news(value, n_clicks):

    if n_clicks > 0:
        docs = retriever.retrieve(value, top_k=10)
        childrens = []
        for doc in docs:
            childrens.append(html.Div([html.H3(doc[DocumentStore.NAME] + " " + doc[Twitter.DATE]), html.Span(doc[Twitter.TWEET])], 
                    style={"margin-left": "32%", "font-family": "Open Sans, sans-serif", "width": "700px"}))
        return childrens

    return ""

if __name__ == "__main__":
    app.run_server()
