from datetime import datetime
import inspect

from globals import *

ADMINS = CONFIG['ADMINS']
LOGFILE = DIRECTION + CONFIG['downloader_logfile']

class Log():
    def __init__(self, file: str = LOGFILE) -> None:
        self.file = file

    def log(self, text: str, offset = 0, *, logfile = None) -> None:
        now = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3] # [:-3] crops the extra milliseconds digits
        tab = '\t'*offset
        fmt = f"[{now}]{tab} {text}\n"

        print(fmt, end='')
        if not logfile:
            with open(self.file, 'a', encoding='utf-8') as f:
                f.write(fmt)
        else:
            with open(logfile, 'a', encoding='utf-8') as f:
                f.write(fmt)

logger_ = Log()

def _dbgl() -> int:
    """
    Returns the line where this function
    was called
    """
    return inspect.currentframe().f_back.f_lineno

def notify_admins(text: str) -> None:
    """
    Notifies all admins with a text and logs it.
    :param text: text to send
    """
    for admin in ADMINS:
        bot.send_message(admin, text)
    logger_.log(text)

if __name__ == '__main__':
    """Tests"""
    test_logger = Log("D:\\test\\bin\\bruhlog.txt")
    test_logger.log(_dbgl(), 2)
    test_logger.log(_dbgl(), 1)
    test_logger.log(2)
    test_logger.log(_dbgl(), 0)
