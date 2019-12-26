from pages import Page
from stats import HistoricalClosedOpenDistribution

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set()

INDEX_TEMPLATE = '\
Welcome to OpenCV pull requests statistics page!\n\
================================================\n\
Updated {}\n\
\n\
Current Pull Requests age distribution\n\
--------------------------------------\n\
.. image:: _static/total_age_distribution.png\n\
\n\
Pull Requests trend\n\
-------------------\n\
.. image:: _static/historical_changes.png\n\
\n\
Pages\n\
-----\n\
\n\
.. toctree::\n\
  :maxdepth: 3\n\
\n\
  {}\n \
'


class TitlePage(Page):
    def __init__(self, generation_datetime, pages):
        self._generation_datetime = generation_datetime
        self._historical_stat = HistoricalClosedOpenDistribution()
        self._pages = pages

    def build(self, pull_requests, pull_requests_retrospective):
        self._historical_stat.build(pull_requests_retrospective)

    def save(self, path_to_page, path_to_resources):
        plot_changes_distribution(
            self._historical_stat.data,
            f'{path_to_resources}/historical_changes.png'
        )
        with open(path_to_page, 'w') as index:
            index.write(INDEX_TEMPLATE.format(
                self._generation_datetime.replace('T', ' ') + ' UTC',
                '\n  '.join(self._pages)
            ))


def plot_changes_distribution(df: pd.DataFrame, img_path):
    df = df.sort_values('Date')
    df.reset_index(drop=True, inplace=True)
    palette = sns.xkcd_palette(['denim blue', 'medium green', 'red orange'])
    with sns.color_palette(palette):
        fig, ax = plt.subplots(figsize=(df.shape[0], 10))
        df.plot(ax=ax, rot=70, linewidth=3)
        ax.set_xticks(range(len(df.index)))
        ax.set_xticklabels(df['Date'])
        ax.set_ylabel('Pull Requests')
        fig.savefig(img_path, bbox_inches='tight')
