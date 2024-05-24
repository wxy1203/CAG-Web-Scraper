from bs4 import BeautifulSoup
import requests
import pandas as pd

def make_request(url: str):
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Failed to retrieve page: {e}")
        return None

def get_default_result():
    return {
        'Terminal': "",
        'Area': "",
        'Level': "",
        'Opening Hour': "",
        'outlets': [],
        'Description': ""
    }

def create_new_row(domain, facility, terminal, area, level, opening_hour, description):
    return pd.DataFrame({
        'Domain': [domain],
        'Facility/Service/Attraction': [facility],
        'Terminal': [terminal],
        'Area': [area],
        'Level': [level],
        'Opening Hour': [opening_hour],
        'Description': [description]
    })