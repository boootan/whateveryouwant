import os
import sys
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
#df = pandas.read_csv("business_data.csv", engine='python', index_col=False)


userLocation = ""
#object to represent businesses/restaurants
class business:
    def __init__(self, index):
        self.dfIndex = index
        self.id = dfLookup(index, 'business_id')
        self.name = dfLookup(index, 'name')
        self.street = dfLookup(index, 'address')
        self.city = dfLookup(index,'city')
        self.state = dfLookup(index,'state')
        self.zip = dfLookup(index, 'postal_code')
        self.address = str(self.street) +" " +str(self.city)+" " + " "+str(self.state)+ " " + " "+ str(self.zip)
        self.distance = getDistance(self.address)
        self.stars = dfLookup(index, 'stars')
#get travel distance, calls Google Maps Distance Matrix API
def getDistance(destination):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?'
    r = requests.get(url + 'origins='+userLocation + '&destinations=' + destination+'&key='+API_KEY)
    x = r.json()
    dist = x['rows'][0]['elements'][0]['distance']['value']
    return round((dist/1000)*0.621371, 2)
#read in data from business_data.csv, define index into dataframe UNLESS FILESIZE is 0 (file empty)
def readBusinesses():
    if(os.stat("business_data.csv").st_size == 0):
        return False
    global df
    df = pandas.read_csv("business_data.csv", engine='python', index_col=False)
    df['index'] = range(0, len(df))
    if len(df) >= 25:
        return True
    else:
        return False

#lookup index from name
def index_from_name(name):
    return df[df.name == name]["index"].values[0]
#lookup name from index
def name_from_index(index):
    return df[df.index == index]["name"].values[0]
#lookup any other property in the dataframes
def dfLookup(index, lookup):
    return df[df.index == index][lookup].values[0]

#Sanitize chains and duplicate restaurants, no point in recommending Taco Bell 5 times.
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
    ### Collecting user Input ###
    supportedCities = ["Philadelphia", "New Orleans", "Nashville", "Tampa", "St. Louis", "Tucson"]
    for x in supportedCities:
        print("{}: {}".format(supportedCities.index(x)+1, x))
    city = int(input("Hi! What city are you located in? Please select the number of one of the supported cities above."))
    city = supportedCities[city-1]
    global userLocation 
    userLocation = input("What is your location? Please enter address format i.e 800 N State College Blvd, Fullerton CA 92831: ")
    keyword = input("What kind of food are you feeling? i.e. Mexican, Pizza, Chinese, Noodles?: ")
    distLimit = float(input("How many miles are you willing to travel for good food? Enter a whole number: "))
    json2db(city, keyword)
    if(readBusinesses() == False):
        print("Sorry, there aren't enough restaurants for us to make a good recommendation. Please adjust your parameters and try again.")
        return
    factors = ['categories']
    randomsample = df['name'].sample(n = 10)
    count = 1
    randomsample = randomsample.values.tolist()
    count = 1
    for i in randomsample:
        print("{}: {}".format(count, i))
        count += 1
    
    #ask for personal experience
    like = input("Above is a random sample of restaurants in your area, if you like any of them, or any of them sound good please tell us the number: ")
    restaurant_user_likes = randomsample[int(like)-1]
    

    for factor in factors:
        df[factor] = df[factor].fillna('')

    #create restaurant matrix to run similarity check on
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["categories"])

    #calculate cosine similarity of restaurant objects

    cosine_sim = cosine_similarity(count_matrix)
    #numpy.savetxt('F:/array.txt', cosine_sim)


    restaurant_index = index_from_name(restaurant_user_likes)

    similar_restaurants = list(enumerate(cosine_sim[restaurant_index]))
    #Ranking the returned restaurants
    ranked_similar_restaurants = sorted(similar_restaurants, key=lambda x:x[1], reverse=True)

    count = 0

    top25 = sanitizeChains(ranked_similar_restaurants, restaurant_user_likes)

    top25list = []
    for key in top25.keys():
        obj = business(key)
        top25list.append(obj)
    
    #code to filter out restaurants too far outside user's travel radius.
    

    for i in top25list:
        if i.distance > distLimit:
            top25list.remove(i)

    #top25list.sort(key=lambda x: x.distance)
        
    print("Here's our top recommendation!: ", top25list[0].name)
    print("Distance: ", top25list[0].distance, " miles")
    print("Address: ", top25list[0].address)
    print("Stars: ", top25list[0].stars)
    exitmsg = input("\nHope you enjoy your meal! You can hit enter to see more recommendations, or enter Q to quit. ")
    if exitmsg == 'Q':
        sys.exit()
    top25list.pop(0)
    
    for i in top25list:
        print("Name: ", i.name)
        print("Distance: ", i.distance, " miles")
        print("Address: ", i.address)
        print("Stars: ", i.stars)
        exitmsg = input("\nHope you enjoy your meal! You can hit enter to see more recommendations, or enter Q to quit. ")
        if exitmsg == "Q":
            sys.exit()


    
if __name__ == '__main__':
    main()