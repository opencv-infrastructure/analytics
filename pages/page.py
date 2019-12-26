class Page:
    def build(self, pull_requests, pull_requests_retrospective):
        raise NotImplementedError()

    def save(self, path_to_page, path_to_resources):
        raise NotImplementedError()
