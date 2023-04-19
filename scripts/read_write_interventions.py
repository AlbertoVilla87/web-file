# -*- coding: utf-8 -*-
"""
Read transcripts from Congreso de Diputados
"""
import logging
from configparser import ConfigParser
import warnings

from scripts import CONF_INI
from processing.transcripts import Transcripts
from processing.clean import Cleaning
from preparation.data_manager import DataManager

warnings.filterwarnings("ignore")


def _main():
    try:
        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["TRANSCRIPTS"]["dir_raw"]
        out_dir = cfg["TRANSCRIPTS"]["dir_processed"]
        manager = DataManager()
        transcript = manager.read_json_file(in_dir + "sanchezperez_castejonpedro.json")
        transcriptor = Transcripts(transcript)
        transcriptor.read_write_interventions()
        out_file = out_dir + Cleaning.create_name_file(transcriptor.name) + ".json"
        DataManager.write_json(out_file, transcriptor.interventions)

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
