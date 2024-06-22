from woocommerce import API
from databases.database import Base, FlatsSaleObjectsData, Databases
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from project_configs.configurations import load_bd_configs, load_woo_configs

class WooCommerceFunction:
    def __init__ (self, url):
       self.username_bd, self.password_bd, self.host_bd, self.port_bd, self.database_bd = load_bd_configs()
       self.consumer_key, self.consumer_secret, self.wp_url = load_woo_configs()
       self.url = url

    def woo_load_product_data(self, url):
        engine = create_engine(f"mysql+mysqlconnector://{self.username_bd}:{self.password_bd}@{self.host_bd}:{self.port_bd}/{self.database_bd}")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        data_dict, product_pictures = Databases.get_data_by_url(FlatsSaleObjectsData, Session, url)
        return data_dict, product_pictures
    
    
    def woo_create_product_data(self):
        data_dict, product_pictures = WooCommerceFunction.woo_load_product_data(self.url)
        return {
            "name": data_dict["title"],
            "type": "simple",
            "regular_price": str(data_dict["price"]),
            "description": data_dict["description"],
            "categories": [
                {"price_m2": data_dict["price_m2"],
                    "num_rooms": data_dict["number_of_rooms"],
                    "separated_rooms": data_dict["separated_rooms"],
                    "all_rooms_separated": data_dict["all_rooms_separated"],
                    "number_of_floor": data_dict["floors"],
                    "number_of_storeys": data_dict["number_of_floors"],
                    "floor_no_first": data_dict["floor_no_first"],
                    "floor_no_last": data_dict["floor_no_last"],
                    "floor_last": data_dict["floor_last"],
                    "total_area": data_dict["total_area"],
                    "living_area": data_dict["living_area"],
                    "kitchen_area": data_dict["kitchen_area"],
                    "balcony": data_dict["balcony"],
                    "bath": data_dict["bathroom"],
                    "plan_type": data_dict["project"],
                    "repair": data_dict["type_of_finishing"],
                    "walls_material": data_dict["type_of_layout"],
                    "celling_heights": data_dict["celling_heights"],
                    "furniture": data_dict["furniture"],
                }
            ],
            "meta_data": [
                {"key": "district", "value": data_dict["district"]},
                {"key": "region", "value": data_dict["region"]},
                {"key": "subregion", "value": data_dict["furniture"]},
                {"key": "location_city", "value": data_dict["location_city"]},
                {"key": "location_street", "value": data_dict["location_street"]},
                {"key": "house_number", "value": data_dict["house_number"]},
                {"key": "location_coordinates", "value": data_dict["location_coordinates"]},
                {"key": "contract_number", "value": data_dict["contract_number"]},
                {"key": "terms_of_sale", "value": data_dict["terms_of_sale"]},
                {"key": "ownership", "value": data_dict["ownership"]}
            ],
        }
        
    
    def woo_create_api(self):
        return API(
            url=self.wp_url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
        )
        

    def woo_create_product(self, Session, product_data):
        wcapi = WooCommerceFunction.woo_create_api()
        response = wcapi.post("products", product_data)
        response_data = response.json()
        if response.status_code == 201:
            print('Товар создан:', response_data.get('id'))
            return response_data.get('id')
        else:
            print('Ошибка при создании товара:', response.status_code, response.text)


    def woo_product_add_pictures(self, product_id):
        wcapi = WooCommerceFunction.woo_create_api()
        data_dict, product_pictures = WooCommerceFunction.woo_load_product_data(self.url)
        product = wcapi.get(f"products/{product_id}").json()
        existing_images = product.get("images", [])
        new_images = [{"src": url} for url in product_pictures]
        updated_images = existing_images + new_images
        data = {"images": updated_images}
        wcapi.put(f"products/{product_id}", data)