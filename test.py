import clipboard
from requests import get
from bs4 import BeautifulSoup

soup = get('https://www.tripadvisor.com/Hotels-g35805-oa30-Chicago_Illinois-Hotels.html')

clipboard.copy(soup.text)
