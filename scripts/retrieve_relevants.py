import os
import logging
import time
import pandas as pd
from configparser import ConfigParser
from subprocess import Popen, PIPE, STDOUT

from scripts import CONF_INI
from modeling.haystack import DocumentStore


def _main():
    try:

        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["PATHS"]["data_trans"]
        storage = DocumentStore(in_dir)
        storage.store_docs()
        

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
