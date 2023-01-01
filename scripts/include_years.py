# -*- coding: utf-8 -*-
"""
Add year to the profiles
"""
import logging
import pandas as pd
from configparser import ConfigParser
from tqdm import tqdm

from scripts import CONF_INI
from processing.clean import Cleaning
from scraper.twitter import Twitter
from preparation.data_manager import DataManager


def _main():
    try:
        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["PATHS"]["data_trans"]
        manager = DataManager()
        files = manager.list_csv_files(in_dir)
        cleaner = Cleaning()
        for file in tqdm(files):
            data = pd.read_csv(file, sep=";")
            dates = data[Twitter.DATE]
            data[Cleaning.YEAR] = cleaner.add_year(dates)
            data.to_csv(file, sep=";", index=False)

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
