"""This file, which can be treated as the "main" file, is the .py responsible
for interfacing with Reddit for THE-equity-bot.  Written by Andrew H. Pometta.
As of now, it is solely a skeleton of the project.  """

import datetime
import time
import praw
import sys
import logging
import logging.config
import yaml

#de facto constants
PRAW_COMMENT = praw.models.reddit.comment.Comment
PRAW_SUBMISSION = praw.models.reddit.submission.Submission
CFG_PATH = "../config/" #change to your liking if forked.

def setup_logging():
    """Set up the logging configuration from the logging YAML file.  This sets
    up various loggers, by different names with different settings, to be used
    throughout the program.  If the logger cannot be created, the root logger
    is still configured.  While this functionality is not optimal - logs will
    not be written to a file - it will not break the program in any part,
    since named loggers will simply be children of the root logger."""
    #Root logger set up in case we need it
    logging.basicConfig(datefmt="%Y/%m/%d %H:%M:%S",
                    format="%(asctime)s:%(name)s:%(levelname)s:%(message)s")
    try:
        with open(CFG_PATH + "logging.yml", "rt") as log_yaml:
            log_config = yaml.safe_load(log_yaml)
        logging.config.dictConfig(log_config)
        #gather the logger from wherever you want in the program - it should
        #work with just the right name
        return
    except OSError as e:
        logging.error("Cannot open logging.yml; using root logger")
    except:
        logging.error("Unexpected error " + str(sys.exc_info()[0]) +
                      " configuring logging; using root logger")

def print_post(post, debug=False):
    """To be deprecated."""
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
    """The main function of THE-equity-bot, it instantiates everything and
    begins to perform the bots function: monitor submissions, submissions and
    inbox messages,  parse them for requests, and replies with equity analyses
    as needed."""
    #Set ups: Set up Reddit praw instance, subreddit (list), database handler,
    #executable
    reddit = praw.Reddit('THE-equity-bot')

    #Next: set up stream, check inbox, perform wake-up tests if needed.

    #Final: begin monitoring all comments/submissions/messages.  Loop until
    #shutdown sequence given.

    #Quitting: If shutdown sequence given or some other reason necessary to
    #fail out, finish all logging and db inquiries, clean up and quit.
    pass

if __name__ == "__main__":
    main()
