# curl -X POST http://data.bls.gov/pdq/SurveyOutputServlet -d 'data_tool=surveymost' -d 'series_id=LNS12000000' -d 'delimiter=comma' -d 'from_year=1948' -d 'to_year=2012' -d 'output_format=text' -d 'reformat=true'

from bs4 import BeautifulSoup as Soup
from sys import argv
import urllib, urllib2
import StringIO, csv
    
class UnicodeCsvReader(object):
    def __init__(self, f, encoding="utf-8", **kwargs):
        self.csv_reader = csv.reader(f, **kwargs)
        self.encoding = encoding

    def __iter__(self):
        return self

    def next(self):
        # read and split the csv row into fields
        row = self.csv_reader.next() 
        # now decode
        return [unicode(cell, self.encoding) for cell in row]

    @property
    def line_num(self):
        return self.csv_reader.line_num

class UnicodeDictReader(csv.DictReader):
    def __init__(self, f, encoding="utf-8", fieldnames=None, **kwds):
        csv.DictReader.__init__(self, f, fieldnames=fieldnames, **kwds)
        self.reader = UnicodeCsvReader(f, encoding=encoding, **kwds)

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
    
    return '\n'.join(csvRawList).encode('UTF-8')

# print csvRawList
def writeSeries(series):
    outfile = open(series + '.csv', 'w')
    outfile.write(getData(series))
    outfile.close()

# actually we want string IO to get the csv parsing to work...
# see http://stackoverflow.com/questions/3305926/python-csv-string-to-array

def parseSeries(series):
    scsvRaw = getData(series)
    f = StringIO.StringIO(scsvRaw)
    reader = UnicodeDictReader(f)
    data = [ r for r in reader ]
    return data


if __name__ == "__main__":
    # LNS12000000 is the base unemployment rate
    series = argv[1] if len(argv) > 1 else 'LNS12000000'

    if len(argv) > 2 and argv[2] == 'file':
        writeSeries(series)
    else:
        print parseSeries(series)