import os
import settings
import json
from github import Github
from collections import namedtuple


Repo = namedtuple('Repo', ['name', 'url', 'gazers'])


class GithubInterface(object):
    def __init__(self):
        self.data = {}
        self.load_data()
        self.repos = []
        self.gh = Github(settings.github_user, settings.github_pass)

    def fetch_updated_repos(self):
        self.load_data()
        self.repos.clear()
        all_repos = self.gh.get_user().get_repos(visibility='public')

        for repo in all_repos:
            new_stargazers = [gazer for gazer in repo.get_stargazers()
                              if gazer.email is not None
                              and (repo.html_url not in self.data
                              or gazer.email not in self.data[repo.html_url])]
            stargazer_info = [(gazer.name if gazer.name else gazer.login, gazer.email)
                               for gazer in new_stargazers]
            if len(new_stargazers) == 0:
                continue
            self.repos.append(Repo(repo.name, repo.html_url, stargazer_info))

    def mark_as_sent(self, repo_url, email):
        if repo_url not in self.data:
            self.data[repo_url] = []
        self.data[repo_url].append(email)

    def load_data(self):
        if os.path.isfile('data.json'):
            with open('data.json', 'r') as fp:
                self.data = json.load(fp)

    def save_data(self):
        with open('data.json', 'w') as fp:
            json.dump(self.data, fp, sort_keys=True, indent=4)
