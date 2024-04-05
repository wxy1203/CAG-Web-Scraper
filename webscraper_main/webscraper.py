from bs4 import BeautifulSoup
import pandas as pd
import re
import requests

def scrape_text(url: str) -> str:
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        response.raise_for_status()

    except requests.RequestException as e:
        return f"Failed to retrieve page: {e}"

    soup = BeautifulSoup(response.content, 'html.parser')

    main_content = soup.find('main')

    text = main_content.get_text(separator=" ").strip()

    text = re.sub('\s+', ' ', text)
    return text

def main():
    df = pd.read_excel('Pages to crawl.xlsx', sheet_name=0)

    results_df = pd.DataFrame(columns=['Content', 'Source'])

    for url in df['Weblink']:
        text = scrape_text(url)

        new_row = pd.DataFrame({'Content': [text], 'Source': [url]})

        results_df = pd.concat([results_df, new_row], ignore_index=True)

    results_df.to_csv('output.csv', index=False, encoding='utf-8-sig')

if __name__ == '__main__':
    main()