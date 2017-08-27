import logging
import os
import sys
import time

import praw
from AFLogic import AFLogic
from db_manage import InitDB


class LoggerObject:
    def __init__(self, log_file_name):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.handler = logging.FileHandler(log_file_name)
        self.handler.setLevel(logging.INFO)

    def add_event_to_file(self, logging_string):
        logging.info(logging_string)

    def add_error(self, error_string):
        logging.error(error_string)


class CheckPID:
    def __init__(self, pid_text):
        self.pid = str(os.getpid())
        self.pid_text = pid_text

    def control_exit(self):
        if self.is_running():
            print(self.pid_text + " already running, exiting")
            sys.exit()
        else:
            # Create the lock file for the script
            open(self.pid_text, 'w').write(self.pid)

    def is_running(self):
        return os.path.isfile(self.pid_text)


class LoadCredentials:
    def __init__(self, cred_file_name, logging_object ):
        self.credentials = self.load_creds(cred_file_name, logging_object)
        self.open_time = time.strftime("%Y/%m/%d %H:%M:%S ") + "Opened creds file"

    def load_creds(self, cred_file_name, logging_object):
        try:
            with open(cred_file_name, 'r') as loaded_file:
                return dict(line.replace('\n', '').split('=') for line in loaded_file)
        except OSError:
            print("Couldn't open ExcusesCreds.txt")
            logging_object.add_error("{} Couldn't open ExcusesCreds.txt".format(time.strftime("%Y/%m/%d %H:%M:%S ")))
            exit()

    def get_credentials(self):
        return self.credentials


class RedditAuthenticate:
    def __init__(self, cred_file_name, logging_object):
        self.logging_object = logging_object
        self.credentails = LoadCredentials(cred_file_name, logging_object).get_credentials()
        self.client = None
        self.retry_count = 0
        self.log_in()

    def log_in(self):
        while not self.authenticate():
            self.authenticate()

    def authenticate(self):
        try:
            self.client = praw.Reddit(**self.credentails)
            print('Logged in')
            return True
        except praw.errors.InvalidUserPass:
            print("Wrong username or password")
            self.logging_object.add_error('Wrong username or password'.format(time.strftime("%Y/%m/%d %H:%M:%S ")))
            exit(1)
        except Exception as err:
            print(str(err))
            time.sleep(1 * (2 ** self.retry_count))  # exponentially longer retry. 2^4 = 16 seconds. So 4 retry = 31
            self.retry_count += 1
            return

    def get_client(self):
        return self.client


def main():
    selected_subreddit = 'AFexcuse'
    CheckPID('AFexcuses.pid')
    db_connection, db_comment_record, db_object = InitDB("ExcusesCommentRecord.db").get_db()
    logging_object = LoggerObject('AFexcuses.log')
    auth_client = RedditAuthenticate('ExcusesCreds.txt', logging_object)
    r_air_force = auth_client.get_client().subreddit(selected_subreddit)
    count_comment = 0
    logic_handler = AFLogic(db_object, logging_object)
    while True:
        try:
            for comment in r_air_force.stream.comments():
                count_comment += 1
                logic_handler.single_comment(count_comment, comment)
            continue
        # what to do if Ctrl-C is pressed while script is running
        except KeyboardInterrupt:
            print("Keyboard Interrupt experienced, cleaning up and exiting")
            db_connection.commit()
            db_connection.close()
            print("Exiting due to keyboard interrupt")
            logging_object.add_event_to_file(' Exiting due to keyboard interrupt'.format(time.strftime("%Y/%m/%d %H:%M:%S ")))
            exit(0)
        except Exception as err:
            print("Exception: {}".format(err.with_traceback()))
            logging_object.add_error('{} Unhandled exception: {}'.format(time.strftime("%Y/%m/%d %H:%M:%S "), str(err.with_traceback())))
            continue
        finally:
            os.unlink('AFexcuses.pid')


if __name__ == '__main__':
    main()
