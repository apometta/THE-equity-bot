"""
This file, written by Andrew H. Pometta, is the main source file for the 
equity_bot Reddit bot.  See README.md for more details.

Some of these tasks might be diverted into different files later.
"""

import praw
import os

reddit = praw.Reddit(
    "equitybot", user_agent="script:equitybot:v0.2 (Andrew H. Pometta)")


def perform_some_action():
    sleep(5)

done = False
while not done:
    perform_some_action()
    for i in reddit.inbox.mentions(limit=10):
        if not i.new:
            break
        i.mark_read()
