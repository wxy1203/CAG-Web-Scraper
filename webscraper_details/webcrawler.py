import pandas as pd
import re
from urllib.parse import urlparse
from utils import get_default_result, make_request, create_new_row

# For websites of type https://www.changiairport.com/en/airport-guide/facilities-and-services
# For websites of type https://www.changiairport.com/en/discover/attractions
def scrape_changi_facilities_attractions(url: str) -> str:
    soup = make_request(url)
    if not soup:
            return get_default_result()

    text = ' '.join([element.get_text(strip = 'True', separator= ' ') for element in soup.find_all(class_='rich-text-content')])
    result = get_default_result()
    result['Description'] = text
    outlets = soup.find_all(class_='outlet-item')
    key_mapping = {
        'outlet-head': 'Terminal',
        'area-type': 'Area',
        'address': 'Level',
        'opening-hours': 'Opening Hour'
    }

    for outlet in outlets:
        outlet_info = {}
        for class_ in ['outlet-head', 'area-type', 'address', 'opening-hours']:
            element = outlet.find(class_=class_)
            if element:
                text = element.get_text(separator=" ").strip()
                if class_ == 'opening-hours':
                    text = text.replace('Opening hours:\n', '').strip()
            else:
                text = ''
            outlet_info[key_mapping[class_]] = text
        result['outlets'].append(outlet_info)
    return result

# For websites of type https://www.jewelchangiairport.com/en/attractions/
def scrape_jewel_attractions(url: str) -> str:
    soup = make_request(url)
    if not soup:
            return get_default_result()

    text = ' '.join([element.get_text(strip='True', separator= ' ') for element in soup.find_all(class_='desc')])
    result = get_default_result()
    result['Description'] = text
    outlets = soup.find_all(class_='meta')
    key_mapping = {
        'location': 'Area',
        'open': 'Opening Hour'
    }
    for outlet in outlets:
        outlet_info = {}
        for class_ in ['open', 'location']:
            element = outlet.find(class_=class_)
            if element:
                text = element.get_text(separator=' ').strip()
                text = text.split('\n')[-1].strip()
                if class_ == 'location':
                    split_text = text.split(' (')  # Split by ' (' to separate area and level
                    area = split_text[0]
                    level = split_text[1].rstrip(')') if len(split_text) > 1 else ''
                    if len(level) == 2:
                        level = 'Level ' + level[1]
                    outlet_info['Area'] = "Public"
                    if level:
                        outlet_info['Level'] = level + ", " + area
                    else:
                        if len(area) == 2:
                            area = 'Level ' + area[1]
                        outlet_info['Level'] = area
                else:
                    outlet_info[key_mapping[class_]] = text
            else:
                text = ''
                outlet_info[key_mapping[class_]] = text
        outlet_info['Terminal'] = 'Jewel'
        result['outlets'].append(outlet_info)
    return result

# For websites of type https://www.changiairport.com/en/airport-guide/departing
def scrape_changi_departing(url: str):
    soup = make_request(url)
    if not soup:
            return get_default_result()

    result = get_default_result()
    parsed_url = urlparse(url)
    fragment = parsed_url.fragment
    text = soup.find(id=fragment).get_text(strip= 'True', separator=" ").strip()
    text = re.sub('\n\s*\n', '\n', text)
    result['Description'] = text
    return result

def handle_scraping(url: str) -> str:
    parsed_url = urlparse(url)
    base_url = parsed_url.netloc
    path_parts = parsed_url.path.split('/')
    path = '/'.join(path_parts[:4])
    if base_url == 'www.changiairport.com':
        if path in ['/en/airport-guide/facilities-and-services', '/en/discover/attractions']:
            return scrape_changi_facilities_attractions(url)
        elif path in ['/en/airport-guide/departing']:
            return scrape_changi_departing(url)
    elif base_url == 'www.jewelchangiairport.com':
        return scrape_jewel_attractions(url)

def main():
    df = pd.read_excel('Pages to Crawl.xlsx', sheet_name=0)

    results_df = pd.DataFrame(columns=['Domain', 'Facility/Service/Attraction' , 'Terminal',
                                       'Area', 'Level', 'Opening Hour', 'Description'])
    results = []

    for _, row in df.iterrows():
        result = handle_scraping(row['Weblink'])
        if result:
            if result['outlets']:
                for outlet in result['outlets']:

                    opening_hour = outlet['Opening Hour']
                    if opening_hour == '24/7' or opening_hour == '24 Hours' or opening_hour == 'Daily,24 hours' or opening_hour == '24 hours':
                        opening_hour = '24 hours daily'
                        
                    new_row = create_new_row(row['Domain'], row['Facility/Service/Attraction'], outlet['Terminal'],
                                                outlet['Area'], outlet['Level'], opening_hour, result['Description'])
                    results.append(new_row)
            else:
                new_row = create_new_row(row['Domain'], row['Facility/Service/Attraction'], '',
                                            '', '', '', result['Description'])
                results.append(new_row)
        # print(result['Description'])

    results_df = pd.concat(results, ignore_index=True)
    results_df.to_csv('output.csv', index=False, encoding='utf-8')

if __name__ == '__main__':
    main()