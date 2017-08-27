from lib.AFExcuse import LoggerObject, CheckPID, LoadCredentials, RedditAuthenticate
from lib.AFLogic import AFLogic
from lib.db_manage import ManageDB
from os import unlink
from time import strftime

def main():
    selected_subreddit = 'AFexcuse'
    CheckPID('AFexcuses.pid')
    db_connection, db_comment_record, db_object = ManageDB("ExcusesCommentRecord.db").get_db()
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
            logging_object.add_event_to_file(' Exiting due to keyboard interrupt'.format(strftime("%Y/%m/%d %H:%M:%S ")))
            exit(0)
        except Exception as err:
            print("Exception: {}".format(err.with_traceback()))
            logging_object.add_error('{} Unhandled exception: {}'.format(strftime("%Y/%m/%d %H:%M:%S "), str(err.with_traceback())))
            continue
        finally:
            unlink('AFexcuses.pid')


if __name__ == '__main__':
    main()