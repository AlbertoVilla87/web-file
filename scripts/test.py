import logging
import pandas as pd


from modeling.extractive_qa import ExtractiveQA

pd.options.mode.chained_assignment = None


def _main():
    try:

        model_path = "minilm-uncased-squad2"
        qa_model = ExtractiveQA(model_path)
        profile = pd.read_csv("data/processed/translated/sanchezcastejon.csv", sep=";")
        test = qa_model.answer_from_profile_onnx(profile, "what do you want", "energy")

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
