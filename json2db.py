import json
import csv


with open('yelp_academic_dataset_business.json', 'r', encoding='utf-8') as f:
    data = [json.loads(line) for line in f]

    business = []
    index = 1
    for d in data:
        if d['city'] == "Philadelphia" and (str(d['categories']).find("Restaurant") != -1 and (str(d['categories']).find("Mexican") != -1)):
            business.append(d)
    
    data_file = open('business_data.csv', 'w', encoding='utf-8')
    csv_writer = csv.writer(data_file)
    count = 0

    for b in business:
        if count == 0:
            header = b.keys()
            csv_writer.writerow(header)
            count += 1
        csv_writer.writerow(b.values())
data_file.close()

