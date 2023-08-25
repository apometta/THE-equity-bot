"""
This file, written by Andrew H. Pometta, is the main source file for the
equity_bot Reddit bot.  See README.md for more details.

Some of these tasks might be diverted into different files later.
"""

import praw
import os

reddit = praw.Reddit(
    "equitybot", user_agent="script:equitybot:v0.2 (Andrew H. Pometta)")


# This function will almost certainly be split across multiple later to
# flesh out error checking, timing for large queries, etc.
def comment_reply(content):
    # first, prune ranges
    words = content.split()  # across newlines, tabs and spaces
    ranges, opts = [], []  # separate list references
    for i in words:
        if "/u/" in i:
            continue  # skip the actual mention of the bot
        if ':' in i:
            opts.append(i)
        else:
            ranges.append(i)

    if len(ranges) == 0:
        return "help message"
    # run program and receive output.
    command_str = "holdem-eval/holdem-eval"

    for i in opts:
        pre, post = i.split(':')
        if len(pre) == 0 or len(post) == 0:
            return "invalid option"
        if pre[0] == 'b':
            command_str += " -b " + post
        elif pre[0] == 'd':
            command_str += " -d " + post
        else:
            return "invalid option"

    for r in ranges:
        command_str += ' ' + r
    os.system(command_str + " 1>o.txt 2>e.txt")
    f = open("o.txt", 'r')
    output = f.read()
    f.close()

    # parse output
    if len(output) <= 1:  # there was an error piped to e.txt
        print("Error")
        return "Error"
    equities = output.split("***")[1].strip().split('\n')
    reply_str = "Range|Equity\n:--|--:\n"
    for i in equities:
        player, eq = i.split(':')
        player, eq = player.strip(), eq.strip()
        reply_str += player + '|' + eq + '\n'
    return reply_str


def perform_some_action():
    sleep(5)

done = False
while not done:  # main progrm infinite loop
    for i in reddit.inbox.mentions(limit=10):
        if not i.new:
            break  # ignore read messages
        i.mark_read()
        if i.author.name != "bromeatmeco":
            continue  # while testing the bot, it will only reply to my queries
        i.reply(comment_reply(i.body))

    print("Performed cycle")
    # perform_some_action()  # to avoid querying API too much
    done = True  # while testing, we will only run the bot once instead of continually checking
