import re
import nltk
import emoji
import pandas as pd
import unicodedata
from string import printable
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

class Cleaning:

    SIGN = "@[A-Za-z0-9]+"
    LINK = r"(?:\@|http?\://|https?\://|www)\S+"
    LANG = "es"
    STOP = stopwords.words("spanish")
    BIGRAMS_ATTR = "bigrams"
    FREQUENCY_ATTR = "frequency"
    YEAR = "year"

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
    def remove_hidden_characters(content: str) -> str:
        """_summary_
        :param content: _description_
        :type content: str
        :return: _description_
        :rtype: str
        """
        content = " ".join(word_tokenize(content))
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

    @staticmethod
    def add_year(dates: pd.Series) -> pd.Series:
        """_summary_
        :param dates: _description_
        :type dates: pd.Series
        :return: _description_
        :rtype:
        """
        dates = pd.to_datetime(dates)
        years = dates.dt.year
        return years

    @staticmethod
    def compute_date(date: str) -> str:
        """_summary_
        :param date: _description_
        :type date: str
        :return: _description_
        :rtype: str
        """
        date = pd.to_datetime(date)
        date = str(date.date())
        return date

    @staticmethod
    def compute_period(start_year: str, end_year: str) -> list:
        """_summary_
        :param start_year: _description_
        :type start_year: str
        :param end_year: _description_
        :type end_year: str
        :return: _description_
        :rtype: list
        """
        start_year, end_year = int(start_year), int(end_year)
        start = min([start_year, end_year])
        end = max([start_year, end_year])
        period = list(range(start, end + 1))
        return period

    @staticmethod
    def create_name_file(name: str):
        """_summary_
        :param name: _description_
        :type name: str
        """
        name = (
            unicodedata.normalize("NFKD", name)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
        name = name.lower()
        name = name.replace(" ", "").replace(",", "").replace("-", "_")
        return name

    @staticmethod
    def extrat_year(text: str):
        """_summary_
        :param text: _description_
        :type text: str
        """
        years = re.findall(r"2\d{3}", text, flags=re.IGNORECASE)
        if len(years) > 0:
            return years[0]
        else:
            return ""
