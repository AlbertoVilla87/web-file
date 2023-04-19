import pandas as pd
from typing import Union
from tqdm import tqdm

from deep_translator import GoogleTranslator


class Translator:
    @staticmethod
    def translate_sp_en(contents: Union[pd.Series, list]) -> list:
        """Spanish to English
        :param contents: _description_
        :type contents: Union[pd.Series, list]
        :return: _description_
        :rtype: list
        """
        trans = []
        for content in tqdm(contents):
            try:
                trans.append(
                    GoogleTranslator(source="es", target="en").translate(content)
                )
            except:
                trans.append("")
                pass
        return trans

    @staticmethod
    def translate_sp_en_query(query: str) -> str:
        """Spanish to English
        :param query: _description_
        :type query: str
        :return: _description_
        :rtype: str
        """
        return GoogleTranslator(source="es", target="en").translate(query)

    @staticmethod
    def translate_en_sp_query(query: str) -> str:
        """English to Spanish
        :param query: _description_
        :type query: str
        :return: _description_
        :rtype: str
        """
        try:
            return GoogleTranslator(target="es").translate(query)
        except:
            return query
