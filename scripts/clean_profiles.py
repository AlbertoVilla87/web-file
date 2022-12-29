# -*- coding: utf-8 -*-
"""
Clean tweets of the profiles
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
        in_dir = cfg["PATHS"]["data"]
        out_dir = cfg["PATHS"]["data_clean"]
        manager = DataManager()
        files = manager.list_csv_files(in_dir)
        cleaner = Cleaning()
        for file in tqdm(files):
            name_file = manager.get_filename(file)
            data = pd.read_csv(file, sep=";")
            tweets = data[Twitter.TWEET]
            data[Twitter.TWEET_PARSED] = cleaner.clean_tweets(tweets)
            data.dropna(inplace=True)
            data = data[data[Twitter.TWEET_PARSED] != ""]
            data.to_csv(out_dir + name_file, sep=";", index=False)

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
