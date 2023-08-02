import json
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd

def working_hours_translate(l):
    result =[]
    days = {
        "L": "mon",
        "Ma": "tue",
        "Mi": "wen",
        "J": "thu",
        "V": "fri",
        "S": "sut",
        "D": "sun",
        "a": "-",
        "y": "and"
        }

    for i in l:
        temp = i.split()
        for n, t in enumerate(temp):
            for day in days:
                if t.startswith(day):
                    temp[n] = days[day]     
        result.append(' '.join(temp))

    return result  

json_temp = []

URL_TAMPLATE = "https://dentalia.com/clinica/"
r = requests.get(URL_TAMPLATE, stream=True)

soup = bs(r.text, "html.parser")

div_container = soup.find('div', class_ = "jet-map-listing google-provider")
post_container = soup.find('div', class_ = "jet-listing-grid-loading")
post_container1 = soup.find('div', class_ = "elementor-widget-jet-listing-grid")

json_post = json.loads(post_container['data-lazy-load'])

pg_settings = json_post['post_id']  #page_settings[post_id]
qrd_id = json_post['queried_id'] #page_settings[queried_id] 
elmt_id = post_container1['data-id'] #page_settings[element_id]
json_latlang = json.loads(div_container['data-markers']) 

print(pg_settings, qrd_id, elmt_id)

for i in json_latlang:
    print(i["id"], i['latLang']['lat'], i['latLang']['lng'])

json_post_info = {
    'action': 'jet_engine_ajax',
    'handler': 'get_listing',
    'page_settings[post_id]': pg_settings,
    'page_settings[queried_id]': qrd_id,
    'page_settings[element_id]': elmt_id,
    'page_settings[page]': '1' 
}
print(json_post_info)
row = requests.post("https://dentalia.com/clinica/?nocache=1690811014", data=json_post_info)

json_row = json.loads(row.text)
s = bs(json_row["data"]["html"], "html.parser")

test = s.findAll('div', class_ = "jet-listing-grid__item") 

for i in test:
    s = bs(i.encode('utf-8'), "html.parser")
    div_name = s.find('h3') #name
    test1 = s.findAll('div', class_ = "jet-listing-dynamic-field__content") #info: location, telephones, working hours
    
    for json_value in json_latlang:
        if 'data-post-id="{0}"'.format(json_value['id']) in str(i.encode('utf-8')):
            
            name = div_name.text
            adress = test1[0].text
            phones = test1[1].text[13:].split('\r\n')
            working_hours = test1[2].text[9:].split('\r\n')# print(name.encode('utf-8'))
            
            temp = list(filter(None, working_hours))
            working_hours_translated = working_hours_translate(temp)
            json_temp.append({"name": name, #.text.encode('utf-8')
                              "address": adress,
                              "latlon": [json_value['latLang']['lat'], json_value['latLang']['lng']],
                              "phones": list(filter(None, phones)),
                              "working_hours": working_hours_translated})
            break            

with open('json_res', 'w') as json_file:
    json.dump(json_temp, json_file)
