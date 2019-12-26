from pages import Page
from stats import ProblematicPullRequests

REPLACE_TABLE = {
    '`': '',
    '### ': '',
    '## ': '',
    '<!--': '',
    '-->': '',
}


def cleanup(line: str):
    for old, new in REPLACE_TABLE.items():
        line = line.replace(old, new)
    return line


class ProblematicPullRequestsPage(Page):
    def __init__(self):
        self._stat = ProblematicPullRequests()

    def build(self, pull_requests, pull_requests_retrospective):
        self._stat.build(pull_requests)

    def save(self, path_to_page, path_to_resources):
        def write_pr(pr, add_descr=True):
            result_file.write(f' - [PR#{pr.number}]({pr.url}): {pr.title}\n\n')

            if add_descr:
                result_file.write(f'   __Description__:<br/>\n```\n')
                for line in pr.body.split('\n'):
                    result_file.write(f'{cleanup(line)}\n')
                result_file.write('```\n')

        with open(path_to_page, 'w') as result_file:
            result_file.writelines((
                '# Problematic pull requests\n',
                '## Stable reproducers\n'
            ))
            for reproducer in self._stat.reproducers:
                write_pr(reproducer)
            result_file.write('## WIP\n')

            for wip in self._stat.wip:
                write_pr(wip, False)

            for problem, pull_requests in self._stat.distribution.items():
                result_file.write(f'## Problem: {problem}\n')
                for pr in pull_requests:
                    write_pr(pr)
