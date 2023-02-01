import logging
import warnings
from configparser import ConfigParser

from scripts import CONF_INI
from modeling.haystack import DocumentStore
from preparation.data_manager import DataManager

warnings.filterwarnings("ignore")


def _main():
    try:

        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["TRANSCRIPTS"]["dir_processed"]
        manager = DataManager()
        storage = DocumentStore(in_dir, manager)
        storage.document_store.delete_documents()
        transcript = manager.read_json_file(in_dir + "sanchezperez_castejonpedro.json")
        storage.store_transcripts(transcript)

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
