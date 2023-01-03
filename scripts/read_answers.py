import logging
from configparser import ConfigParser

from scripts import CONF_INI
from modeling.haystack import DocumentStore, Reader
from preparation.data_manager import DataManager
from processing.translation import Translator

# https://stackoverflow.com/questions/57234859/how-to-fill-elasticsearch-database-before-starting-webapp-with-docker-compose


def _main():
    try:

        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["PATHS"]["data_trans"]
        model_path = "minilm-uncased-squad2"
        query = "Por qué cerrar las centrales nucleares?"
        manager = DataManager()
        storage = DocumentStore(in_dir, manager)
        reader = Reader(model_path, storage)
        query = Translator.translate_sp_en_query(query)
        answers = reader.read(query, 10, ["Abascal"], "2009", "2022")

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
