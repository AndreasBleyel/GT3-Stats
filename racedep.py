from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime as dtime

GT3_CARS = {
    'AUDI R8 LMS ULTRA': 0,
    'BMW Z4 GT3': 0,
    'FERRARI 488 GT3': 0,
    'LAMBO HURACAN GT3': 0,
    'MCLAREN 650S GT3': 0,
    'MCLAREN MP4-12C GT3': 0,
    'MERCEDES SLS AMG GT3': 0,
    #'MERCEDES AMG GT3': 0,
    'NISSAN GT-R GT3': 0,
    'PORSCHE 911 GT3': 0, 
    #'PORSCHE 911 GT3 R 2016': 0,
    #'PORSCHE 911 GT3 CUP 2017': 0,
    #'PORSCHE 911 GT RSR 2017': 0,
    'SCG-003': 0
}

REGEX_CARS = {
    'AUDI R8 LMS ULTRA': '.*audi.*|.*r8.*',
    'BMW Z4 GT3': '.*bmw.*|.*z4.*',
    'FERRARI 488 GT3': '.*ferrari.*|.*488.*',
    'LAMBO HURACAN GT3': '.*lambo.*|.*huracan.*',
    'MCLAREN 650S GT3': '.*650?s.*',
    'MCLAREN MP4-12C GT3': '.*mp4.*',
    'MERCEDES SLS AMG GT3': '.*sls.*|.*amg.*|.*merc.*',
    #'MERCEDES AMG GT3': '.*amg.*',
    'NISSAN GT-R GT3': '.*nissan.*|.*gt?-r.*',
    'PORSCHE 911 GT3': '.*porsche.*|.*911.*', 
    #'PORSCHE 911 GT3 R 2016': 0,
    #'PORSCHE 911 GT3 CUP 2017': 0,
    #'PORSCHE 911 GT RSR 2017': 0,
    'SCG-003': '.*scuderia.*|.*scg.*'
}

REGEX_CARS_DISQUALIFIERS = {
    'BMW M3 GT2': '.*m3.*',
    'GT2': '.*gt2.*',
    'Free': '.*free.*',
    'Open': '.*open.*',
    'Metzger82': '.*metzger8.*',
    'Reserve': '.*reserve.*'
}

STATS = {}
nodate = []
nodata = []
hits = {}
wrong_class = []

page_max = 58
base_url = 'https://www.racedepartment.com'
racing_club_url = '/forums/assetto-corsa-racing-club.171/' 

def check_wrong_class(listitem):
    for car, regex in REGEX_CARS_DISQUALIFIERS.items():
        if re.search(regex, listitem):
            wrong_class.append(listitem)
            #print('Wrong class: {}'.format(listitem))
            return True
    return False

def check_cars(listitem, post_date, valid_date):
    if valid_date:
        date = post_date.strftime('%Y')+'-'+post_date.strftime('%m')
    else:
        date = 'unknown_date'
    for car, regex in REGEX_CARS.items():
        if re.search(regex, listitem):
            if not check_wrong_class(listitem):
                if not date in STATS:
                    STATS[date] = {}                       
                if not car in STATS[date]: 
                    STATS[date][car] = 1
                else:
                    STATS[date][car] += 1    
                if not car in hits:
                    hits[car] = []
                hits[car].append(listitem)
                #print('Hit: {} its a: {}'.format(listitem, car))
                return True
    return False
    #print('Found: {}, {} \n String: {}\n-------'.format(car, GT3_CARS[car], listitem.lower()))

for page_nr in range(1,2):
    url = base_url + racing_club_url
    page = 'page-' + str(page_nr)
    response = requests.get(url+page)
    soup = BeautifulSoup(response.content, 'html.parser')
    threads = soup.find_all(class_= 'structItem-title')
    print('Page: {}'.format(page))

    for thread in threads:
        i = 0
        if re.search('.*gt3.*', thread['uix-data-href'].lower()):
            #print('Thread: {}'.format(thread['uix-data-href']))
            url = base_url + thread['uix-data-href']
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            try:
                post_date = dtime.strptime(soup.time['datetime'], '%Y-%m-%dT%H:%M:%S%z')
                valid_date = True
                """
                for b in soup.findAll('b'):
                    if 'Track' in b.text:
                        print(b.text)
                        #print(b.next_sibling)
                """
            except TypeError:
                nodate.append(thread['uix-data-href'])
                valid_date = False
                print('Exception')

            for ol in soup.findAll('ol'):
                for li in ol.findAll('li'):
                    if check_cars(li.text.strip().lower(), post_date, valid_date):
                        i += 1

        
        if i > 0:
            print('Thread: {} Amount: {}\n------'.format(thread['uix-data-href'],i))
        else:
            nodata.append(thread['uix-data-href'])

def save_results():
    STATS['hits'] = hits
    #STATS['nomonths'] = nomonth
    #STATS['noyears'] = noyear
    STATS['wrong_class'] = wrong_class
    STATS['nodate'] = nodate
    STATS['nodata'] = nodata
    
    path = '/home/andi/Desktop/RaceDepStats/'     
    filename = 'gt3-stats_' + dtime.now().strftime('%Y-%m-%d_%H:%M') + '.json'
    with open(path+filename, 'w') as fp:
        json.dump(STATS, fp)
    print('Saved to: {} {}'.format(path, filename))

#save_results()
def print_stats():       
    for my, cars in STATS.items():
        print('Month Year: {}'.format(my))
        for car, amount in cars.items():
            print('Car {}, Amount: {}'.format(car,amount))
        print('---')

#print_stats()


    
#https://www.racedepartment.com/threads/gt3-spa-sunday-15th-march-2020.179893
#https://www.racedepartment.com/forums/assetto-corsa-racing-club.171/page-2

"""REGEX_MONTHS = {
    'January': '.*jan.*',
    'February': '.*feb.*',
    'March': '.*mar.*',
 	'April': '.*apr.*',
    'May': '.*may.*', 
    'June': '.*jun.*',
    'July': '.*jul.*',
	'August': '.*aug.*',
    'September': '.*sep.*',
	'October': '.*oct.*',
    'November': '.*nov.*',
 	'December': '.*dec.*|.*christ.*|.*xmas.*'
}

REGEX_YEARS = {
    '2014': '.*2014.*',
    '2015': '.*2015.*',
    '2016': '.*2016.*',
    '2017': '.*2017.*',
    '2018': '.*2018.*',
    '2019': '.*2019.*',
    '2020': '.*2020.*'
}
def check_month(thread_name):
    for month, regex in REGEX_MONTHS.items():
        if re.search(regex, thread_name):
            return month

    nomonth.append(thread_name)
    return 'nomonth'

def check_year(thread_name):
    for year, regex in REGEX_YEARS.items():
        if re.search(regex, thread_name):
            return year
    noyear.append(thread_name)
    return 'noyear'
"""