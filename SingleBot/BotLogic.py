import time
import random
import re


class BotLogic:
    def __init__(self,  db_object, logging_object):
        self.db_object = db_object
        self.logging_object = logging_object
        self.excuse_list = self.read_in_excuse_list('Excuses.txt')

    def read_in_excuse_list(self, excuse_file_name):
        with open(excuse_file_name, 'r') as f:
            return f.read().splitlines()

    def single_comment(self, count_comment, comment):
        self.print_start_items(count_comment, comment)
        if self.db_object(comment.id):
            print("Already processed comment: " +
                  str(comment.id) + ", skipping")
            return
        elif comment.author == "AFexcuses":
            print("Author was the bot, skipping...")
            return
        else:
            if self.is_match(comment.body):
                self.process_comment(comment)

    def print_start_items(self, count_comment, comment):
        print("\nComments processed since start of script: {}".format(count_comment))
        print("Processing comment: " + comment.id)
        # prints a link to the comment. A True for permalink generates a fast find (but is not an accurate link,
        # just makes the script faster *SIGNIFICANTLY FASTER)
        print('http://www.reddit.com{}/'.format(comment.permalink(True)))

    def is_match(self, comment_text):
        match = re.search(r'(?i)(!*)afexcuse(s)?(!*)', comment_text)
        # example = ['!afexcuses', '!AFEXCUSES', '!aFeXcuSeS!']
        # case insenstive match, exclamation bfore or after.
        # match objects are true or None, so you can check for conditional
        return match

    def reply_comment(self, comment):
        comment.reply(self.get_random_comment())

    def get_random_comment(self):
        return '^^You\'ve ^^spun ^^the ^^wheel ^^of ^^Air ^^Force ^^excuses, ^^here\'s ^^your ^^prize:\n\n {}\n\n\n\n ^^[Source](https://github.com/HadManySons/AFexcuses)^^| ^^[Subreddit](https://www.reddit.com/r/AFExcuses)'.format(random.choice(self.excuse_list))

    def process_comment(self, comment):
        single_log = 'Dropping an excuse on: {}. Comment ID:  {}  with {} excuses loaded.'.format(comment.author, comment.id, len(self.excuse_list))
        self.logging_object.add_event_to_file('{} {}'.format(time.strftime("%Y/%m/%d %H:%M:%S "), single_log))
        self.reply_comment(comment)
        self.db_object.insert(comment.id)
