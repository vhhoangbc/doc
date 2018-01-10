#!/usr/bin/env python

"""
Searches for log lines between the given dates.
Expected date format in log files eg.:
Oct 22 11:46:24.394

On SLES12 TG other date format:
2017-10-22T11:46:24.748034+02:00

USAGE: <filename> <start_time> <end_time> [<filter>]
	filename	- name of the log file
	startdate	- from which date to get log lines (in secs since epoch)
	enddate		- until this date (in secs since epoch)
	filter		- [optional] text to search for

Examples:
./getLogBetween.py repdb.log `date --date="1 day ago" '+%s'` `date '+%s'` "Send buffer full" | less
./getLogBetween.py messages `date --date="2017-10-22 01:37:24" '+%s'` `date --date="2017-10-22 01:40:00" '+%s'` charon | less
"""

import sys
import traceback
import time
from datetime import datetime

format_1 = '%Y/%b/%d-%H:%M:%S'
format_2 = '%Y-%m-%dT%H:%M:%S'
month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
year = str(datetime.today().year)

def printStackDump():
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logError(''.join(line for line in traceback.format_exception(exc_type, exc_value, exc_traceback)))

def logError(text):
    sys.stderr.write(text + '\n')
    sys.stderr.flush()

def log(text):
    sys.stdout.write(text)
    sys.stdout.flush()

def calculateTime(line):
    _format = None
    _time = 0
    header = line.split()[:3]
    new_time = ''
    if [i for i in month_list if i in header]:
        _format = format_1
        month = header[0]
        day = '0' + header[1] if len(header[1]) < 2 else header[1]
        hour = header[2].split('.',1)[0]
        new_time = year + '/' + month + '/' + day + '-' + hour
    elif 'T' in header[0]:
        _format = format_2
        new_time = header[0].split('.')[0]
    if _format:
        t = datetime.strptime(new_time, _format)
        _time = time.mktime(t.timetuple())
    return _format, _time

def main(file_name, start, end, grep = None):
    with open(file_name,'r') as fp:
        try:
            for line in fp:
                _format, _time = calculateTime(line)
                if _format:
                    if _time > float(end):
                        break
                    else:
                        if (grep is None or grep in line):
                            log(line)
                else:
                    if (grep is None or grep in line):
                        log(line)
        except:
            printStackDump()

if __name__ == '__main__':
    an = len(sys.argv)
    if an == 4:
        sys.exit(main(sys.argv[1],sys.argv[2],sys.argv[3]))
    else:
        sys.exit(main(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4]))

