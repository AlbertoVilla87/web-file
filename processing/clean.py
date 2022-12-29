import re
import nltk
import emoji
import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class Cleaning:

    SIGN = "@[A-Za-z0-9]+"
    LINK = r"(?:\@|http?\://|https?\://|www)\S+"
    LANG = "es"
    STOP = stopwords.words("spanish")
    BIGRAMS_ATTR = "bigrams"
    FREQUENCY_ATTR = "frequency"

    @staticmethod
    def remove_line_breaks(content: str) -> str:
        """_summary_
        :param content: _description_
        :type content: str
        :return: _description_
        :rtype: str
        """
        content = " ".join(content.split())
        return content

    @staticmethod
    def clean_tweets(contents: pd.Series) -> list:
        """_summary_
        :param data: _description_
        :type data: pd.Series
        :return: _description_
        :rtype: pd
        """
        return contents.apply(Cleaning.cleaner)

    @staticmethod
    def cleaner(content: str) -> str:
        """_summary_
        :param content: _description_
        :type content: str
        :return: _description_
        :rtype: str
        """
        content = content.lower()
        content = re.sub(Cleaning.SIGN, "", content)
        content = re.sub(Cleaning.LINK, "", content)
        content = content.replace("#", "")
        content = emoji.demojize(content, language=Cleaning.LANG)
        content = content.replace("_", " ").replace(":", " ")
        content = " ".join(
            [
                word
                for word in content.split()
                if (word not in Cleaning.STOP) & (word.isalpha())
            ]
        )
        return content

    @staticmethod
    def compute_freq_bigrams(docs: pd.Series, top_words: int) -> pd:
        """
        Compute bigram frequency from a list of docs
        :param docs: list of docs
        :type docs: pd.Series
        :param top_words: top N words to return
        :type top_words: int
        :return: words vs frequency
        :rtype: pd
        """
        words = word_tokenize(" ".join(docs.values))
        bigram_freq = nltk.FreqDist(nltk.bigrams(words)).most_common(top_words)
        bigram_freq = pd.DataFrame(bigram_freq)
        bigram_freq.columns = [
            Cleaning.BIGRAMS_ATTR,
            Cleaning.FREQUENCY_ATTR,
        ]
        return bigram_freq
