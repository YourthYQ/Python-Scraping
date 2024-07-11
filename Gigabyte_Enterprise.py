import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib3.exceptions import InsecureRequestWarning

class ResponseHandler:
    @staticmethod
    def get_response(url, headers, payload):

        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
    
class ProductHandler:
    def __init__(self, products_urls, headers, payload):
        self.products_urls = products_urls
        self.headers = headers
        self.payload = payload
    
    def get_data_from_response(self):

        list_of_urls = self.products_urls

        scraped_data = []
        base_url = 'https://www.gigabyte.com'
        
        for url in list_of_urls:
            soup = ResponseHandler.get_response(url, self.headers, self.payload)

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

            # Find the products from next page
            next_page = soup.select_one('a.Button[title="Next"]')
            if next_page and next_page['href'] != 'javascript:void(0);': # a.href = 'javascript:void(0);' is the last page
                next_url = base_url + next_page['href']
                list_of_urls.append(next_url)

        return scraped_data

    def save_to_excel(self, data_list, filename):
        if data_list:
            df = pd.DataFrame(data_list)
            df.to_excel(filename + '.xlsx', index=False)
            print(f"Data has been exported to {filename}.xlsx")
        else:
            print("No data to write to Excel.")

if __name__ == "__main__":
    products_urls = [
        'https://www.gigabyte.com/Enterprise/Server-Motherboard',
        'https://www.gigabyte.com/Enterprise/Workstation-Motherboard',
        'https://www.gigabyte.com/Enterprise/Rack-Server',
        'https://www.gigabyte.com/Enterprise/GPU-Server',
        'https://www.gigabyte.com/Enterprise/High-Density-Server',
        'https://www.gigabyte.com/Enterprise/Tower-Server'
    ]
    payload = {}
    headers = {}
    product_handler = ProductHandler(products_urls, payload, headers)

    scraped_data_list = product_handler.get_data_from_response()
    product_handler.save_to_excel(scraped_data_list, 'Gigabyte_Enterprise')