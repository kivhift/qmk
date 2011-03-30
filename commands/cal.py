import calendar
import datetime

import qmk

class CalendarCommand(qmk.Command):
    '''Display a calendar for a given month.  With no arguments, the
    current year and month are used.  If one argument is given, it is
    used as the month with the current year unless the month is invalid
    in which case the current month is used with the argument as the
    year.  If two arguments are given, they are assumed to be the year
    and month, respectively, unless the month is invalid in which case
    the arguments are used as month and year, respectively.'''
    def __init__(self):
        self._name = 'cal'
        self._help = self.__doc__

    def action(self, arg):
        now = datetime.datetime.now()
        year, month = now.year, now.month

        if arg is not None:
            args = arg.split()
            if len(args) == 2:
                try:
                    y, m = int(args[0]), int(args[1])
                    if m < 1 or m > 12:
                        y, m = m, y
                    year, month = y, m
                except:
                    pass
            elif len(args) == 1:
                try:
                    y = now.year
                    m = int(args[0])
                    if m < 1 or m > 12:
                        y = m
                        m = now.month
                    year, month = y, m
                except:
                    pass

        cal = calendar.TextCalendar(firstweekday=calendar.MONDAY)
        lines = [ '     ' + cal.formatmonthname(year, month, 20, True) ]
        lines.append('Wk | ' + cal.formatweekheader(2))

        i = 0
        ln = ''
        mark = '*' if year == now.year and month == now.month else ' '
        a_day_in_week = 0
        for d in cal.itermonthdays(year, month):
            if 0 == d:
                ln += '   '
            else:
                ln += '%2d%s' % (d, ' ' if now.day != d else mark)
                if 0 == a_day_in_week:
                    a_day_in_week = d

            if 6 == i % 7:
                lines.append('%2d | %s' % (datetime.date(
                    year, month, a_day_in_week).isocalendar()[1], ln))
                ln = ''
                a_day_in_week = 0

            i += 1

        qmk.Message()('\n'.join(lines))

def commands(): return [ CalendarCommand() ]
