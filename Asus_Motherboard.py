import requests
import pandas as pd
from urllib3.exceptions import InsecureRequestWarning

class ProductScraper:
    def __init__(self, data_url, headers):
        """Initialize ProductScraper class with data URL and headers."""
        self.data_url = data_url
        self.headers = headers

    def get_data_from_response(self, response):
        """Extract product data from API response."""
        quantity = response.json()["Result"]["TotalCount"]
        df = pd.DataFrame(columns=["Product Name", "Product URL"])
        for i in range(quantity):
            # Extract product name and URL from JSON response
            product_str = response.json()["Result"]["ProductList"][i]['Name']
            start_idx = product_str.find('>') + 1
            end_idx = product_str.rfind('<')
            product_name = product_str[start_idx:end_idx]
            product_url = response.json()["Result"]["ProductList"][i]["ProductURL"]

            # Append data to DataFrame
            df = df._append({"Product Name": product_name, "Product URL": product_url}, ignore_index=True)
        return df 

    def get_response(self):
        """Fetch product data from the specified URL using HTTP GET request."""
        # Disable SSL warnings and make HTTP GET request
        requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)
        response = requests.request("GET", self.data_url, headers=self.headers, verify=False)

        # Extract data from response
        return self.get_data_from_response(response)   

def main():
    # Create an empty DataFrame to store product data
    final_df = pd.DataFrame(columns=["Product Name", "Product URL"])

    # Create a dictionary for all the categories and subcategories of products
    product_categories = {
        "motherboards-components": ["motherboards"],
        "networking-iot-servers": ["servers"],
        "laptops": ["for-home", "for-work", "for-creators", "for-students", "for-gaming"],
        "displays-desktops": ["all-in-one-pcs", "tower-pcs", "gaming-tower-pcs", "nucs", "mini-pcs", "workstations"]
    }
    
    # Iterate over categories and subcategories
    for category in product_categories.keys():
            subcategories = product_categories[category]
            for sub_cat in subcategories:

                # Construct data URL for each category and subcategory
                data_url = f"https://odinapi.asus.com/recent-data/apiv2/SeriesFilterResult?SystemCode=asus&WebsiteCode=global&ProductLevel1Code={category}&ProductLevel2Code={sub_cat}"
                agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                cookie = "BIGipServerodinapi.asus.com_443=834934444.47873.0000"

                # Define user agent and cookie for HTTP request headers
                headers = {
                    "User-Agent": agent,
                    "Cookie": cookie
                }

                # Instantiate ProductScraper and fetch product data
                scraper = ProductScraper(data_url, headers)
                df = scraper.get_response()

                # Append product data to final DataFrame
                final_df = final_df._append(df, ignore_index=True)

    # Return the DataFrame instead of saving it to an Excel file
    return final_df

if __name__ == "__main__":
    final_df = main()
    print(final_df)