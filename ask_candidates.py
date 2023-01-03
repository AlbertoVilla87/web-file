import time
from dash import html, dcc, Dash
from dash.dependencies import Input, State, Output

from modeling.haystack import DocumentStore, Reader
from scraper.twitter import Twitter
from processing.translation import Translator

from preparation.data_manager import DataManager

from haystack.utils import launch_es

launch_es()
time.sleep(50)

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
                        doc[Reader.ANSWER_TAG],
                        html.Div(
                            doc[DocumentStore.NAME],
                            style={
                                "float": "right",
                                "color": "#9aa0a6",
                                "font-style": "italic",
                                "font-weight": "normal",
                            },
                        ),
                    ]
                ),
            ),
            html.Span(
                [
                    html.Span(doc[Twitter.DATE] + " - ", style={"color": "#9aa0a6"}),
                    html.Span(doc[Twitter.TWEET]),
                ]
            ),
        ],
        style={
            "margin-left": "32%",
            "font-family": "Open Sans, sans-serif",
            "width": "700px",
        },
    )
    return out


app = Dash(__name__)

app.layout = html.Div(
    [
        html.H1(
            children="Conoce a los políticos",
            style={"textAlign": "center", "font-family": "Open Sans, sans-serif"},
        ),
        html.Div(
            dcc.Checklist(
                id="candidates",
                options=[
                    {"label": "Sánchez", "value": "Sanchez"},
                    {"label": "Díaz", "value": "Diaz"},
                    {"label": "Abascal", "value": "Abascal"},
                    {"label": "Feijó", "value": "Feijo"},
                ],
                value=["Sanchez", "Diaz", "Abascal", "Feijo"],
                labelStyle={"display": "inline-block"},
            ),
            style={"textAlign": "center"},
        ),
        html.Div(
            [
                dcc.Dropdown(
                    id="start",
                    options=[
                        {"label": "2009", "value": "2009"},
                        {"label": "2010", "value": "2010"},
                        {"label": "2011", "value": "2011"},
                        {"label": "2012", "value": "2012"},
                        {"label": "2013", "value": "2013"},
                        {"label": "2014", "value": "2014"},
                        {"label": "2015", "value": "2015"},
                        {"label": "2016", "value": "2016"},
                        {"label": "2017", "value": "2017"},
                        {"label": "2018", "value": "2018"},
                        {"label": "2019", "value": "2019"},
                        {"label": "2020", "value": "2020"},
                        {"label": "2021", "value": "2021"},
                        {"label": "2022", "value": "2022"},
                    ],
                    placeholder="2009",
                    value="2009",
                    style={"width": "100px"},
                ),
                dcc.Dropdown(
                    id="end",
                    options=[
                        {"label": "2009", "value": "2009"},
                        {"label": "2010", "value": "2010"},
                        {"label": "2011", "value": "2011"},
                        {"label": "2012", "value": "2012"},
                        {"label": "2013", "value": "2013"},
                        {"label": "2014", "value": "2014"},
                        {"label": "2015", "value": "2015"},
                        {"label": "2016", "value": "2016"},
                        {"label": "2017", "value": "2017"},
                        {"label": "2018", "value": "2018"},
                        {"label": "2019", "value": "2019"},
                        {"label": "2020", "value": "2020"},
                        {"label": "2021", "value": "2021"},
                        {"label": "2022", "value": "2022"},
                    ],
                    placeholder="2022",
                    value="2022",
                    style={"width": "100px"},
                ),
            ],
            style={"margin-left": "37%", "display": "flex"},
        ),
        html.Div(
            dcc.Input(
                id="query",
                type="text",
                placeholder="Haz una pregunta o consulta",
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
    State("candidates", "value"),
    State("start", "value"),
    State("end", "value"),
)
def update_news(value, n_clicks, candidates, start_year, end_year):

    if n_clicks > 0:
        query = Translator.translate_sp_en_query(value)
        docs = reader.read(
            query,
            top_k_retr=10,
            candidates=candidates,
            start_year=start_year,
            end_year=end_year,
        )
        childrens = []
        for doc in docs:
            childrens.append(create_output(doc))
        return childrens

    return ""


if __name__ == "__main__":
    app.run_server()
