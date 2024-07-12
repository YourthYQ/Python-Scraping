import requests 
import pandas as pd
from bs4 import BeautifulSoup 
from urllib3.exceptions import InsecureRequestWarning

class ResponseHandler:   
    @staticmethod
    def get_response(url, headers, payload):
        """Fetches and parses the HTML content of a page."""
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup

class ProductHandler:
    def __init__(self, products_urls, headers, payload):
        self.products_urls = products_urls
        self.headers = headers
        self.payload = payload

    def get_total_page(self, products_url):
        """Get the total number of pages for a given product URL."""
        soup = ResponseHandler.get_response(products_url, self.headers, self.payload)
        if soup.find('span', attrs={'class':'pageMaximumPage'}) is not None:
            total_page = int(soup.find('span', attrs={'class':'pageMaximumPage'}).text)
        else:
            total_page = 1
        return total_page
    
    @staticmethod
    def extract_product_info(row):
        """Extract product information from a row."""
        product_url = "https://www.gigabyte.com" + row.find('a', href=True)['href']
        product_name = row.find('a', href=True).text.replace('\n','')
        return {"Product Name": product_name, "Product URL": product_url} 
    
    def get_data_from_response(self, products_url):
        # Fetches product data from all pages of a given URL
        total_page = self.get_total_page(products_url)
        df = pd.DataFrame(columns=["Product Name", "Product URL"])
        for page in range(1, total_page+1):
            product_page_url = f"{products_url}?page={page}"
            soup = ResponseHandler.get_response(product_page_url, self.headers, self.payload)
            table = soup.find('div', attrs={'class':'product_list_row StyleCardBox4'})
            for row in table.findAll('div', attrs={'class':'product_info_text_col'}):
                product_info = self.extract_product_info(row)
                df = df._append(product_info, ignore_index=True)
        return df
    
    def get_combined_data(self):
        """Combines all product data into a single DataFrame."""
        final_df = pd.DataFrame(columns=["Product Name", "Product URL"])
        for products_url in self.products_urls:
            df = self.get_data_from_response(products_url) 
            final_df = final_df._append(df, ignore_index=True)
        return final_df

if __name__ == "__main__":
    products_urls = [
        "https://www.gigabyte.com/Motherboard/All-Series", 
        "https://www.gigabyte.com/Gaming-PC", 
        "https://www.gigabyte.com/Mini-PcBarebone/All", 
        "https://www.gigabyte.com/Laptop/All-Series"
    ]
    payload = {}
    headers = {}
    product_handler = ProductHandler(products_urls, payload, headers)
    final_df = product_handler.get_combined_data()
    # Return the DataFrame instead of saving it to an Excel file
    print(final_df)