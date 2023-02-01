# -*- coding: utf-8 -*-
"""
Retrieve transcripts from Congreso de Diputados
"""
import logging
from configparser import ConfigParser
from tqdm import tqdm

from scripts import CONF_INI
from scraper.gob import GobTranscripts
from preparation.data_manager import DataManager


def _main():
    try:
        cfg = ConfigParser()
        cfg.read(CONF_INI)
        out_file = cfg["TRANSCRIPTS"]["dir_raw"]
        name = "García Egea, Teodoro"
        scraper = GobTranscripts(out_file, name)
        scraper.extract_pdf_transcripts()

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
