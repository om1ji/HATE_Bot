from datetime import datetime, timezone
import inspect

def _dbgl():
    return inspect.currentframe().f_back.f_lineno

def _log(file, text, tabbing = 0):
    print("[{}]{} {}".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3], "\t"*tabbing, text))
    with open(file, 'a', encoding='utf-8') as f:
        f.write("[{}]{} {}\n".format(str(datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))[:-3], "\t"*tabbing, text))

if __name__ == '__main__':
    """Tests"""
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 2)
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 1)
    _log("D:\\test\\bin\\bruhlog.txt", 2)
    _log("D:\\test\\bin\\bruhlog.txt", _dbgl(), 0)
