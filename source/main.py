"""
This file, written by Andrew H. Pometta, is the main source file for the
equity_bot Reddit bot.  See README.md for more details.

Some of these tasks might be diverted into different files later.
"""

import praw
import os
from time import sleep

reddit = praw.Reddit(
    "equitybot", user_agent="script:equitybot:v0.2 (Andrew H. Pometta)")


#This function takes in a list of strings, running it through the bot and returning 
#a pair: the first element is the string output of the bot, and the second is 
#a boolean if monte carlo evaluation was used
def evaluate_range(inputs):
    command_str = "holdem-eval/holdem-eval"
    mc = False  # monte carlo simulation
    for r in inputs:
        command_str += ' ' + r

    res = os.system(command_str + " -t 3 1>o.txt 2>e.txt")
    if res > 0:  # some error occurred
        if res == 8:
            return ("range conflict", False)
        else:
            f = open("e.txt", 'r')
            stderr = f.read()
            f.close()
            return (stderr.split(':')[-1], False)
    f = open("o.txt", 'r')
    output = f.read()
    f.close()

    if output[-5:-1] == "--mc":  # timed out calculation
        os.system(command_str + " --mc -t 5 1>o.txt 2>e.txt")
        f = open("o.txt", 'r')
        output = f.read()
        f.close()
        mc = True

    return (output, mc)



# This function will almost certainly be split across multiple later to
# flesh out error checking, timing for large queries, etc.
def comment_reply(content):
    # first, prune ranges
    words = content.split()  # across newlines, tabs and spaces
    ranges, opts = [], []  # separate list references
    i = 0
    while i < len(words) and "/u/" not in words[i]:
        i += 1  # skip everything before the mention

    while i < len(words):
        if "/u/" in words[i]:
            pass  # skip the actual mention of the bot
        elif ':' in words[i]:
            opts.append(words[i])
        else:
            ranges.append(words[i])
        i += 1

    if len(ranges) == 0:
        return "No ranges specified."
    # run program and receive output.

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

    output, mc = evaluate_range(ranges)

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
    if mc:
        reply_str += "**Note:** original calculation timed out: Monte Carlo simulation used instead."
    return reply_str


def perform_some_action():
    sleep(3)

done = False
while not done:  # main progrm infinite loop
    for i in reddit.inbox.mentions(limit=10):
        if not i.new:
            break  # ignore read messages
        i.mark_read()
        # if i.author.name != "bromeatmeco":
        # continue  # while testing the bot, it will only reply to my queries
        i.reply(comment_reply(i.body))
    perform_some_action()  # to avoid querying API too much
