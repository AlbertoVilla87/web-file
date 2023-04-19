import pandas as pd
import PyPDF2
from tqdm import tqdm
from io import BytesIO
from urllib.request import Request, urlopen
from nltk.tokenize import sent_tokenize


from processing.translation import Translator
from processing.clean import Cleaning
from preparation.politics import Politics


class Transcripts(Politics):

    INTERPAGES = 15
    TRANS = "transcript"
    PAGE = "page"
    PAGES = "pages"
    URL = "url"
    INTER = "interventions"
    INTER_EN = "interventions_en"
    AUTHOR = "/Author"
    SUBJECT = "/Subject"
    TITLE = "/Title"
    META = "meta"
    TEXT = "content"
    TEXT_ES = "content_es"
    YEAR = "year"

    def __init__(self, transcript: dict):
        """_summary_
        :param transcripts: _description_
        :type transcripts: dict
        """
        self.transcript = transcript
        self.name = list(transcript.keys())[0]
        self.interventions = {}

    def read_write_interventions(self):
        """_summary_"""
        data = self._create_dataframe(self.transcript)
        self.interventions[self.name] = self._read_contents_pdf(data)

    def _read_contents_pdf(self, data: pd):
        """_summary_
        :param data: _description_
        :type data: pd
        """
        interconts = []
        urls = data[Transcripts.TRANS].unique()
        index = 0
        for url in tqdm(urls):
            pages = data.loc[data[Transcripts.TRANS] == url, Transcripts.PAGE].values
            reader = self._request_reader_pdf(url)
            info = reader.metadata
            title, subject, author = self._remove_clean_metadata(info)
            interpages = self._read_interventions(reader, pages)
            interventions = self._collect_interventions(interpages)
            interventions_en = self._translate_interventions(interventions)
            for index, page in enumerate(pages):
                for sub_index, sent in enumerate(interventions[index]):
                    interconts.append(
                        {
                            Transcripts.TEXT: interventions_en[index][sub_index],
                            Transcripts.META: {
                                Transcripts.TITLE: title,
                                Transcripts.SUBJECT: subject,
                                Transcripts.YEAR: Cleaning.extrat_year(subject),
                                Transcripts.AUTHOR: author,
                                Transcripts.URL: url,
                                Transcripts.PAGE: int(page),
                                Transcripts.TEXT_ES: sent,
                            },
                        }
                    )
        return interconts

    def _remove_clean_metadata(self, info: dict):
        """_summary_
        :param info: _description_
        :type info: dict
        """
        title = Cleaning.remove_hidden_characters(info[Transcripts.TITLE])
        subject = Cleaning.remove_hidden_characters(info[Transcripts.SUBJECT])
        author = Cleaning.remove_hidden_characters(info[Transcripts.AUTHOR])
        return title, subject, author

    def _read_interventions(self, reader: PyPDF2.PdfReader, pages: list):
        """_summary_
        :param reader: _description_
        :type reader: PyPDF2.PdfReader
        :param pages: _description_
        :type pages: list
        """
        interconts = []
        inters = self._inter_pages(pages, len(reader.pages))
        for inter in inters:
            content = []
            for page in inter:
                page = int(page)
                content.append(reader.pages[page - 1].extract_text())
            interconts.append(" ".join(content))
        return interconts

    def _create_dataframe(self, transcript: list) -> pd:
        """_summary_
        :param transcripts: _description_
        :type transcripts: list
        :return: _description_
        :rtype: pd
        """
        data = pd.DataFrame.from_dict({Transcripts.URL: list(transcript.values())[0]})
        data[[Transcripts.TRANS, Transcripts.PAGE]] = data[Transcripts.URL].str.split(
            "#page=", 1, expand=True
        )
        data[Transcripts.PAGE] = data[Transcripts.PAGE].astype(int)
        data.drop_duplicates(inplace=True)
        data.sort_values(by=[Transcripts.TRANS, Transcripts.PAGE], inplace=True)
        return data

    def _request_reader_pdf(self, url: str):
        """_summary_
        :param url: _description_
        :type url: str
        """
        req = Request(url, headers={"User-Agent": "XYZ/3.0"})
        remote_file = urlopen(req, timeout=10).read()
        remote_file_bytes = BytesIO(remote_file)
        reader = PyPDF2.PdfReader(remote_file_bytes)
        return reader

    def _collect_interventions(self, interpages: list):
        """_summary_
        :param contents: _description_
        :type contents: list
        """
        interconts = []
        for inter in interpages:
            interconts += self._search_sents(inter)
        return interconts

    def _translate_interventions(self, interventions: list):
        """_summary_
        :param interventions: _description_
        :type interventions: list
        """
        interventions_en = []
        for intervention in interventions:
            interventions_en.append(Translator.translate_sp_en(intervention))
        return interventions_en

    def _search_sents(self, inter: str):
        """_summary_
        :param inter: _description_
        :type inter: str
        """
        interconts, intercont = [], []
        collect = False
        sents = sent_tokenize(inter)
        for sent in sents:
            sent = Cleaning.remove_line_breaks(sent)
            if collect == False:
                if self._search_spec_inter(Transcripts.REGEX[self.name], sent):
                    collect = True
                    intercont.append(sent)
            else:
                if not Transcripts.INTER_REGEX.search(sent):
                    intercont.append(sent)
                else:
                    interconts.append(intercont)
                    collect = False
                    intercont = []
        if collect == True:
            interconts.append(intercont)
        return interconts

    def _search_spec_inter(self, regex: list, sent: str) -> bool:
        """_summary_
        :param regex: _description_
        :type regex: list
        :param sent: _description_
        :type sent: str
        """
        for regex_i in regex:
            if regex_i.search(sent):
                return True
        return False

    def _inter_pages(self, pages: list, max_page: int):
        """_summary_
        :param pages: _description_
        :type pages: list
        :param max_page: _description_
        :type max_page: int
        """
        interpages = []
        max_page -= 1
        for index in range(0, len(pages) - 1):
            max_window = pages[index] + Transcripts.INTERPAGES
            if index == max_page:
                max_window = max_page
            elif max_window >= pages[index + 1]:
                max_window = pages[index + 1]
            elif max_window > max_page:
                max_window = max_page
            interpages.append(list(range(pages[index], max_window)))
        max_window = pages[-1] + (Transcripts.INTERPAGES)
        if pages[-1] < max_page:
            interpages.append(list(range(pages[-1], min(max_window, max_page))))
        else:
            interpages.append([pages[-1]])
        return interpages
