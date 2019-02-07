"""This file, which can be treated as the "main" file, is the .py responsible for interfacing with Reddit for THE-equity-bot.  Written by Andrew H. Pometta.  As of now, it is solely a skeleton of the project.  """

import datetime
import time
import praw
import sys

#de facto constants
PRAW_COMMENT = praw.models.reddit.comment.Comment
PRAW_SUBMISSION = praw.models.reddit.submission.Submission

def print_post(post, debug=False):
    if type(post) is not PRAW_COMMENT and type(post) is not PRAW_SUBMISSION:
        print("Error: post " + str(post) + " is neither comment nor submission.", file=sys.stderr)
        return
    print("id: " + post.id)
    print("author.name: " + post.author.name)
    if debug:
        print("permalink: " + post.permalink)
        print("created_utc (converted): " + str(datetime.datetime.fromtimestamp(post.created_utc)))
    if type(post) is PRAW_COMMENT:
        print("body: " + post.body, end="\n\n", flush=True)
    elif type(post) is PRAW_SUBMISSION:
        if post.is_self:
            print("selftext: " + post.selftext, flush=True)
        else:
            print("url: " + post.url, flush=True)

def main():
    """The main function of THE-equity-bot, it instantiates everything and begins to perform the bots function: monitor submissions, submissions and inbox messages, parse them for requests, and replies with equity analyses as needed."""
    #Set ups: Set up Reddit praw instance, subreddit (list), database handler,
    #logger, executable
    reddit = praw.Reddit('THE-equity-bot')
    subreddit = reddit.subreddit('askreddit')
    #post = reddit.submission(id="")
    #post = reddit.comment(id="efyp4y0")
    print_post(5, True)

    #Next: set up stream, check inbox, perform wake-up tests if needed.

    #Final: begin monitoring all comments/submissions/messages.  Loop until
    #shutdown sequence given.

    #Quitting: If shutdown sequence given or some other reason necessary to
    #fail out, finish all logging and db inquiries, clean up and quit.
    pass

if __name__ == "__main__":
    main()
