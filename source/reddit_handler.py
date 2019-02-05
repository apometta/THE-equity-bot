"""This file, which can be treated as the "main" file, is the .py responsible
for interfacing with Reddit for THE-equity-bot.  Written by Andrew H. Pometta.
As of now, it is solely a skeleton of the project.  """

def main():
    """The main function of THE-equity-bot, it instantiates everything and
    begins to perform the bots function: monitor comments, submissions and
    inbox messages, parse them for requests, and replies with equity
    analyses as needed."""
    #Set ups: Set up Reddit praw instance, subreddit (list), database handler,
    #logger, executable

    #Next: set up stream, check inbox, perform wake-up tests if needed.

    #Final: begin monitoring all comments/submissions/messages.  Loop until
    #shutdown sequence given.

    #Quitting: If shutdown sequence given or some other reason necessary to
    #fail out, finish all logging and db inquiries, clean up and quit.
    pass

if __name__ == "__main__":
    main()
