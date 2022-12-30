# -*- coding: utf-8 -*-
"""
Translate the tweets into English
"""
import logging
import pandas as pd
from configparser import ConfigParser
from tqdm import tqdm

from scripts import CONF_INI
from scraper.twitter import Twitter
from processing.translation import Translator
from preparation.data_manager import DataManager


def _main():
    try:
        cfg = ConfigParser()
        cfg.read(CONF_INI)
        in_dir = cfg["PATHS"]["data_clean"]
        out_dir = cfg["PATHS"]["data_trans"]
        manager = DataManager()
        files = manager.list_csv_files(in_dir)
        translator = Translator()
        for file in tqdm(files):
            name_file = manager.get_filename(file)
            data = pd.read_csv(file, sep=";")
            tweets = data[Twitter.TWEET]
            data[Twitter.TWEET_EN] = translator.translate_sp_en(tweets)
            data.dropna(inplace=True)
            data = data[data[Twitter.TWEET_EN] != ""]
            data.to_csv(out_dir + name_file, sep=";", index=False)

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
