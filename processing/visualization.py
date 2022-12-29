import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx

from scraper.twitter import Twitter
from processing.clean import Cleaning


class Visual:
    @staticmethod
    def create_wordcloud(profiles: list, names: list, keyword: str):
        """_summary_
        :param profiles: _description_
        :type profiles: list
        :param names: _description_
        :type names: list
        :param keyword: _description_
        :type keyword: str
        """
        fig, ax = plt.subplots(2, 2, figsize=(12.5, 6.5))
        fig.suptitle(keyword, fontsize=16)
        row, col = 0, 0
        for index, profile in enumerate(profiles):
            words = profile[Twitter.TWEET_PARSED].str.cat(sep=" ")
            wordcloud = WordCloud().generate(words)
            _ = ax[row][col].imshow(wordcloud, interpolation="bilinear")
            ax[row][col].set_title(names[index])
            row = row + 1
            if row == 2:
                row = 0
                col = col + 1

    @staticmethod
    def word_net(profiles: list, names: list, top_words: int, keyword: str):
        """_summary_
        :param profiles: _description_
        :type profiles: list
        :param names: _description_
        :type names: list
        :param top_words: _description_
        :type top_words: int
        :param keyword: _description_
        :type keyword: str
        """
        fig, ax = plt.subplots(2, 2, figsize=(12.5, 6.5))
        fig.suptitle(keyword, fontsize=16)
        row, col = 0, 0
        for index, profile in enumerate(profiles):
            docs = profile[Twitter.TWEET_PARSED]
            bigrams_freq = Cleaning.compute_freq_bigrams(docs, top_words)
            d = bigrams_freq.set_index(Cleaning.BIGRAMS_ATTR).T.to_dict("records")
            G = nx.Graph()
            for k, v in d[0].items():
                G.add_edge(k[0], k[1], weight=(v * 10))
            pos = nx.fruchterman_reingold_layout(G, k=5, seed=50)
            nx.draw_networkx(
                G,
                pos,
                arrows=True,
                font_size=2,
                width=2,
                edge_color="#595959",
                node_color="#CDC9A5",
                alpha=0.8,
                node_size=[len(v) * 10**2 for v in G.nodes()],
                with_labels=False,
                connectionstyle="arc3,rad=0.1",
                ax=ax[row][col],
            )
            for key, value in pos.items():
                x, y = value[0], value[1]
                ax[row][col].text(
                    x,
                    y,
                    s=key,
                    bbox=dict(facecolor="black", alpha=0),
                    horizontalalignment="center",
                    fontsize=8,
                )
            ax[row][col].set_title(names[index])
            row = row + 1
            if row == 2:
                row = 0
                col = col + 1
