import pandas as pd
import snscrape.modules.twitter as sntwitter
from tqdm import tqdm

from processing.clean import Cleaning


class Twitter(Cleaning):

    DATE = "date"
    LIKES = "likes"
    SOURCE = "source"
    TWEET = "tweet"
    TWEET_PARSED = "tweet_parsed"
    TWEET_EN = "tweet_en"

    def __init__(self, user: str, out_file: str, limit: int = 10e100):
        """_summary_
        :param user: user name
        :type user: str
        :param out_file: output file path
        :type out_file: str
        :param limit: number of tweets
        :type limit: int
        """
        self._user = user
        self._limit = limit
        self._out_file = out_file
        self._data = None

    def get_tweets(self):
        """_summary_"""
        data_info = []
        for index, tweet in tqdm(
            enumerate(sntwitter.TwitterSearchScraper("from:" + self._user).get_items())
        ):
            if index > self._limit:
                break
            data_info.append(
                [
                    tweet.date,
                    tweet.likeCount,
                    tweet.sourceLabel,
                    Twitter.remove_line_breaks(tweet.content),
                ]
            )

        self._data = pd.DataFrame(
            data_info,
            columns=[
                Twitter.DATE,
                Twitter.LIKES,
                Twitter.SOURCE,
                Twitter.TWEET,
            ],
        )

    def save_profile(self):
        """_summary_
        :return: _description_
        :rtype: _type_
        """
        self._data.to_csv(self._out_file, sep=";", index=False)

    @property
    def data(self):
        return self._data
