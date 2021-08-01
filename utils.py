from datetime import datetime
import inspect
import sqlite3
from time import sleep

def _dbgl() -> int:
    """
    Returns the line where this function
    was called
    """
    return inspect.currentframe().f_back.f_lineno

def _log(file: str, text: str, tabbing = 0):
    print("[{}]{} {}".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3], "\t"*tabbing, text))
    with open(file, 'a', encoding='utf-8') as f:
        f.write("[{}]{} {}\n".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3], "\t"*tabbing, text))

def db_retry_until_unlocked(logfile: str, directory: str, cmd: str, sleep_time = 2, max_retries = 10):
    """
    Handles the 'database is locked' exception
    and tries to execute the function until the db
    gets unlocked, and closes the connection afterwards.
    :param file: logfile
    :param directory: directory of the db
    :param cmd: sqlite command 
    :param time: sleep time between attempts in seconds (default = 2)
    :param max_retries: amounts of attempts allowed until breaking (default = 10)
    """
    _flag = False
    retry_count = 0
    con = sqlite3.connect(directory)
    cur = con.cursor()
    while not _flag:
        if retry_count < max_retries:
            try:
                cur.execute(cmd)
                con.commit()
                _flag = True
            except sqlite3.OperationalError:
                _log(logfile, f"[{retry_count}]Database is locked, reattempting again in {sleep_time} seconds...", 2)
                retry_count += 1
                sleep(sleep_time)
        else:
            _log(logfile, f"======Reached max retries ({max_retries}), breaking")
            raise ValueError("Reached max retries")
    fetched = cur.fetchall()
    con.close()
    return fetched

if __name__ == '__main__':
    """Tests"""
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 2)
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 1)
    _log("D:\\test\\bin\\bruhlog.txt", 2)
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 0)
