import os
from tqdm import tqdm
from haystack.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack.nodes.retriever import BM25Retriever
from haystack.nodes.reader.farm import FARMReader
from haystack.pipelines import ExtractiveQAPipeline

from preparation.data_manager import DataManager
from scraper.twitter import Twitter
from processing.clean import Cleaning
from processing.translation import Translator

# TODO: Entity Recognition for meta information

os.environ["TOKENIZERS_PARALLELISM"] = "true"


class DocumentStore:

    TEXT = "content"
    META = "meta"
    NAME = "name"
    DOC = "document"

    def __init__(self, dir_docs: str, manager: DataManager):
        """_summary_
        :param dir_docs: _description_
        :type dir_docs: str
        """
        self.document_store = ElasticsearchDocumentStore(return_embedding=True)
        self.dir_docs = dir_docs
        self.manager = manager

    def store_docs(self):
        """_summary_"""
        profiles = self.manager.read_profiles(self.dir_docs)
        for index, profile in enumerate(tqdm(profiles)):
            docs = [
                {
                    DocumentStore.TEXT: row[Twitter.TWEET_EN],
                    DocumentStore.META: {
                        Twitter.DATE: row[Twitter.DATE],
                        Cleaning.YEAR: row[Cleaning.YEAR],
                        Twitter.TWEET: row[Twitter.TWEET],
                        DocumentStore.NAME: self.manager.names[index],
                    },
                }
                for _, row in profile.drop_duplicates(
                    subset=Twitter.TWEET_EN
                ).iterrows()
            ]
            self.document_store.write_documents(docs, index=DocumentStore.DOC)


class Retriever:

    RET_TAG = "Retriever"
    TOP_K_TAG = "top_k"
    FILT_TAG = "filters"

    def __init__(self, store: DocumentStore):
        """_summary_
        :param store: _description_
        :type store: DocumentStore
        """
        self.retriever = BM25Retriever(document_store=store.document_store)

    def retrieve(
        self, query: str, top_k: int, candidates: list, start_year: str, end_year: str
    ):
        """_summary_
        :param query: _description_
        :type query: str
        :param top_k: _description_
        :type top_k: int
        :param candidates: _description_
        :type candidates: list
        :param start_year: _description_
        :type start_year: str
        :param end_year: _description_
        :type end_year: str
        :return: _description_
        :rtype: _type_
        """
        period = Cleaning.compute_period(start_year, end_year)
        docs = self.retriever.retrieve(
            query=query,
            top_k=top_k,
            filters={DocumentStore.NAME: candidates, Cleaning.YEAR: period},
        )
        docs_parsed = []
        for doc in docs:
            data = doc.to_dict()
            date = Cleaning.compute_date(data[DocumentStore.META][Twitter.DATE])
            docs_parsed.append(
                {
                    Twitter.TWEET: data[DocumentStore.META][Twitter.TWEET],
                    DocumentStore.NAME: data[DocumentStore.META][DocumentStore.NAME],
                    Twitter.DATE: date,
                }
            )
        return docs_parsed


class Reader:

    READ_TAG = "Reader"
    TOP_K_TAG = "top_k"
    ANSWERS_TAG = "answers"
    ANSWER_TAG = "answer"
    QUERY_TAG = "query"
    CONTEXT_TAG = "context"

    def __init__(self, model_path: str, store: DocumentStore):
        """_summary_
        :param model_path: _description_
        :type model_path: str
        :param store: _description_
        :type store: DocumentStore
        :param translator: _description_
        :type translator: Translator
        """
        self.reader = FARMReader(
            model_name_or_path=model_path,
            progress_bar=False,
            return_no_answer=False,
        )
        self.retriever = BM25Retriever(document_store=store.document_store)
        self.pipe = ExtractiveQAPipeline(self.reader, self.retriever)

    def read(
        self,
        query: str,
        top_k_retr: int,
        candidates: list,
        start_year: str,
        end_year: str,
    ):
        """_summary_
        :param query: _description_
        :type query: str
        :param top_k_retr: _description_
        :type top_k_retr: int
        :param candidates: _description_
        :type candidates: list
        :param start_year: _description_
        :type start_year: str
        :param end_year: _description_
        :type end_year: str
        """
        docs = []
        period = Cleaning.compute_period(start_year, end_year)
        filters = {DocumentStore.NAME: candidates, Cleaning.YEAR: period}
        params = {
            Retriever.RET_TAG: {
                Retriever.TOP_K_TAG: top_k_retr,
                Retriever.FILT_TAG: filters,
            },
            Reader.READ_TAG: {Reader.TOP_K_TAG: top_k_retr},
        }
        answers = self.pipe.run(query=query, params=params)
        for idx in range(top_k_retr):
            answer = Translator.translate_en_sp_query(
                answers[Reader.ANSWERS_TAG][idx].answer
            )
            date = Cleaning.compute_date(
                answers[Reader.ANSWERS_TAG][idx].meta[Twitter.DATE]
            )
            docs.append(
                {
                    Reader.ANSWER_TAG: answer,
                    Twitter.TWEET: answers[Reader.ANSWERS_TAG][idx].meta[Twitter.TWEET],
                    DocumentStore.NAME: answers[Reader.ANSWERS_TAG][idx].meta[
                        DocumentStore.NAME
                    ],
                    Twitter.DATE: date,
                }
            )
        return docs
