import os
import pandas
import numpy
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')
df = pandas.read_csv("business_data.csv", engine='python', index_col=False)
df['index'] = range(0, len(df))

class business():
    def __init__():
        name = ""
        dfIndex = None
        location = (0, 0)
        
def readBusinesses():
    f = open('yelp_academic_dataset_business.json', 'r', encoding="utf8")
    input = [json.loads(line) for line in f]
    business = []
    f.close()
    for i in input:
        if i['city'] == "Philadelphia":
            business.append(i)
    return business

def readUsers():
    f = open('yelp_academic_dataset_user.json', 'r', encoding="utf8")
    user = [json.loads(line) for line in f]
    f.close()
    return user

def readReviews():
    f = open('yelp_academic_dataset_review.json', 'r', encoding="utf8")
    user = [json.loads(line) for line in f]
    f.close()
    return user

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
    factors = ['categories']

    for factor in factors:
        df[factor] = df[factor].fillna('')

    cv = CountVectorizer()
    count_matrix = cv.fit_transform(df["categories"])
    print("Count Matrix:", count_matrix.toarray())

    cosine_sim = cosine_similarity(count_matrix)
    numpy.savetxt('F:/array.txt', cosine_sim)

    restaurant_user_likes = "Xochitl"

    restaurant_index = index_from_name(restaurant_user_likes)

    similar_restaurants = list(enumerate(cosine_sim[restaurant_index]))

    ranked_similar_restaurants = sorted(similar_restaurants, key=lambda x:x[1], reverse=True)

    count = 0

    top25 = sanitizeChains(ranked_similar_restaurants, restaurant_user_likes)

    print(top25.values())

    
    

    
    



if __name__ == '__main__':
    main()