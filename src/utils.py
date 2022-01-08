from datetime import datetime
import inspect
from typing import Tuple

from pyrogram.errors import PeerIdInvalid
from globals import DIRECTORY, CONFIG, bot

ADMINS = CONFIG['ADMINS']
LOGFILE = DIRECTORY + CONFIG['downloader_logfile']

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
    with bot:
        for admin in ADMINS:
            try:
                bot.send_message(admin, text)
            except PeerIdInvalid:
                logger_.log(f"Failed to send warning message to admin {admin}, skipping")
    logger_.log(text)

def run_cmd(command: str) -> Tuple[str, str]:
    import subprocess as sp
    cmd_result = sp.run(command, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)

    return (
        cmd_result.stdout.decode('utf-8').strip(),
        cmd_result.stderr.decode('utf-8').strip(),
    )

if __name__ == '__main__':
    """Tests"""
    test_logger = Log("D:\\test\\bin\\bruhlog.txt")
    test_logger.log(_dbgl(), 2)
    test_logger.log(_dbgl(), 1)
    test_logger.log(2)
    test_logger.log(_dbgl(), 0)
