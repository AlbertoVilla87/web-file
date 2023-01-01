from tqdm import tqdm
from haystack.document_stores.elasticsearch import ElasticsearchDocumentStore
from haystack.nodes.retriever import BM25Retriever

from preparation.data_manager import DataManager
from scraper.twitter import Twitter
from processing.clean import Cleaning

# TODO: Entity Recognition for meta information


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
