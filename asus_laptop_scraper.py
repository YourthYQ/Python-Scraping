import requests
from bs4 import BeautifulSoup
import csv

list_of_urls = [
    'https://www.gigabyte.com/Enterprise/Server-Motherboard',
    'https://www.gigabyte.com/Enterprise/Workstation-Motherboard',
    'https://www.gigabyte.com/Enterprise/Rack-Server',
    'https://www.gigabyte.com/Enterprise/GPU-Server',
    'https://www.gigabyte.com/Enterprise/High-Density-Server',
    'https://www.gigabyte.com/Enterprise/Tower-Server'
]

scraped_data = []

base_url = 'https://www.gigabyte.com'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

session = requests.Session()

def start_scrape():
    for url in list_of_urls:
        try:
            response = session.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to retrieve {url}: {e}")
            continue
        
        if response.status_code == 200:
            # Parse Data
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract products with only one series
            single_products = soup.select('div.Content-Area-ResultItem.Grid-System-ResultItem.js-splide-Slider.Grid-System-OnlyParent')
            for product in single_products:
                element = product.select_one('a.ResultItem-ParentInfo-ModelNameMobile.haveLink')
                
                if element:
                    title = element.get_text(strip=True)
                    url = element['href']

                    # Add to data output
                    scraped_data.append({
                        'title': title,
                        'url': base_url + url
                    })
            
            # Extract products with series
            multiple_products = soup.select('ul.splide__list')
            for product in multiple_products:
                container = product.select('a.Content-ModelChildItem-ModelNameRow')
                for element in container:
                    title = element.get_text(strip=True)
                    url = element['href']

                    # Add to data output
                    scraped_data.append({
                        'title': title,
                        'url': base_url + url
                    })

            next_page = soup.select_one('a.Button[title="Next"]')
            if next_page and next_page['href'] != 'javascript:void(0);': # a.href = 'javascript:void(0);' is the last page
                next_url = base_url + next_page['href']
                list_of_urls.append(next_url)

        else:
            print(f"Failed to retrieve {url}, status code: {response.status_code}")

def save_to_csv(data_list, filename):
    if data_list:
        keys = data_list[0].keys()
        with open(filename + '.csv', 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data_list)
    else:
        print("No data to write to CSV.")

if __name__ == '__main__':
    start_scrape()
    save_to_csv(scraped_data, 'Gigabyte_Enterprise')