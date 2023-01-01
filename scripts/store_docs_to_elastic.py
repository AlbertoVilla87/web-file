import logging
from configparser import ConfigParser

from scripts import CONF_INI
from modeling.haystack import DocumentStore
from preparation.data_manager import DataManager


def _main():
    try:

        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["PATHS"]["data_trans"]
        manager = DataManager()
        storage = DocumentStore(in_dir, manager)
        storage.document_store.delete_documents()
        storage.store_docs()

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
