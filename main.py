import os
import pandas
import numpy
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import requests
from json2db import json2db
load_dotenv()
API_KEY = os.getenv('API_KEY')
df = pandas.read_csv("business_data.csv", engine='python', index_col=False)


userLocation = ""

class business:
    def __init__(self, index):
        self.dfIndex = index
        self.id = dfLookup(index, 'business_id')
        self.name = dfLookup(index, 'name')
        self.street = dfLookup(index, 'address')
        self.city = dfLookup(index,'city')
        self.state = dfLookup(index,'state')
        self.zip = dfLookup(index, 'postal_code')
        self.address = str(self.street) + str(self.city) + str(self.state) + str(self.zip)
        self.distance = getDistance(self.address)
        self.stars = dfLookup(index, 'stars')

def getDistance(destination):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    r = requests.get(url + 'origins='+userLocation + '&destinations=' + destination+'&key='+API_KEY)
    x = r.json()
    dist = x['rows'][0]['elements'][0]['distance']['value']
    return round((dist/1000)*0.621371, 2)
        
def readBusinesses():
    global df
    df = pandas.read_csv("business_data.csv", engine='python', index_col=False)
    df['index'] = range(0, len(df))


def index_from_name(name):
    return df[df.name == name]["index"].values[0]

def name_from_index(index):
    return df[df.index == index]["name"].values[0]

def dfLookup(index, lookup):
    return df[df.index == index][lookup].values[0]

def dictLookup(dict, lookup):
    for key, value in dict.items():
        if (value == lookup):
            print(True)
            return True
        else:
            print(False)
            return False

def sanitizeChains(ranked_similar_restaurants, name):
    ret = dict([])
    count = 0
    for r in ranked_similar_restaurants:
        restname = name_from_index(r[0])
        if restname != name and count < 24 and (restname not in ret.values()):
            ret[r[0]] = restname 
            count += 1
    return ret
    

def main():
    city = input("Hi! What city are you located in? ")
    global userLocation 
    userLocation = input("What is your location? Please enter address format i.e 800 N State College Blvd, Fullerton CA 92831: ")
    keyword = input("What kind of food are you feeling? i.e. Mexican, Pizza, Chinese")
    json2db(city, keyword)
    readBusinesses()
    factors = ['categories']
    randomsample = df['name'].sample(n = 10, index=range(1,10))
    count = 1
    for i in randomsample:
        print("{}: {}".format(randomsample.where(i), i))
        count += 1

    like = input("Above is a random sample of restaurants in your area, if you like any of them, or any of them sound good please tell us the number: ")
    restaurant_user_likes = randomsample[like-1]
    

    for factor in factors:
        df[factor] = df[factor].fillna('')

    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["categories"])

    cosine_sim = cosine_similarity(count_matrix)
    numpy.savetxt('F:/array.txt', cosine_sim)

    restaurant_index = index_from_name(restaurant_user_likes)

    similar_restaurants = list(enumerate(cosine_sim[restaurant_index]))

    ranked_similar_restaurants = sorted(similar_restaurants, key=lambda x:x[1], reverse=True)

    count = 0

    top25 = sanitizeChains(ranked_similar_restaurants, restaurant_user_likes)

    top25list = []
    for key in top25.keys():
        obj = business(key)
        top25list.append(obj)
    
    distLimit = 2.0

    for i in top25list:
        if i.distance > distLimit:
            top25list.remove(i)

    top25list.sort(key=lambda x: x.distance)
        
    for i in top25list:
        print(i.name, i.distance, i.stars)

    
if __name__ == '__main__':
    main()