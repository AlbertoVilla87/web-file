# -*- coding: utf-8 -*-
"""
Retrieve tweets from an specific user
"""
import logging
from configparser import ConfigParser

from scripts import CONF_INI
from scraper.twitter import Twitter
from preparation.data_manager import DataManager


def _main():
    try:
        cfg = ConfigParser()
        cfg.read(CONF_INI)
        out_dir = cfg["PATHS"]["data"]
        manager = DataManager()
        for user in manager.accounts:
            out_file = out_dir + user + ".csv"
            profile = Twitter(user, out_file)
            profile.get_tweets()
            profile.save_profile()

    except Exception:  # pylint: disable=broad-except
        logging.exception("Process failed")


if __name__ == "__main__":
    _main()
