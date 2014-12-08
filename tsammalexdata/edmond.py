from io import open

import requests

from tsammalexdata.util import data_file


URL = \
    "http://edmond.mpdl.mpg.de/imeji/export"\
    "?format=xml&type=image&n=10000&col=d2JGQRxO19XTOEXG&q="


if __name__ == '__main__':
    with open(data_file('Edmond.xml'), 'w', encoding='utf8') as fp:
        fp.write(requests.get(URL).text)
