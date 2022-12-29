import pandas as pd
from tqdm import tqdm

from deep_translator import GoogleTranslator


class Translator:
    @staticmethod
    def translate_sp_en(contents: pd.Series) -> list:
        """_summary_
        :param contents: _description_
        :type contents: pd.Series
        :return: _description_
        :rtype: list
        """
        trans = []
        for content in tqdm(contents):
            trans.append(GoogleTranslator(source="es", target="en").translate(content))
        return trans
