import urllib2
from icalendar import Calendar, Event, vRecur
from datetime import *
import commands
import os
import pytz
from dateutil.rrule import *
from dateutil.parser import *

class EventWrapper(object):
    def __init__(self, summary, start, end, now):
        self.summary = summary
        self.start = start
        self.end = end
        self.localize(now)
    def __str__(self):
        out = "<name>"
        out += self.summary
        out += "</name><start>"
        out += str(self.start)
        out += "</start><end>"
        out += str(self.end)
        out += "</end>"
        return out
    def localize(self, now):
        if type(self.start) is datetime:
            if type(self.start.tzinfo) is type(None):
                self.start = self.start.replace(tzinfo=now.tzinfo)
        if type(self.end) is datetime:
            if type(self.end.tzinfo) is type(None):
                self.end = self.end.replace(tzinfo=now.tzinfo)

def loadFileFromLink(url):
    file = urllib2.urlopen(url)
    file_text = ""
    for line in file:
        file_text += line
    cal = Calendar.from_ical(file_text)
    return cal

def getAllEvents(cal):
    now = datetime.now(pytz.timezone("America/New_York"))
    today = date.today()
    MAX_YEAR = 2040
    output = []
    for component in cal.walk():
        if component.name == "VEVENT":
            if type(component.get('rrule')) is vRecur:
                rrule_string = component.get('rrule').to_ical()
                ori = component.get('dtstart').dt
                if type(ori) == datetime:
                    start_false = datetime(ori.year, ori.month, ori.day, ori.hour, ori.minute, ori.second)
                else:
                    start_false = ori
                dates = rrulestr(rrule_string, ignoretz=True, forceset=True, dtstart=start_false)
                diff = component.get('dtend').dt - ori
                for a in dates:
                    if type(ori) == datetime:
                        a.replace(a.year, a.month, a.day, ori.hour, ori.minute, ori.second)
                    inRange = True
                    if a.year > MAX_YEAR:
                        inRange = False
                    elif a.year < now.year:
                        inRange = False
                    elif a.year == now.year:
                        if a.month < now.month:
                            inRange = False
                        elif a.month == now.month:
                            if a.day < now.day:
                                inRange = False
                            #else:
                                #we will allow through events from earlier the same day
                    if inRange:
                        summary = component.get('summary')
                        start = a
                        end = a + diff
                        output.append(EventWrapper(summary, start, end, now))
            else:
                isBefore = False
                try:
                    if component.get('dtstart').dt > now:
                        isBefore = True
                except TypeError: #found a whole-day event
                    toCompare = component.get('dtstart').dt
                    if today.year < toCompare.year:
                        isBefore = True
                    elif today.year == toCompare.year:
                        if today.month < toCompare.month:
                            isBefore = True
                        elif today.month == toCompare.month:
                            if today.day <= toCompare.day:
                                isBefore = True

                if isBefore:
                    summary = component.get('summary')
                    start = component.get('dtstart').dt
                    end = component.get('dtend').dt
                    output.append(EventWrapper(summary, start, end, now))
    return output

def printAsXML(wrappers):
    print "<calendar>"
    for this in wrappers:
        print this
    print "</calendar>"
