import tkinter as tk
import gmail
import settings
import threading
from datetime import datetime
from github_interface import GithubInterface


def change_button_states(active):
    state = 'normal' if active else 'disabled'
    refresh_button.config(state=state)
    send_button.config(state=state)


def log_message(text):
    message.configure(state='normal')
    time = datetime.now()
    time_trimmed = time.strftime('%Y-%m-%d %H:%M:%S')
    message.insert(tk.END, f"{time_trimmed}   {text}\n")
    message.configure(state='disabled')
    message.see(tk.END)


def async_github_fetch():
    github.fetch_updated_repos()

    for repo in github.repos:
        text = f"{repo.name} ({len(repo.gazers)} new gazers)"
        listbox.insert('end', text)
    log_message("Done fetching repositories!")
    change_button_states(True)


def refresh_repos():
    change_button_states(False)
    log_message("Fetching repos...")
    listbox.delete(0, 'end')
    github_fetch_thread = threading.Thread(target=async_github_fetch)
    github_fetch_thread.start()


def async_send_email():
    selected = listbox.curselection()
    for index, repo in enumerate(github.repos):
        if index not in selected:
            continue
        log_message(f"Repository: {repo.name}")
        for name, email in repo.gazers:
            log_message(f"Sending to \'{name}\' ({email})")
            email_text = settings.email_text.format(settings.gmail_user,
                                                    settings.gmail_user,
                                                    repo.name,
                                                    name,
                                                    repo.name,
                                                    repo.url)
            gmail.send_mail(email, email_text)
            github.mark_as_sent(repo.url, email)

    log_message("Saving sent emails...")
    github.save_data()
    log_message("Done sending emails!")
    refresh_repos()


def send_emails():
    change_button_states(False)
    send_email_thread = threading.Thread(target=async_send_email)
    send_email_thread.start()


github = GithubInterface()

master = tk.Tk()
master.title("GithubSurvey")

title_label = tk.Label(master, text="Github Repositories:")
refresh_button = tk.Button(master, text="Refresh", command=refresh_repos)

pw = tk.PanedWindow(master, orient=tk.VERTICAL)

# listbox + scrollbar
listbox_frame = tk.Frame(pw)
listbox_scrollbar = tk.Scrollbar(listbox_frame)
listbox = tk.Listbox(listbox_frame, yscrollcommand=listbox_scrollbar.set, selectmode=tk.EXTENDED)
listbox_scrollbar.config(command=listbox.yview)
listbox.pack(expand=tk.Y, side=tk.LEFT, fill=tk.BOTH)
listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
pw.add(listbox_frame)

# debug message box
message_frame = tk.Frame(pw)
message_scrollbar = tk.Scrollbar(message_frame)
message = tk.Text(message_frame, height=8, wrap=None, state='disabled')
message_scrollbar.config(command=message.yview)
message.pack(expand=tk.Y, side=tk.LEFT, fill=tk.BOTH)
message_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
pw.add(message_frame)

send_button = tk.Button(master, text="Send!", command=send_emails)

# pack everything
title_label.pack()
refresh_button.pack()
pw.pack(side=tk.TOP, expand=tk.Y, fill=tk.BOTH, pady=2, padx='2m')
send_button.pack()

title_label.after(0, refresh_repos)
master.mainloop()
