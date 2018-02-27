import praw
import sqlite3
from pathlib import Path
import random
import logging
import time
import os
import sys
from BotCreds import credsPassword, credsUserName, credsClientSecret, credsClientID, credsUserAgent

# Initialize a logging object and have some examples below from the Python
# Doc page
logging.basicConfig(filename='AFexcuses.log', level=logging.INFO)

#Get the PID of this process
pid = str(os.getpid())
pidfile = "AFexcuses.pid"

#Exit if a version of the script is already running
if os.path.isfile(pidfile):
    print(pidfile + " already running, exiting")
    sys.exit()

#Create the lock file for the script
open(pidfile, 'w').write(pid)

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") + "Starting script")

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
        print("Logged in")
        NotLoggedIn = False
    except praw.errors.InvalidUserPass:
        print("Wrong username or password")
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ") + "Wrong username or password")
        exit(1)
    except Exception as err:
        print(str(err))
        time.sleep(5)

# vars
globalCount = 0
dbFile = Path("ExcusesCommentRecord.db")

# check to see if database file exists
if dbFile.is_file():
    # connection to database file
    conn = sqlite3.connect("ExcusesCommentRecord.db")
    # database cursor object
    dbCommentRecord = conn.cursor()
else:  # if it doesn't, create it
    conn = sqlite3.connect("ExcusesCommentRecord.db")
    dbCommentRecord = conn.cursor()
    dbCommentRecord.execute('''CREATE TABLE comments(comment text)''')

# subreddit instance of /r/AirForce. 'AFexcuses' must be changed to 'airforce' for a production version of the
# script.
#subreddit = 'airforce+airnationalguard+afrotc'
subreddit = 'AFexcuses'
rAirForce = reddit.subreddit(subreddit)

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
             "Starting processing loop for subreddit: " + subreddit)

triggerWords = ['afexcuses!', 'afexcuse!']

while True:
    try:
        # stream all comments from /r/AirForce
        for rAirForceComments in rAirForce.stream.comments():
            globalCount += 1
            print("\nComments processed since start of script: " + str(globalCount))
            print("Processing comment: " + rAirForceComments.id)

            # prints a link to the comment.
            permlink = "http://www.reddit.com" + \
                rAirForceComments.permalink + "/"
            print(permlink)
            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                         "Processing comment: " + permlink)

            # Pulls all comments previously commented on
            dbCommentRecord.execute(
                "SELECT * FROM comments WHERE comment=?", (rAirForceComments.id,))

            id_exists = dbCommentRecord.fetchone()

            # Make sure we don't reply to the same comment twice or to the bot
            # itself
            if id_exists:
                print("Already processed comment: " +
                      str(rAirForceComments.id) + ", skipping")
                continue
            elif rAirForceComments.author == "AFexcuses":
                print("Author was the bot, skipping...")
                continue
            else:
                formattedComment = rAirForceComments.body
                formattedComment = formattedComment.lower()

                # A little extra something
                if any(matches in formattedComment for matches in triggerWords):
                    dalist = []
                    with open('Excuses.txt', 'r') as f:
                        dalist = f.read().splitlines()
                    print("Dropping an excuse on: " + str(rAirForceComments.author)
                          + ". Comment ID: " + rAirForceComments.id + " with " + str(len(dalist)) + " excuses loaded.")
                    logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                                 "Dropping an excuse on: " + str(rAirForceComments.author) + ". Comment ID: " +
                                 rAirForceComments.id + " with " + str(len(dalist)) + " excuses loaded.\n")
                    ExcuseReply = '^^You\'ve ^^spun ^^the ^^wheel ^^of ^^Air ^^Force ^^excuses, ' + \
                                   '^^here\'s ^^your ^^prize:\n\n' \
                                  + (dalist[random.randint(0, len(dalist) - 1)]) \
                                  + "\n\n\n\n ^^[Source](https://github.com/HadManySons/AFexcuses)" \
                                  + " ^^| ^^[Subreddit](https://www.reddit.com/r/AFExcuses)"

                    rAirForceComments.reply(ExcuseReply)
                    dbCommentRecord.execute(
                        'INSERT INTO comments VALUES (?);', (rAirForceComments.id,))
                    conn.commit()
                    continue

    # what to do if Ctrl-C is pressed while script is running
    except KeyboardInterrupt:
        print("Keyboard Interrupt experienced, cleaning up and exiting")
        conn.commit()
        conn.close()
        print("Exiting due to keyboard interrupt")
        logging.info(time.strftime("%Y/%m/%d %H:%M:%S ")
                    + "Exiting due to keyboard interrupt")
        exit(0)
    
    except Exception as err:
        print("Exception: " + str(err.with_traceback()))
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ") 
                                + "Unhandled exception: " + str(err.with_traceback()))

    finally:
        os.unlink(pidfile)
