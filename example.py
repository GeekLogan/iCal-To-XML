import iCalToXML

url = 'http://www.google.com/calendar/ical/en.usa%23holiday%40group.v.calendar.google.com/public/basic.ics'

file = iCalToXML.loadFileFromLink(url)
events = iCalToXML.getAllEvents(file)
iCalToXML.printAsXML(events)
