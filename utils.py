from datetime import datetime
import inspect
import sqlite3

def _dbgl():
    """
    Returns the line where this function
    was called
    """
    return inspect.currentframe().f_back.f_lineno

def _log(file, text, tabbing = 0):
    print("[{}]{} {}".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3], "\t"*tabbing, text))
    with open(file, 'a', encoding='utf-8') as f:
        f.write("[{}]{} {}\n".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3], "\t"*tabbing, text))

def db_retry_until_unlocked(logfile, cur, cmd: str, time = 2, max_retries = 10):
    """
    Handles the 'database is locked' exception
    and tries to execute the function until the db
    gets unlocked.
    :param file: logfile
    :param cur: sqlite cursor
    :param cmd: sqlite command 
    :param time: sleep time between attempts in seconds (default = 2)
    :param max_retries: amounts of attempts allowed until breaking (default = 10)
    """
    _flag = False
    retry_count = 0
    while not _flag:
        if retry_count < max_retries:
            try:
                cur.execute(cmd)
                _flag = True
            except sqlite3.OperationalError:
                _log(logfile, f"[{retry_count}]Database is locked, reattempting again in {time} seconds...", 2)
                retry_count += 1
                time.sleep(2)
        else:
            _log(logfile, f"======Reached max retries ({max_retries}), breaking")
            raise ValueError("Reached max retries")


if __name__ == '__main__':
    """Tests"""
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 2)
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 1)
    _log("D:\\test\\bin\\bruhlog.txt", 2)
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 0)
