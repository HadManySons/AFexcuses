import praw
import random
import logging
from logging.handlers import RotatingFileHandler
import time
import os

credsPassword = os.environ.get('AFE_PASSWORD')
credsUserName = os.environ.get('AFE_USERNAME')
credsClientSecret = os.environ.get('AFE_SECRET')
credsClientID = os.environ.get("AFE_ID")
credsUserAgent = os.environ.get("AFE_USERAGENT")
subreddit = os.environ.get("AFE_SUBREDDIT")
excuseFile = os.environ.get("AFE_EXCUSEFILE")

# Initialize a logging object and have some examples below from the Python
# Doc page

LOG_TIME_FORMAT = "%Y/%m/%d %H:%M:%S "

logger = logging.getLogger("AFexcuses Rotating Log")
logger.setLevel(logging.INFO)
    
# add a rotating handler
handler = RotatingFileHandler("AFexcuses.log", maxBytes=2048000, backupCount=25)
logger.addHandler(handler)

def print_and_log(text, error=False):
    print(text)
    if error:
        logger.error(time.strftime(LOG_TIME_FORMAT) + text)
    else:
        logger.info(time.strftime(LOG_TIME_FORMAT) + text)

print_and_log("Starting script")

#Try to login or sleep/wait until logged in, or exit if user/pass wrong
NotLoggedIn = True
while NotLoggedIn:
    try:
        reddit = praw.Reddit(
            user_agent=credsUserAgent.strip(),
            client_id=credsClientID.strip(),
            client_secret=credsClientSecret.strip(),
            username=credsUserName.strip(),
            password=credsPassword.strip())
        print_and_log("Logged in")
        NotLoggedIn = False
    except praw.errors.InvalidUserPass:
        print_and_log("Wrong username or password", error=True)
        exit(1)
    except Exception as err:
        print_and_log(str(err), error=True)
        time.sleep(5)

# vars
globalCount = 0
rAirForce = reddit.subreddit(subreddit)

print_and_log("Starting processing loop for subreddit: " + subreddit)

triggerWords = ['afexcuses!', 'afexcuse!']
def checkForReplies(comment_list, rAirForceComments):
    for comment in comment_list:
        if rAirForceComments.id in comment.body:
            print_and_log("Already processed comment: " + permlink + ", skipping")
            return True
    return False

while True:
    try:
        # stream all comments from /r/AirForce
        for rAirForceComments in rAirForce.stream.comments():
            globalCount += 1
            
            #If the post is older than about 5 months, ignore it and move on.
            if (time.time() - rAirForceComments.created) > 13148715:
                print("Post too old, continuing")
                continue

            print_and_log("\nComments processed since start of script: " + str(globalCount))
            print_and_log("Processing comment: " + rAirForceComments.id)

            # prints a link to the comment.
            permlink = "http://www.reddit.com" + rAirForceComments.permalink            
            print_and_log("Processing comment: " + permlink)

            # Check replies to make sure the bot hasn't responded yet
            rAirForceComments.refresh()
            rAirForceComments.replies.replace_more()
            if checkForReplies(rAirForceComments.replies.list(), rAirForceComments):
                continue

            formattedComment = rAirForceComments.body
            formattedComment = formattedComment.lower()

            if any(matches in formattedComment for matches in triggerWords):
                dalist = []
                with open(excuseFile, 'r') as f:
                    dalist = f.read().splitlines()
                print_and_log("Dropping an excuse on: " + str(rAirForceComments.author) + ". Comment ID: " +
                             rAirForceComments.id + " with " + str(len(dalist)) + " excuses loaded.\n")
                ExcuseReply = '^^You\'ve ^^spun ^^the ^^wheel ^^of ^^Air ^^Force ^^excuses, ' + \
                               '^^here\'s ^^your ^^prize:\n\n' \
                              + (dalist[random.randint(0, len(dalist) - 1)]) \
                              + "\n\n\n\n ^^[Source](https://github.com/HadManySons/AFexcuses)" \
                              + " ^^| ^^[Subreddit](https://www.reddit.com/r/AFExcuses)" \
                              + " ^^^^^^" + rAirForceComments.id

                rAirForceComments.reply(ExcuseReply)
                continue

    # what to do if Ctrl-C is pressed while script is running
    except KeyboardInterrupt:
        print_and_log("Exiting due to keyboard interrupt")
        exit(0)
    
    except Exception as err:
        print_and_log("Exception: " + str(err.with_traceback()))