import glob
import os
import json
import pandas as pd
import ast
from configparser import ConfigParser

from scraper.twitter import Twitter

from scripts import CONF_INI


class DataManager:
    def __init__(self):
        """_summary_
        :return: _description_
        :rtype: _type_
        """
        cfg = ConfigParser()
        cfg.read(CONF_INI)
        self.names = ast.literal_eval(cfg["PROFILES"]["names"])
        self.accounts = ast.literal_eval(cfg["PROFILES"]["accounts"])
        self.trans_names = ast.literal_eval(cfg["TRANSCRIPTS"]["politics"])

    @staticmethod
    def read_profiles(dir: str) -> list:
        """_summary_
        :param dir: _description_
        :type dir: str
        :return: _description_
        :rtype: _type_
        """
        profiles = []
        files = DataManager.list_csv_files(dir)
        for file in files:
            profiles.append(pd.read_csv(file, sep=";"))
        return profiles

    @staticmethod
    def read_transcripts_urls(dir: str) -> list:
        """_summary_
        :param dir: _description_
        :type dir: str
        :return: _description_
        :rtype: _type_
        """
        transcripts = []
        files = DataManager.list_json_files(dir)
        for file in files:
            transcripts.append(DataManager.read_json_file(file))
        return transcripts

    @staticmethod
    def collect_keyword(profiles: list, keyword: str):
        """_summary_
        :param profiles: _description_
        :type profiles: list
        :param keyword: _description_
        :type keyword: str
        :return: _description_
        :rtype: _type_
        """
        profiles_kw = []
        empty_info = ["", "", "", "", "notweets"]
        profile_empty = pd.DataFrame([empty_info], columns=profiles[0].columns)
        for profile in profiles:
            profile_i = profile[profile[Twitter.TWEET_PARSED].str.contains(keyword)]
            if not profile_i.empty:
                profiles_kw.append(profile_i)
            else:
                profiles_kw.append(profile_empty)

        return profiles_kw

    @staticmethod
    def collect_period(profiles: list, start_date: str, end_date: str):
        """_summary_
        :param profiles: _description_
        :type profiles: list
        :param start_date: _description_
        :type start_date: str
        :param end_date: _description_
        :type end_date: str
        :return: _description_
        :rtype: _type_
        """
        profiles_kw = []
        for profile in profiles:
            pass
        return profiles_kw

    @staticmethod
    def list_csv_files(dir: str) -> list:
        """_summary_
        :param dir: _description_
        :type dir: str
        :return: _description_
        :rtype: list
        """
        files = []
        for file in glob.glob(dir + "*.csv"):
            files.append(file)
        return files

    @staticmethod
    def list_json_files(dir: str) -> list:
        """_summary_
        :param dir: _description_
        :type dir: str
        :return: _description_
        :rtype: list
        """
        files = []
        for file in glob.glob(dir + "*.json"):
            files.append(file)
        return files

    @staticmethod
    def get_filename(filename: str) -> str:
        """_summary_
        :param filename: _description_
        :type filename: _type_
        """
        base = os.path.basename(filename)
        return base

    @staticmethod
    def read_json_file(file):
        with open(file, encoding="utf-8") as json_file:
            json_file = json.load(json_file)
        return json_file

    @staticmethod
    def write_json(file: str, data: dict):
        """_summary_
        :param file: _description_
        :type file: str
        :param data: _description_
        :type data: dict
        """
        with open(file, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)
