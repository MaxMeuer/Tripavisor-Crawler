from requests import get
import requests
import re
from multiprocessing import Pool
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from db_connector import *
from hotels import *
from functools import partial
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

def format_date(date):

    month = date[:-4]
    year = date[-4:]
    new_date = month + "1, " + year
    return new_date

# returns array of data to each review
def get_review_content(container):
        stars_span = container.find('span', class_='ui_bubble_rating')
        stars_string = str(stars_span)
        stars = re.findall(r'\d+',stars_string)[0]

        # get date of Review
        date_span = container.find('span', class_='ratingDate' )
        date_of_review = date_span['title']

        # get date of Visit
        visit_date =  container.find("div", class_='prw_rup prw_reviews_stay_date_hsx').get_text().replace('Date of visit: ',"")
        if(visit_date == ""):
            visit_date = date_of_review
        else:
            visit_date = format_date(visit_date)

        # get header
        print(visit_date)
        print(date_of_review)

        text = container.find('span', class_='noQuotes').get_text()

        return [stars,text,visit_date, date_of_review]

def format_date_hotel(date,type):
    if(type == 'review'):
        print(date[-4])
        if(date[-4] != "2"):
            return ""
        else:
            year = date[-4:]
            month = date[:3]
            return month + " 1," + year


def get_review_content_hotel(container):
    stars_span = container.find('span', class_='ui_bubble_rating')
    stars_string = str(stars_span)
    stars = re.findall(r'\d+', stars_string)[0]

    # get date of Review
    date_div = container.find('div', class_='social-member-event-MemberEventOnObjectBlock__event_type--3njyv').find('span', recursive= False).get_text()
    # print(date_div)
    date_of_review = format_date_hotel(date_div[-8:],'review')

    # get date of Visit
    visit_date = container.find("div", class_='location-review-review-list-parts-EventDate__event_date--1epHa')
    if (visit_date == None):
        visit_date = date_of_review
    else:
        visit_date = "1" + visit_date.get_text()

    text_a = container.find('a', class_='location-review-review-list-parts-ReviewTitle__reviewTitleText--2tFRT')
    text = text_a.find('span', recursive=False).get_text()

    return [stars, text, visit_date, date_of_review]


def create_url(url, page_number):
        partitioned_url = url.partition('Reviews')
        loop_url = partitioned_url[0] + partitioned_url[1] + '-or' + str(page_number) + '0'+ partitioned_url[2]
        return loop_url


def create_url_hotel(url, page_number):
    partitioned_url = url.partition('Reviews')
    loop_url = partitioned_url[0] + partitioned_url[1] + '-or' + str(page_number*5) + partitioned_url[2]
    return loop_url

def check_date(date):
    print(date)
    if(date== '' or date[-3:] == "ago" or date[-4:] == "2020"):
        return "skip"
    elif( 2020 > int(date[-4:]) > 2010):
        return "write"
    else:
        return "break"

# starting Point of single Restaurant/attraction  => "item"
def get_soup(url):
    response = session.get(url)
    return BeautifulSoup(response.text, 'html.parser')

def iterate_activity(initial_url,id):
    # inital page of item
    initial_response = session.get(initial_url)
    html_soup = BeautifulSoup(initial_response.text, 'html.parser')

    # get Name and add to db
    item_name = html_soup.find('h1', class_='ui_header').get_text()
    item_id = db_connector.write_activity( id, item_name,'restaurant')

    # number of review Pages for single Item
    number_of_pages_html = html_soup.find('a', class_='last')
    if(number_of_pages_html != None):
        number_of_pages = int(number_of_pages_html.get_text())
    else:
        number_of_pages = 0


    for i in range(number_of_pages + 1):
        # print("i: " + str(i))
        if(i!=0):
            loop_url = create_url(initial_url, i)

            # get Reviews
            loop_response = session.get(loop_url)
            html_soup = BeautifulSoup(loop_response.text, 'html.parser')

        review_containers = html_soup.find_all('div', class_='review-container')
        z=1

        for EachPart in review_containers:
            # print("review: " + str(i)+ str(z))
            review_data = get_review_content(EachPart)
            check = check_date(review_data[2])
            if(check == "write"):
                # write into Db
                db_connector.write_sentiment(item_id,review_data)
            elif(check =='break'):
                return
            else:
                # do nuttin
                pass

def iterate_hotel(initial_url, id):
    initial_response = session.get(initial_url)
    html_soup = BeautifulSoup(initial_response.text, 'html.parser')

    # get Name and add to db
    item_name = html_soup.find('h1', class_='hotels-hotel-review-atf-info-parts-Heading__heading--2ZOcD').get_text()

    item_id = db_connector.write_activity(id, item_name, 'hotel')

    # number of review Pages for single Item
    number_of_pages_html = html_soup.findAll('a', class_='pageNum')
    if (len(number_of_pages_html) != 0):
        number_of_pages = int(number_of_pages_html[-1].get_text())
    else:
        number_of_pages = 0

    for i in range(number_of_pages):
        # print("i: " + str(i))
        if (i != 0):
            loop_url = create_url_hotel(initial_url, i)
            # get Reviews
            loop_response = session.get(loop_url)
            html_soup = BeautifulSoup(loop_response.text, 'html.parser')
    #
        review_containers = html_soup.find_all('div', class_='hotels-community-tab-common-Card__card--ihfZB hotels-community-tab-common-Card__section--4r93H')
        z = 1

        for EachPart in review_containers:
            # print("review: " + str(i)+ str(z))
            # get_review_content_hotel(EachPart)
            review_data = get_review_content(EachPart)
            check = check_date(review_data[2])
            if (check == "write"):
                # write into Db
                db_connector.write_sentiment(item_id, review_data)
            elif (check == 'break'):
                return
            else:
                # do nuttin
                pass

def create_next_page_url_restaurant(url, id,index):
     partitioned_url = url.partition('-'+id)
     url = partitioned_url[0][:-1] + 'Search' + partitioned_url[1] + "-oa" + str(index * 30 ) + partitioned_url[2]
     return url


def create_next_page_url_hotel(url, id, index):
    partitioned_url = url.partition('-' + id)
    url = partitioned_url[0]  + partitioned_url[1] + "-oa" + str(index * 30) + partitioned_url[2]
    return url


def get_coordinates(name):
         geolocator = Nominatim(user_agent="specify_your_app_name_here")
         location = geolocator.geocode(name)
         point = (location.latitude, location.longitude)
         return point

def db_write_city(name):
    coordinates = get_coordinates(name)
    db_city_id = db_connector.write_city(name, coordinates)
    return db_city_id

def iterate_pages_restaurant(url, id):
        response = session.get(url)
        restaurants_html = BeautifulSoup(response.text, 'html.parser')
        all_restaurants = restaurants_html.findAll('div' , class_='_1kNOY9zw')

        i = 1
        for restaurant in all_restaurants:
            if(restaurant.find('div' , class_='_376lhJeB fXv-kKaf') == None ):
                href = restaurant.find('a', class_= '_15_ydu6b')['href']
                restaurant_url = 'https://www.tripadvisor.com' + href
                # print("Restaurant: " + str(x*10 + i) + 'name: ' + href)
                iterate_activity(restaurant_url,id)
                i = i + 1

def iterate_pages_hotel(url,id):
    response = session.get(url)
    hotel_html = BeautifulSoup(response.text, 'html.parser')
    all_hotels = hotel_html.findAll('div', class_='listing collapsed')

    i = 1
    for hotel in all_hotels:
        if(hotel.find('span', class_='ui_merchandising_pill sponsored_v2') == None):
            print(i)
            href = hotel.find('a' , class_= 'property_title prominent')['href']
            hotel_url = 'https://www.tripadvisor.com' + href
            i =i+1
            iterate_hotel(hotel_url, id)

def all_urls_of_city(city_url,city_id,type):
    init_restaurant_response = session.get(city_url)
    init_restaurant_html = BeautifulSoup(init_restaurant_response.text, 'html.parser')
    # count number of pages to iterate
    all_page_numbers = init_restaurant_html.findAll('a', class_='pageNum')
    number_of_pages =  int(all_page_numbers[-1].getText())
    all_urls = []
    all_urls.append(city_url)
    for x in range(number_of_pages + 1):
        if x > 1:
            if(type == 'hotel'):
                next_page_url = create_next_page_url_hotel(city_url, city_id, x - 1)
            else:
                next_page_url = create_next_page_url_restaurant(city_url, city_id, x - 1)
            all_urls.append(next_page_url)
    return all_urls

restaurant_url = "https://www.tripadvisor.com/Restaurants-g35805-Chicago_Illinois.html"
hotel_url = "https://www.tripadvisor.com/Hotels-g35805-Chicago_Illinois-Hotels.html"
city_name = "Chicago"
tripadvisor_city_id = "g35805"

if __name__ == '__main__':
    restaurant_urls = all_urls_of_city(restaurant_url, tripadvisor_city_id,'rest')
    hotel_urls = all_urls_of_city(hotel_url,tripadvisor_city_id,'hotel')
    # hotel_helper = partial(iterate_pages_hotel, id=5)
    db_city_id = db_write_city(city_name)
    for url in hotel_urls:
        iterate_pages_hotel(url, db_city_id)
    # helper = partial(iterate_pages_restaurant, id = db_city_id)
    # p = Pool(4)
    # p.map(helper, restaurant_urls)
    # p.terminate()
    # p.join()




# iterate_page('https://www.tripadvisor.de/Restaurant_Review-g35805-d4783426-Reviews-Taqueria_La_Zacatecana-Chicago_Illinois.html')
# iterate_restaurants_of_city(city_url, tripadvisor_city_id, city_name)
# db_write_city(city_name)
