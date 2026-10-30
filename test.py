import json
import os

directry = os.path.dirname(os.path.abspath(__file__))
filepath = os.path.join(directry,"data","processed","bns_sections.json")


# data = "../data/processed/bns_section.json"




with open(filepath,"r", encoding="utf-8") as file:
    data = json.load(file)
    # i = 1
    # while i<358:
    #     sec_num = data[i]['section_number']
    #     if i != sec_num:
    #         print(i)
    #         i+=1
    #         break
    i = 1
    while i < 358:
        if str(i+1) != data[i]['section_number']:
            print(i+1,end=",")
            i = int(data[i]['section_number'])
            
        i+=1