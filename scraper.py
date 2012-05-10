# curl -X POST http://data.bls.gov/pdq/SurveyOutputServlet -d 'data_tool=surveymost' -d 'series_id=LNS12000000' -d 'delimiter=comma' -d 'from_year=1948' -d 'to_year=2012' -d 'output_format=text' -d 'reformat=true'

from bs4 import BeautifulSoup as Soup
from sys import argv
import urllib, urllib2
import StringIO, csv

series = argv[1] if len(argv) > 1 else 'LNS12000000'

def getData(series):
    postData = {
        'data_tool'     : 'surveymost',
        'series_id'     : series,
        'delimiter'     : 'comma',
        'from_year'     : '1948',
        'to_year'       : '2012',
        'output_format' : 'text',
    }
    url = 'http://data.bls.gov/pdq/SurveyOutputServlet'

    req = urllib2.Request(url)
    req.add_data(urllib.urlencode(postData))

    html = urllib2.urlopen(req)

    htmlStr = html.read()

    # now we have the HTML content as a string!
    soup = Soup(htmlStr)

    csvSuperRaw = soup.find('pre', attrs={'style': 'csv-output'}).getText()

    # ok, let's tear this down to the real data...
    active = False
    csvRawList = []
    for line in csvSuperRaw.split('\n'):
        if line.find('Year') is 0:
            active = True
        if len(line.strip()) is 0:
            active = False
        if active is True:
            csvRawList.append(line)
    
    return '\n'.join(csvRawList)

# print csvRawList

outfile = open(series + '.csv', 'w')
outfile.write(getData(series).encode('UTF-8'))
outfile.close()

# actually we want string IO to get the csv parsing to work...
# see http://stackoverflow.com/questions/3305926/python-csv-string-to-array