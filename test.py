import settings
from github import Github


g = Github(settings.user, settings.password)

print("Projects with stargazers: ")
for repo in g.get_user().get_repos(visibility='public'):
    stargazers = repo.get_stargazers()
    if not stargazers.totalCount: continue
    
    print(repo.name)
    for gazer in stargazers:
        print(f"[{gazer.login}] {gazer.name}: {gazer.email}")
    print("-------------------")