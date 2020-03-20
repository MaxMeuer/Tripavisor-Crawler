from requests import get
import re
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from db_connector import *
# url = 'https:#//www.tripadvisor.de/Restaurant_Review-g60763-d492818-Reviews-or10-John_s_of_Bleecker_Street-New_York_City_New_York.html'
# response = get(url)
# html_soup = BeautifulSoup(response.text, 'html.parser')
# type(html_soup)

# def formatDate(date, type):
#     if(type == 'visit'):
#
#     elif(type == 'create'):
#         pass
#     return date


# returns array of data to each review
def get_review_content(container):
        stars_span = container.find('span', class_='ui_bubble_rating')
        stars_string = str(stars_span)
        stars = re.findall(r'\d+',stars_string)[0]

        # get date per Review
        date_span = container.find('span', class_='ratingDate' )
        date_of_review = date_span['title']

        # get date of Visit
        visit_date = container.find("div", class_='prw_rup prw_reviews_stay_date_hsx').get_text().replace('Date of visit: ',"")


        # get header
        text = container.find('span', class_='noQuotes').get_text()

        return [stars,text,visit_date, date_of_review]


def create_url(url, page_number):
        partitioned_url = url.partition('Reviews')
        loop_url = partitioned_url[0] + partitioned_url[1] + '-or' + str(page_number) + '0'+ partitioned_url[2]
        return loop_url

def check_date(date):
    if(date== '' or date[-3:] == "ago" or date[-4:] == "2020"):
        return "skip"
    elif( 2020 > int(date[-4:]) > 2010):
        return "write"
    else:
        return "break"

# starting Point of single Restaurant/attraction  => "item"
def iterate_page(initial_url,id):
    # inital page of item
    initial_response = get(initial_url)
    html_soup = BeautifulSoup(initial_response.text, 'html.parser')

    # get Name and add to db
    item_name = html_soup.find('h1', class_='ui_header').get_text()
    print(item_name)
    item_id = db_connector.write_activity( id, item_name,'restaurant')
    print(item_id)

    # number of review Pages for single Item
    number_of_pages_html = html_soup.find('a', class_='last')
    if(number_of_pages_html != None):
        number_of_pages = int(number_of_pages_html.get_text())
    else:
        number_of_pages = 0

    for i in range(number_of_pages + 1):
        # print("i: " + str(i))
        if(i!=0):
            # print('review: ' + str(i))
            # create URL
            loop_url = create_url(initial_url, i)

            # get Reviews
            loop_response = get(loop_url)
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

def create_next_page_url(url, id,index):
     partitioned_url = url.partition('-'+id)
     url = partitioned_url[0][:-1] + 'Search' + partitioned_url[1] + "-oa" + str(index * 30 ) + partitioned_url[2]
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


city_url = "https://www.tripadvisor.com/Restaurants-g35805-Chicago_Illinois.html"
city_name = "Chicago"
tripadvisor_city_id = "g35805"


def iterate_restaurants_of_city(city_url,city_id,city_name):
    db_city_id = db_write_city(city_name)

    init_restaurant_response = get(city_url)
    init_restaurant_html = BeautifulSoup(init_restaurant_response.text, 'html.parser')
    # count number of pages to iterate
    all_page_numbers = init_restaurant_html.findAll('a', class_='pageNum')
    number_of_pages =  int(all_page_numbers[-1].getText())

    for x in range(number_of_pages + 1):
        # if(x == 0):
        #     init_entrys = init_restaurant_html.findAll('a', class_='_15_ydu6b')
        #     z = 1
        #     for item in init_entrys:
        #             # print('Restaurant: ' + str(z) + 'name: ' + item['href'])
        #             restaurant_url = 'https://www.tripadvisor.com' + item['href']
        #             iterate_page(restaurant_url,db_city_id)
        #             z  = z+1


        if (x > 1):
            next_page_restaurants_url = create_next_page_url(city_url,tripadvisor_city_id,x-1)
            next_page_restaurants_response =  get(next_page_restaurants_url)
            next_page_restaurants_html = BeautifulSoup(next_page_restaurants_response.text, 'html.parser')
            all_restaurants = next_page_restaurants_html.findAll('div' , class_='_1kNOY9zw')

            # eliminate Sponsered Restaurant after first Page
            # no_sponsors = array(filter(lambda x : x.find('div' , class_='_376lhJeB fXv-kKaf') == None, all_restaurants))
            # entrys = no_sponsors.findAll('a', class_='_15_ydu6b')
            i = 1
            for restaurant in all_restaurants:
                if(x >= 10):
                    if(restaurant.find('div' , class_='_376lhJeB fXv-kKaf') == None ):
                        href = restaurant.find('a', class_= '_15_ydu6b')['href']
                        restaurant_url = 'https://www.tripadvisor.com' + href
                        print("Restaurant: " + str(x*10 + i) + 'name: ' + href)
                        iterate_page(restaurant_url,db_city_id)
                        i = i + 1



# iterate_page('https://www.tripadvisor.de/Restaurant_Review-g35805-d4783426-Reviews-Taqueria_La_Zacatecana-Chicago_Illinois.html')
iterate_restaurants_of_city(city_url,tripadvisor_city_id, city_name)
# db_write_city(city_name)
