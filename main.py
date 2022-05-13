import os
import pandas
import numpy
import json
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv('API_KEY')

def readBusinesses():
    f = open('yelp_academic_dataset_business.json', 'r', encoding="utf8")
    business = [json.loads(line) for line in f]
    f.close()
    return business

def readUsers():
    f = open('yelp_academic_dataset_user.json', 'r', encoding="utf8")
    user = [json.loads(line) for line in f]
    f.close()
    return user


def main():
    business = readBusinesses()
    user = readUsers()
    
    print(business['business_id'])


if __name__ == '__main__':
    main()