import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

from pages import Page
from stats import AgeDistribution, HistoricalAgeDistribution

sns.set()


class AgeDistributionPage(Page):
    def __init__(self):
        self._age_distribution_stat = AgeDistribution()
        self._historical_age_distribution = HistoricalAgeDistribution()

    def build(self, pull_requests, pull_requests_retrospective):
        self._age_distribution_stat.build(pull_requests)
        self._historical_age_distribution.build(pull_requests_retrospective)

    def save(self, path_to_page, path_to_resources):
        plot_total_age_distribution(
            self._age_distribution_stat.ages_distribution,
            f'{path_to_resources}/total_age_distribution.png'
        )
        plot_categories_age_distribution(
            self._age_distribution_stat.distribution,
            f'{path_to_resources}/categories_age_distribution.png'
        )
        plot_historical_age_distribution(
            self._historical_age_distribution.distribution,
            f'{path_to_resources}/historical_age_distribution.png'
        )
        ages = np.array([
            pr.age
            for prs in self._age_distribution_stat.ages_distribution.values()
            for pr in prs
        ])
        with open(path_to_page, 'w') as result_file:
            result_file.writelines((
                '# Age distribution\n',
                '## Overview\n',
                f' - Average age of the pull requests: {int(np.mean(ages))} days\n',
                f' - Median age of the pull requests: {int(np.median(ages))} days\n\n',
                '### Current age distribution\n',
                '![Age distribution](_static/total_age_distribution.png)\n',
                '### Historical age distribution\n',
                '![Historical age distribution](_static/historical_age_distribution.png)\n',
                '## Age distribution by categories\n',
                '![Age distribution by categories](_static/categories_age_distribution.png)\n',
                '## Age distribution by age categories\n'
            ))
            for category, prs in self._age_distribution_stat.ages_distribution.items():
                result_file.write(f'### Pull Requests with age: {category}\n')
                for i, (pr, age) in enumerate(prs, 1):
                    result_file.writelines((
                        f' - [PR#{pr.number}]({pr.url}): {pr.title}\n<br/>',
                        f'   __Age__: {age} day{"s" if age > 1 else ""}<br/>\n',
                        f'   __Labels__: {list(map(str, pr.labels))}<br/>\n',
                        f'   __Categories__: {pr.categories}\n',
                        '---\n' if i < len(prs) else ''
                    ))


def plot_historical_age_distribution(age_distribution, img_path):
    df = pd.DataFrame.from_dict({
        date: {category: len(prs) for category, prs in age_categories.items()}
        for date, age_categories in age_distribution.items()
    }, orient='index')
    df = df.reindex(index=df.index[::-1])
    df = df[reversed(list(df.columns))]
    with sns.color_palette('RdYlGn', df.shape[1]):
        fig, ax = plt.subplots(figsize=(df.shape[0], 10))
        ax.set_ylabel('Pull Requests')
        df.plot(kind='area', ax=ax)
        fig.savefig(img_path, bbox_inches='tight')


def plot_total_age_distribution(age_distribution, img_path):
    df = pd.DataFrame.from_dict({
        category: len(prs) for category, prs in age_distribution.items()
    }, orient='index')
    df = df.reindex(index=df.index[::-1])
    df.set_axis(['Pull Requests', ], axis=1, inplace=True)
    fig, ax = plt.subplots(figsize=(10, 3))
    with sns.color_palette('RdYlGn', df.shape[0]):
        df.T.plot(kind='barh', stacked=True, ax=ax)
    for patch, value in zip(ax.patches, df.values.flatten()):
        width, height = patch.get_width(), patch.get_height()
        r, g, b, _ = patch.get_facecolor()
        text_color = 'white' if r * g * b < 0.5 else 'black'
        if height > 0.05:
            x, y = patch.get_xy()
            ax.text(x + 0.5 * width, y + 0.5 * height,
                    '{0}'.format(value),
                    ha='center', va='center', color=text_color, fontsize=14)

    legend_anchor = (0., 0.911, 1., .102)
    legend_location = 'upper center'
    lgd = ax.legend(ncol=df.shape[0], bbox_to_anchor=legend_anchor,
                    loc=legend_location, fontsize=10, mode='expand')
    fig.savefig(img_path, bbox_extra_artists=(lgd,), bbox_inches='tight')


def plot_categories_age_distribution(age_distribution, img_path):
    df = pd.DataFrame.from_dict({
        category: {age_category: len(prs) for age_category, prs in
                   prs_distr.items()}
        for category, prs_distr in age_distribution.items()

    }, orient='index')
    df = df[reversed(list(df.columns))]
    normalized = df.copy(deep=True)
    normalized = normalized.div(normalized.sum(axis=1), axis=0)
    fig, ax = plt.subplots(figsize=(normalized.shape[0], 10))
    ax.yaxis.set_visible(False)
    ax.set_ylim(0, 1)
    with sns.color_palette('RdYlGn', df.shape[1]):
        normalized.plot(kind='bar', stacked=True, ax=ax, rot=70)
    ax.yaxis.set_visible(False)
    for patch, value in zip(ax.patches, df.values.flatten(order='F')):
        width, height = patch.get_width(), patch.get_height()
        r, g, b, _ = patch.get_facecolor()
        text_color = 'white' if r * g * b < 0.5 else 'black'
        if height > 0.05:
            x, y = patch.get_xy()
            ax.text(x + 0.5 * width, y + 0.5 * height,
                    '{0}'.format(value), ha='center', va='center',
                    color=text_color, fontsize=14)

    legend_anchor = (0., 0.99, 1., .102)
    legend_location = 'upper center'
    lgd = ax.legend(ncol=df.shape[1], bbox_to_anchor=legend_anchor,
                    loc=legend_location, fontsize=10, mode='expand')
    fig.savefig(img_path, bbox_extra_artists=(lgd,), bbox_inches='tight')
