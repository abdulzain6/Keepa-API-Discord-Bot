from dataclasses import dataclass
from typing import Set

@dataclass
class Seller:
    name: str
    id: str
    products: set
    
    @property
    def length_of_products(self):
        return len(self.products)
    
    def __hash__(self):
        return hash((self.name, self.id, tuple(self.products)))
    
    def __eq__(self, other):
        if isinstance(other, Seller):
            return (self.name, self.id, tuple(self.products)) == (other.name, other.id, tuple(other.products))
        return False
    
    def __str__(self) -> str:
        return f"Name : {self.name} | ID: {self.id} | Total Products: {self.length_of_products}"
    
def get_all_sellers_formatted(sellers_set: Set[str]) -> str:
    formatted_sellers = ""
    for i, seller in enumerate(sellers_set):
        formatted_sellers = f"{formatted_sellers}\n{i + 1}. {seller}"
    return formatted_sellers

def remove_seller_by_id(id: str, set_of_sellers: Set[Seller]):
    for seller in set_of_sellers:
        if seller.id == id:
            seller.remove(seller)
            return
            
            
            