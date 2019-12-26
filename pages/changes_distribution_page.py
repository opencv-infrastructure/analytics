from github_api.models import ChangeType
from pages import Page

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from stats import ChangesDistribution

sns.set()


class ChangesDistributionPage(Page):
    def __init__(self):
        self._changes_distribution = ChangesDistribution()

    def build(self, pull_requests, pull_requests_retrospective):
        self._changes_distribution.build(pull_requests)

    def save(self, path_to_page, path_to_resources):
        changes_distribution = self._changes_distribution.distribution
        additions = []
        deletions = []
        for category, changes in changes_distribution.items():
            additions.append(changes[ChangeType.Addition])
            deletions.append(changes[ChangeType.Deletion])
        df = pd.DataFrame({'Additions': additions,
                           'Deletions': deletions},
                          index=tuple(changes_distribution.keys()))
        plot_total_changes_distribution(
            df, f'{path_to_resources}/total_changes_distribution.png'
        )
        plot_relative_changes_distribution(
            df, f'{path_to_resources}/relative_changes_distribution.png'
        )
        plot_absolute_changes_distribution(
            df, f'{path_to_resources}/absolute_changes_distribution.png'
        )
        most_changing = df.idxmax(axis=0)
        most_deletes = df.loc[most_changing["Deletions"]]
        most_additions = df.loc[most_changing["Additions"]]
        most_changing = df.loc[df.sum(axis=1).idxmax(axis=0)]
        with open(path_to_page, 'w') as result_file:
            result_file.writelines((
                '# Changes distribution\n',
                '## Overview\n',
                f' - Most deletions refer to module: {most_deletes.name} with {most_deletes.Deletions} line deletions\n',
                f' - Most additions refer to module: {most_additions.name} with {most_additions.Additions} line additions\n',
                f' - Most changes refer to module: {most_changing.name} with {most_changing.Additions + most_changing.Deletions} line changes\n',
                '![Total changes distribution](_static/total_changes_distribution.png)\n',
                '## Changes distribution between the modules\n',
                '![Changes distribution between the modules](_static/relative_changes_distribution.png)\n',
                '## Changes distribution in absolute values\n',
                '![Changes distribution in absolute values](_static/absolute_changes_distribution.png)\n'
            ))


def plot_total_changes_distribution(df, img_path):
    total = pd.DataFrame({'Total': df.sum(axis=0)}).T
    relative_values = total.div(total.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(10, 3))
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, 1)
    with sns.color_palette(["#2ecc71", "#e74c3c"]):
        relative_values.plot(kind='barh', stacked=True, ax=ax)
    for patch, value in zip(ax.patches, total.values.flatten()):
        width, height = patch.get_width(), patch.get_height()
        if height > 0.05:
            x, y = patch.get_xy()
            ax.text(x + 0.5 * width, y + 0.5 * height,
                    '{0} ({1:.1%})'.format(value, width),
                    ha='center', va='center', color='white', fontsize=14)

    legend_anchor = (0., 0.911, 1., .102)
    legend_location = 'upper center'
    lgd = ax.legend(ncol=2, bbox_to_anchor=legend_anchor, loc=legend_location,
                    fontsize=12, mode='expand')
    fig.savefig(img_path, bbox_extra_artists=(lgd,), bbox_inches='tight')


def plot_relative_changes_distribution(df, img_path):
    normalized = df.copy(deep=True)
    normalized = normalized.div(normalized.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(normalized.shape[0], 10))
    ax.yaxis.set_visible(False)
    ax.set_ylim(0, 1)
    with sns.color_palette(["#2ecc71", "#e74c3c"]):
        normalized.plot(kind='bar', stacked=True, ax=ax, rot=70)
    ax.yaxis.set_visible(False)
    for patch, value in zip(ax.patches, df.values.flatten(order='F')):
        width, height = patch.get_width(), patch.get_height()
        if height > 0.08:
            x, y = patch.get_xy()
            if height > 0.2:
                label = '{0} ({1:.1%})'.format(value, height)
            else:
                label = '{0:.1%}'.format(height)
            ax.text(x + 0.5 * width, y + 0.5 * height, label,
                    ha='center', va='center', color='white', fontsize=14,
                    rotation=90)

    legend_anchor = (0., 0.99, 1., .102)
    legend_location = 'upper center'
    lgd = ax.legend(ncol=2, bbox_to_anchor=legend_anchor, loc=legend_location,
                    fontsize=12, mode='expand')
    fig.savefig(img_path, bbox_extra_artists=(lgd,), bbox_inches='tight')


def plot_absolute_changes_distribution(df, img_path):
    fig, ax = plt.subplots(figsize=(df.shape[0], 10))
    heights = df.sum(axis=1).sort_values(ascending=False)
    with sns.color_palette([sns.xkcd_rgb['denim blue']]):
        heights.plot(kind='bar', ax=ax, rot=70)
    max_height = heights.max()
    for patch in ax.patches:
        width, height = patch.get_width(), patch.get_height()
        x, y = patch.get_xy()
        ax.text(x + 0.5 * width, y + height + 0.02 * max_height, str(height),
                ha='center', va='center', fontsize=15)

    legend_anchor = (0., 0.99, 1., .102)
    legend_location = 'upper center'
    lgd = ax.legend(labels=('number of changed lines',),
                    ncol=1, bbox_to_anchor=legend_anchor, loc=legend_location,
                    fontsize=12, mode='expand')
    fig.savefig(img_path, bbox_extra_artists=(lgd,), bbox_inches='tight')
