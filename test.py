import os
import settings
import json
from github import Github

# load configs if they exist
data = {}
excluded = []
data_exists = os.path.isfile('data.json')
if data_exists:
    with open('data.json', 'r') as fp:
        data = json.load(fp)
excluded_exists = os.path.isfile('excluded.json')
if excluded_exists:
    with open('excluded.json', 'r') as fp:
        excluded = json.load(fp)

# initialize Github API
gh = Github(settings.user, settings.password)

print("Projects with new stargazers: ")
repos = gh.get_user().get_repos(visibility='public')
for repo in repos:
    if repo.html_url not in data:
        data[repo.html_url] = []

    stargazers = [gazer for gazer in repo.get_stargazers()
                  if gazer.email is not None
                  and gazer.email not in data[repo.html_url]]

    if len(stargazers) == 0:
        continue

    print(f"- {repo.name} {repo.html_url} ({len(stargazers)} new stargazers)")
    should_include = input("    Should this repo be included? (y/n) ").lower()
    while should_include not in ["y", "n"]:
        should_include = input("    Should this repo be included? (y/n) ").lower()
    if should_include == "n":
        excluded.append(repo.html_url)
        continue

    for gazer in stargazers:
        recipient_name = gazer.name if gazer.name is not None else gazer.login
        print(f"   Sending email to {gazer.email}: {recipient_name}")
        email_text = f"Hi {recipient_name}!\n\n" + \
                     f"I noticed you gave my project \'{repo.name}\' ({repo.html_url}) a star on Github. " \
                     "First of all: thank you for that! :)\n" \
                     "I would like to improve the project by taking into consideration " \
                     "your specific needs and wishes.\n" \
                     "That is why I would greatly appreciate it if you could send me a " \
                     "short reply with some information about yourself, why you gave " \
                     "a star to the project or features you would like to see included " \
                     "in the future.\n" \
                     "I am also open to discuss other follow up projects or good ideas " \
                     "that you might have. So just hit me up!\n\n" \
                     "Cheers\n" \
                     "Rafael Kübler da Silva (https://github.com/RafaelKuebler)"
        data[repo.html_url].append(gazer.email)

# store emails sent out and excluded repos
with open('data.json', 'w') as fp:
    json.dump(data, fp, sort_keys=True, indent=4)
with open('excluded.json', 'w') as fp:
    json.dump(excluded, fp, sort_keys=True, indent=4)
