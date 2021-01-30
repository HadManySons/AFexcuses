import praw
import logging
import time
import os
import sys

credsUserAgent = os.environ.get("AFE_USERAGENT")
credsClientID = os.environ.get("AFE_ID")
credsClientSecret = os.environ.get("AFE_SECRET")
credsPassword = os.environ.get("AFE_PASSWORD")
credsUserName = os.environ.get("AFE_USERNAME")

# Initialize a logging object and have some examples below from the Python
# Doc page
logging.basicConfig(filename='AuthDelete.log', level=logging.INFO)

# Get the PID of this process
pid = str(os.getpid())
pidfile = "AuthDelete.pid"

# Exit if a version of the script is already running
if os.path.isfile(pidfile):
    print(pidfile + " already running, exiting")
    sys.exit()

# Create the lock file for the script
open(pidfile, 'w').write(pid)

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") + "Starting script")

# Try to login or sleep/wait until logged in, or exit if user/pass wrong
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
        print(err)
        time.sleep(5)

# vars
globalCount = 0

logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
             "Starting processing loop for comments")
triggerWords = ['afexcuses!', 'afexcuse!']
mods = ['silentd', 'hadmanysons']

while True:
    try:
        # stream all unread messages from inbox
        for rAirForceComments in reddit.inbox.stream():
            globalCount += 1

            #Marks the comment as read
            rAirForceComments.mark_read()
            
            #Check if comment or message
            if isinstance(rAirForceComments, praw.models.reddit.comment.Comment):
                print("Is comment, skipping")
                continue
                
            #If, for some odd reason, the bot is the author, ignore it.
            if rAirForceComments.author == "AFexcuses":
                print("Author was the bot, skipping...")
                continue


            else:

                formattedComment = rAirForceComments.body
                formattedComment = formattedComment.lower()
                formattedComment = formattedComment.replace(' ', '')
                
                #Shutdown bot if mod commands it
                if "shutdown!" in formattedComment:
                    if str(rAirForceComments.author).lower() in mods:
                        os.system("cat /home/redditbots/bots/AFILinkerBot/AFILinkerBot.pid | xargs kill -9")
                    else:
                        print("Not a mod, go fuck yourself")

                #Shutdown bot if mod commands it
                if "shutdown!" in formattedComment and rAirForceComments.author == ("HadManySons" or "SilentD"):
                    os.system("cat /home/redditbots/bots/AFILinkerBot/AFILinkerBot.pid | xargs kill -9")
        
                if "deletethis!" in formattedComment:

                        # Get the parent comment(the bot) and grandparent(comment originally replied to)
                        parent = rAirForceComments.parent()
                        grandparent = parent.parent()
                        #Must be the original comment author
                        if rAirForceComments.author == grandparent.author:
                            print("Deleting comment per redditors request")
                            rAirForceComments.parent().delete()
                            logging.info(time.strftime("%Y/%m/%d %H:%M:%S ") +
                                     "Deleting comment: " + rAirForceComments.id)

                            #Let them know we deleted the comment
                            rAirForceComments.author.message("Comment deleted", "Comment deleted: " + rAirForceComments.id)

    # what to do if Ctrl-C is pressed while script is running
    except KeyboardInterrupt:
        print("Keyboard Interrupt experienced, cleaning up and exiting")
        print("Exiting due to keyboard interrupt")
        logging.info(time.strftime("%Y/%m/%d %H:%M:%S ")
                     + "Exiting due to keyboard interrupt")
        exit(0)

    except Exception as err:
        print("Exception: " + str(err.with_traceback()))
        logging.error(time.strftime("%Y/%m/%d %H:%M:%S ")
                      + "Unhandled exception: " + + str(err.with_traceback()))

    finally:
        os.unlink(pidfile)
