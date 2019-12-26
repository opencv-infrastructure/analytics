from pages import Page
from stats import CategoriesDistribution

import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

sns.set()


class CategoriesDistributionPage(Page):
    def __init__(self):
        self._categories_distribution = CategoriesDistribution()

    def build(self, pull_requests, pull_requests_retrospective):
        self._categories_distribution.build(pull_requests)

    def save(self, path_to_page, path_to_resources):
        with open(path_to_page, 'w') as result_file:
            result_file.write('# Categories distribution\n')
            result_file.write('## Overview\n')
            d = {
                k: len(v)
                for k, v in self._categories_distribution.distribution.items()
            }
            df = pd.DataFrame.from_dict(d, orient='index')
            plot_distribution(df,
                              f'{path_to_resources}/categories_distribution.png',
                              self._categories_distribution.total_pull_requests)
            result_file.writelines((
                'Total percentage may exceed 100%, because several categories '
                'may be assigned to 1 pull request.\n '
                '![Categories distribution plot](_static/categories_distribution.png)\n'
            ))
            result_file.writelines((
                '## Pull requests with auto assigned categories\n',
                'Categories are assigned based on path of the changed '
                'files.\n\n '

            ))
            auto_assigned = self._categories_distribution.with_auto_assigned_categories
            for i, pr in enumerate(auto_assigned, 1):
                result_file.writelines((
                    f' - [PR#{pr.number}]({pr.url}): {pr.title}\n<br/>',
                    f'   __Assigned categories__: {pr.categories}\n',
                    '---\n' if i < len(auto_assigned) else ''
                ))


def plot_distribution(df, img_path, total_pull_requests):
    def annotate(patch, value):
        width, height = patch.get_width(), patch.get_height()
        x, y = patch.get_xy()
        ax.text(x + 0.5 * width, y + height + 0.02 * max_height,
                '{0:.1%}'.format(height / total_pull_requests),
                ha='center', va='center', fontsize=15)
        ax.text(x + 0.5 * width, y + 0.5 * height, str(value),
                ha='center', va='center', fontsize=16, color='white')

    fig, ax = plt.subplots(figsize=(df.shape[0], 10))
    heights = df.sort_values(by=0, ascending=False)
    with sns.color_palette([sns.xkcd_rgb['denim blue']]):
        heights.plot(kind='bar', ax=ax, rot=70)
    ax.set_yticks(heights.values)
    ax.set_yticklabels(map(str, heights.values.flatten()), fontdict={
        'fontsize': 16
    })
    max_height = heights.max()
    annotate(ax.patches[0], max_height[0])
    ax.patches[0].set_facecolor('red')
    for patch, value in zip(ax.patches[1:], heights.values[1:].flatten()):
        annotate(patch, value)

    fig.savefig(img_path, bbox_inches='tight')
