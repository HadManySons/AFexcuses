import logging
import sys
import os
import time
import praw


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


