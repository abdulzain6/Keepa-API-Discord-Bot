from statistics import mean
import discord
import keepa
import requests, os


api_key = os.getenv("KEEPA_KEY")

class KeepaApiClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.keepaAPI = keepa.Keepa(api_key)

    def get_seller_name(self, seller_id: str):
        try:
            results = self.keepaAPI.seller_query(seller_id=seller_id)[seller_id]
            return results["sellerName"]
        except Exception as e:
            return "Not Found"

    def get_seller_products(self, seller_id: str) -> set:
        results = self.keepaAPI.seller_query(seller_id=seller_id, storefront=True)[seller_id]
        return set(results["asinList"])

    def get_product_details(self, asin: str) -> dict:
        product_data: dict = self.keepaAPI.query(items=[asin], offers=100, stats=100)[0]
        buy_box_price = product_data.get("stats", {}).get("buyBoxPrice", "")
        avg = product_data.get("stats", {}).get("avg90", [])
        offers = product_data.get("stats", {}).get("totalOfferCount", "")
        avg.remove(-1)
        try:
            sales_rank = product_data.get("stats", {}).get("current", "")[3]
        except:
            sales_rank = -1
            
        print(product_data.get("title", ""))
        return {
            "ASIN": product_data.get("asin", ""),
            "Brand": product_data.get("brand", ""),
            "Category": self.get_category_name(product_data.get("categories", [""])[0]),
            "Sales rank": sales_rank,
            "Buy Box Price": buy_box_price / 100 if buy_box_price != -1 else buy_box_price,
            "Avg. 90-day": mean(avg) / 100,
            "Offers": offers,
            "Google title": product_data.get("title", ""),
            "Google model": product_data.get("model", ""),
            "UPC": product_data.get("eanList", [""])[0],
            "Image": f"https://images-na.ssl-images-amazon.com/images/I/{product_data.get('imagesCSV', [''])}"
        }, product_data
        
    def get_category_name(self, id: int):
        try:
            data = self.keepaAPI.category_lookup(id)
            return data[str(id)]["name"]
        except:
            return ""

    

    def get_product_price_graph(self, asin, domain_id="com", filename="plot.png", **kwargs):
        url = "https://api.keepa.com/graphimage"
        params = {
            "key": self.api_key,
            "domain": domain_id,
            "asin": asin,
        }
        params.update(kwargs)
        response = requests.get(url, params=params)
        with open(filename, "wb") as file:
            file.write(response.content)
        with open(filename, 'rb') as f:
            file = discord.File(f, filename=filename)
        return file
            
        
if __name__ == "__main__":
    c = KeepaApiClient(api_key)
    print(c.get_product_price_graph(asin="B01MTWGMRR", salesrank=1, bb=1, fba=1, fbm=1))