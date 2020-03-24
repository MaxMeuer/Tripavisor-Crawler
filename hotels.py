# from requests.adapters import HTTPAdapter
# from requests.packages.urllib3.util.retry import Retry
#
# session = requests.Session()
# retry = Retry(connect=3, backoff_factor=0.5)
# adapter = HTTPAdapter(max_retries=retry)
# session.mount('http://', adapter)
# session.mount('https://', adapter)
#
# class hotels:
#
#     def all_urls_of_city(hotel_url,city_id):
#         init_hotel_response = session.get(hotel_url)
#         init_hotel_html = BeautifulSoup(init_hotel_response.text, 'html.parser')
#         # count number of pages to iterate
#         all_page_numbers = init_hotel_html.findAll('a', class_='pageNum')
#         number_of_pages =  int(all_page_numbers[-1].getText())
#         all_urls = []
#         all_urls.append(city_url)
#         for x in range(number_of_pages + 1):
#             if x > 1:
#                 next_page_hotel_url = create_next_page_url(city_url, city_id, x - 1)
#                 all_urls.append(next_page_hotel_url)
#         return all_urls