import time
from dash import html, dcc, Dash
from dash.dependencies import Input, State, Output

from modeling.haystack import DocumentStore, Reader
from processing.transcripts import Transcripts
from processing.translation import Translator

from preparation.data_manager import DataManager


model_path = "minilm-uncased-squad2"
manager = DataManager()
document_store = DocumentStore("", manager)
reader = Reader(model_path, document_store)


def create_output(doc):
    """_summary_
    :param doc: _description_
    :type doc: _type_
    :return: _description_
    :rtype: _type_
    """
    out = html.Div(
        [
            html.Span(
                html.H4(
                    [
                        html.A(doc[Reader.ANSWER_TAG], href=doc[Transcripts.URL]),
                    ]
                ),
            ),
            html.Span(
                [
                    html.Span(
                        doc[Transcripts.SUBJECT] + " - ", style={"color": "#9aa0a6"}
                    ),
                    html.Span(doc[Transcripts.TEXT]),
                ]
            ),
        ],
        style={
            "margin-left": "25%",
            "font-family": "Open Sans, sans-serif",
            "width": "50%",
        },
    )
    return out


app = Dash(__name__)

app.layout = html.Div(
    [
        html.Link(
            href="https://fonts.googleapis.com/css?family=Orbitron", rel="stylesheet"
        ),
        html.H1(
            children="Intervenciones Congreso de los Diputados",
            style={"textAlign": "center", "font-family": "Orbitron"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="politic",
                    options=[
                        {
                            "label": "Sánchez Pérez-Castejón, Pedro",
                            "value": "Sánchez Pérez-Castejón, Pedro",
                        },
                        {
                            "label": "Díaz Pérez, Yolanda",
                            "value": "Díaz Pérez, Yolanda",
                        },
                        {
                            "label": "Abascal Conde, Santiago",
                            "value": "Abascal Conde, Santiago",
                        },
                        {
                            "label": "García Egea, Teodoro",
                            "value": "García Egea, Teodoro",
                        },
                    ],
                    placeholder="Sánchez Pérez-Castejón, Pedro",
                    value="Sánchez Pérez-Castejón, Pedro",
                    style={"width": "45%"},
                ),
                dcc.Dropdown(
                    id="date",
                    options=[
                        {"label": "2019", "value": "2019"},
                        {"label": "2020", "value": "2020"},
                        {"label": "2021", "value": "2021"},
                        {"label": "2022", "value": "2022"},
                    ],
                    placeholder="2022",
                    value="2022",
                    style={"width": "40%", "padding-left": "7%"},
                ),
            ],
            style={"margin-left": "25%", "display": "flex"},
        ),
        html.Div(
            dcc.Input(
                id="query",
                type="text",
                autoComplete="off",
                placeholder="Haz una pregunta o consulta (e.g. quién debe pagar más)",
                className="input",
                style={
                    "margin-left": "25%",
                    "width": "50%",
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
    State("politic", "value"),
    State("date", "value"),
)
def update_news(value, n_clicks, politic, date):

    if n_clicks > 0:
        query = Translator.translate_sp_en_query(value)
        docs = reader.read_transcript(
            query,
            top_k_retr=10,
            politic=politic,
            date=date,
        )
        childrens = []
        for doc in docs:
            childrens.append(create_output(doc))
        return childrens

    return ""


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
