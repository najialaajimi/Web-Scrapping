import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import sys  # Importer sys pour récupérer les arguments de la ligne de commande

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')  # Assurez-vous que MongoDB est en cours d'exécution
db = client['product_comparator']  # Base de données MongoDB
collection = db['products']  # Collection pour stocker les produits

# Fonction pour vérifier si le produit existe déjà dans MongoDB
def product_exists(name, website):
    return collection.find_one({'Name': name, 'Website': website})

# Fonction de recherche de produit par nom dans MongoDB
def search_product_by_name(product_name):
    escaped_name = re.escape(product_name)
    results = collection.find({'Name': {'$regex': escaped_name, '$options': 'i'}})
    return list(results)

# Fonction pour scraper TDISCOUNT
def scrape_tdiscount():
    url = "https://tdiscount.tn/smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
            if product_exists(name, 'TDISCOUNT'):
                continue  # Si le produit existe déjà, on passe au suivant
        except AttributeError:
            name = None

        try:
            price = item.select_one('.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('meta[itemprop="description"]')['content']
        except (AttributeError, TypeError):
            description = None

        try:
            image_url = item.select_one('meta[itemprop="image"]')['content']
        except (AttributeError, TypeError):
            image_url = None

        try:
            availability = item.select_one('meta[itemprop="availability"]')['content']
        except (AttributeError, TypeError):
            availability = None

        try:
            product_url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            product_url = None

        product = {
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Availability': availability,
            'URL': f"{product_url}" if product_url else None,
            'Website': 'TDISCOUNT'
        }

        collection.insert_one(product)  # Ajouter le produit à la base de données
        products.append(product)

    return products

# Fonction pour scraper Tunisianet
def scrape_tunisianet():
    url = "https://www.tunisianet.com.tn/596-smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
            if product_exists(name, 'Tunisianet'):
                continue  # Si le produit existe déjà, on passe au suivant
        except AttributeError:
            name = None

        try:
            price = item.select_one('span.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('.product-description').text.strip()
        except AttributeError:
            description = None

        try:
            image_url = item.select_one('img')['data-full-size-image-url']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            availability = item.select_one('.in-stock').text.strip() if item.select_one('.in-stock') else "Out of stock"
        except AttributeError:
            availability = None

        product = {
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Product URL': f"{product_url}" if product_url else None,
            'Availability': availability,
            'Website': 'Tunisianet'
        }

        collection.insert_one(product)  # Ajouter le produit à la base de données
        products.append(product)

    return products

# Fonction pour scraper Ubuy
def scrape_ubuy():
    url = "https://www.ubuy.tn/en/category/mobile-phones-21453?ref=hm-explore-category"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.listing-product'):
        try:
            name = item.select_one('.product-title').text.strip()
            if product_exists(name, 'Ubuy'):
                continue  # Si le produit existe déjà, on passe au suivant
        except AttributeError:
            name = None

        try:
            price = item.select_one('.product-price').text.strip().replace('TND', '').strip()
        except AttributeError:
            price = None

        try:
            image_url = item.select_one('img')['src']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('a.product-img')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            brand = item.select_one('.brand').text.strip()
        except AttributeError:
            brand = None

        product = {
            'Name': name,
            'Price': price,
            'Image URL': image_url,
            'Product URL': f"{product_url}" if product_url else None,
            'Brand': brand,
            'Website': 'Ubuy'
        }

        collection.insert_one(product)  # Ajouter le produit à la base de données
        products.append(product)

    return products

# Fonction principale pour exécuter tous les scrapers
def main():
    print("Starting the scraping process...")

    # Récupérer le nom du produit passé en argument dans la ligne de commande
    if len(sys.argv) < 2:
        print("Error: Product name must be passed as an argument.")
        return
    product_name = sys.argv[1].strip()

    # Scraper les données des trois sites
    tdiscount_data = scrape_tdiscount()
    tunisianet_data = scrape_tunisianet()
    ubuy_data = scrape_ubuy()

    # Filtrer les produits selon le nom passé en argument
    all_data = tdiscount_data + tunisianet_data + ubuy_data
    filtered_products = [product for product in all_data if product_name.lower() in product['Name'].lower()]

    # Afficher les résultats trouvés
    print(filtered_products)  # Retourne les produits trouvés sous forme de JSON

if __name__ == "__main__":
    main()



""" import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import sys  # Importer sys pour récupérer les arguments de la ligne de commande

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')  # Assurez-vous que MongoDB est en cours d'exécution
db = client['product_comparator']  # Base de données MongoDB
collection = db['products']  # Collection pour stocker les produits

# Fonction pour vérifier si le produit existe déjà dans MongoDB
def product_exists(name, website):
    return collection.find_one({'Name': name, 'Website': website})

# Fonction de recherche de produit par nom dans MongoDB
def search_product_by_name(product_name):
    escaped_name = re.escape(product_name)
    results = collection.find({'Name': {'$regex': escaped_name, '$options': 'i'}})
    return list(results)

# Fonction pour scraper TDISCOUNT
def scrape_tdiscount():
    url = "https://tdiscount.tn/smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
            if product_exists(name, 'TDISCOUNT'):
                continue  # Si le produit existe déjà, on passe au suivant
        except AttributeError:
            name = None

        try:
            price = item.select_one('.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('meta[itemprop="description"]')['content']
        except (AttributeError, TypeError):
            description = None

        try:
            image_url = item.select_one('meta[itemprop="image"]')['content']
        except (AttributeError, TypeError):
            image_url = None

        try:
            availability = item.select_one('meta[itemprop="availability"]')['content']
        except (AttributeError, TypeError):
            availability = None

        try:
            product_url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            product_url = None

        product = {
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Availability': availability,
            'URL': f"https://tdiscount.tn{product_url}" if product_url else None,
            'Website': 'TDISCOUNT'
        }

        collection.insert_one(product)  # Ajouter le produit à la base de données
        products.append(product)

    return products

# Fonction pour scraper Tunisianet
def scrape_tunisianet():
    url = "https://www.tunisianet.com.tn/596-smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
            if product_exists(name, 'Tunisianet'):
                continue  # Si le produit existe déjà, on passe au suivant
        except AttributeError:
            name = None

        try:
            price = item.select_one('span.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('.product-description').text.strip()
        except AttributeError:
            description = None

        try:
            image_url = item.select_one('img')['data-full-size-image-url']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            availability = item.select_one('.in-stock').text.strip() if item.select_one('.in-stock') else "Out of stock"
        except AttributeError:
            availability = None

        product = {
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Product URL': f"https://www.tunisianet.com.tn{product_url}" if product_url else None,
            'Availability': availability,
            'Website': 'Tunisianet'
        }

        collection.insert_one(product)  # Ajouter le produit à la base de données
        products.append(product)

    return products

# Fonction pour scraper Ubuy
def scrape_ubuy():
    url = "https://www.ubuy.tn/en/category/mobile-phones-21453?ref=hm-explore-category"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.listing-product'):
        try:
            name = item.select_one('.product-title').text.strip()
            if product_exists(name, 'Ubuy'):
                continue  # Si le produit existe déjà, on passe au suivant
        except AttributeError:
            name = None

        try:
            price = item.select_one('.product-price').text.strip().replace('TND', '').strip()
        except AttributeError:
            price = None

        try:
            image_url = item.select_one('img')['src']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('a.product-img')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            brand = item.select_one('.brand').text.strip()
        except AttributeError:
            brand = None

        product = {
            'Name': name,
            'Price': price,
            'Image URL': image_url,
            'Product URL': f"https://www.ubuy.tn{product_url}" if product_url else None,
            'Brand': brand,
            'Website': 'Ubuy'
        }

        collection.insert_one(product)  # Ajouter le produit à la base de données
        products.append(product)

    return products

# Fonction principale pour exécuter tous les scrapers
def main():
    print("Starting the scraping process...")

    # Récupérer le nom du produit passé en argument dans la ligne de commande
    if len(sys.argv) < 2:
        print("Error: Product name must be passed as an argument.")
        return
    product_name = sys.argv[1].strip()

    # Scraper les données des trois sites
    tdiscount_data = scrape_tdiscount()
    tunisianet_data = scrape_tunisianet()
    ubuy_data = scrape_ubuy()

    # Filtrer les produits selon le nom passé en argument
    all_data = tdiscount_data + tunisianet_data + ubuy_data
    filtered_products = [product for product in all_data if product_name.lower() in product['Name'].lower()]

    # Afficher les résultats trouvés
    print(filtered_products)  # Retourne les produits trouvés sous forme de JSON

if __name__ == "__main__":
    main()

 """


""" import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')  # Assurez-vous que MongoDB est en cours d'exécution sur le port 27017
db = client['product_comparator']  # Base de données MongoDB
collection = db['products']  # Collection pour stocker les produits

# Fonction de recherche de produit par nom
def search_product_by_name(product_name):
    results = collection.find({'Name': {'$regex': product_name, '$options': 'i'}})  # Recherche insensible à la casse
    return list(results)

# Fonction pour scrapper TDISCOUNT
def scrape_tdiscount():
    url = "https://tdiscount.tn/smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
        except AttributeError:
            name = None

        try:
            price = item.select_one('.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('meta[itemprop="description"]')['content']
        except (AttributeError, TypeError):
            description = None

        try:
            image_url = item.select_one('meta[itemprop="image"]')['content']
        except (AttributeError, TypeError):
            image_url = None

        try:
            availability = item.select_one('meta[itemprop="availability"]')['content']
        except (AttributeError, TypeError):
            availability = None

        try:
            url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            url = None

        products.append({
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Availability': availability,
            'URL': url,
            'Website': 'TDISCOUNT'
        })

    return products

# Fonction pour scrapper Tunisianet
def scrape_tunisianet():
    url = "https://www.tunisianet.com.tn/596-smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
        except AttributeError:
            name = None

        try:
            price = item.select_one('span.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('.product-description').text.strip()
        except AttributeError:
            description = None

        try:
            image_url = item.select_one('img')['data-full-size-image-url']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            availability = item.select_one('.in-stock').text.strip() if item.select_one('.in-stock') else "Out of stock"
        except AttributeError:
            availability = None

        products.append({
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Product URL': product_url,
            'Availability': availability,
            'Website': 'Tunisianet'
        })

    return products

# Fonction pour scrapper Ubuy
def scrape_ubuy():
    url = "https://www.ubuy.tn/en/category/mobile-phones-21453?ref=hm-explore-category"
    service = Service('C:/chromedriver/chromedriver.exe')  # Remplacez par le chemin correct
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(3)  # Attendre que le contenu dynamique soit chargé

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    products = []

    for item in soup.select('.listing-product'):
        try:
            name = item.select_one('.product-title').text.strip()
        except AttributeError:
            name = None

        try:
            price = item.select_one('.product-price').text.strip().replace('TND', '').strip()
        except AttributeError:
            price = None

        try:
            image_url = item.select_one('img')['src']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('a.product-img')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            brand = item.select_one('.brand').text.strip()
        except AttributeError:
            brand = None

        products.append({
            'Name': name,
            'Price': price,
            'Image URL': image_url,
            'Product URL': f"https://www.ubuy.tn{product_url}" if product_url else None,
            'Brand': brand,
            'Website': 'Ubuy'
        })

    return products

# Fonction pour stocker les produits dans MongoDB
def store_products(products):
    for product in products:
        existing_product = collection.find_one({'Name': product['Name'], 'Website': product['Website']})
        if not existing_product:
            collection.insert_one(product)
            print(f"Product {product['Name']} from {product['Website']} saved to MongoDB.")
        else:
            print(f"Product {product['Name']} already exists in MongoDB.")

# Fonction principale pour exécuter tous les scrapers et filtrer les résultats
def main():
    print("Starting the scraping process...")

    # Scrape data from all three websites
    tdiscount_data = scrape_tdiscount()
    tunisianet_data = scrape_tunisianet()
    ubuy_data = scrape_ubuy()

    # Combine all the data into one list
    all_data = tdiscount_data + tunisianet_data + ubuy_data

    # Limite à au moins 20 produits
    if len(all_data) > 20:
        all_data = all_data[:20]

    # Stocke les produits dans MongoDB
    store_products(all_data)

    # Recherche d'un produit par nom
    product_name = input("Enter the product name to search: ")
    found_products = search_product_by_name(product_name)

    if found_products:
        print(f"Found {len(found_products)} product(s):")
        for product in found_products:
            print(f"Name: {product['Name']}, Price: {product['Price']}, Website: {product['Website']}")
    else:
        print(f"No products found for '{product_name}'.")

    print(f"Total products saved: {len(all_data)}")

# Exécuter la fonction principale
if __name__ == "__main__":
    main()
 """

""" import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
from pymongo import MongoClient

# Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017')  # Assurez-vous que MongoDB est en cours d'exécution sur le port 27017
db = client['product_comparator']  # Base de données MongoDB
collection = db['products']  # Collection pour stocker les produits

# Function to scrape TDISCOUNT
def scrape_tdiscount():
    url = "https://tdiscount.tn/smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
        except AttributeError:
            name = None

        try:
            price = item.select_one('.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('meta[itemprop="description"]')['content']
        except (AttributeError, TypeError):
            description = None

        try:
            image_url = item.select_one('meta[itemprop="image"]')['content']
        except (AttributeError, TypeError):
            image_url = None

        try:
            availability = item.select_one('meta[itemprop="availability"]')['content']
        except (AttributeError, TypeError):
            availability = None

        try:
            url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            url = None

        products.append({
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Availability': availability,
            'URL': url,
            'Website': 'TDISCOUNT'
        })

    return products


# Function to scrape Tunisianet
def scrape_tunisianet():
    url = "https://www.tunisianet.com.tn/596-smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        try:
            name = item.select_one('.product-title a').text.strip()
        except AttributeError:
            name = None

        try:
            price = item.select_one('span.price').text.strip()
        except AttributeError:
            price = None

        try:
            description = item.select_one('.product-description').text.strip()
        except AttributeError:
            description = None

        try:
            image_url = item.select_one('img')['data-full-size-image-url']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('.product-title a')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            availability = item.select_one('.in-stock').text.strip() if item.select_one('.in-stock') else "Out of stock"
        except AttributeError:
            availability = None

        products.append({
            'Name': name,
            'Price': price,
            'Description': description,
            'Image URL': image_url,
            'Product URL': product_url,
            'Availability': availability,
            'Website': 'Tunisianet'
        })

    return products


# Function to scrape Ubuy
def scrape_ubuy():
    url = "https://www.ubuy.tn/en/category/mobile-phones-21453?ref=hm-explore-category"
    service = Service('C:/chromedriver/chromedriver.exe')  # Remplacez par le chemin correct
    driver = webdriver.Chrome(service=service)
    driver.get(url)
    time.sleep(3)  # Attendre que le contenu dynamique soit chargé

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    products = []

    for item in soup.select('.listing-product'):
        try:
            name = item.select_one('.product-title').text.strip()
        except AttributeError:
            name = None

        try:
            price = item.select_one('.product-price').text.strip().replace('TND', '').strip()
        except AttributeError:
            price = None

        try:
            image_url = item.select_one('img')['src']
        except (AttributeError, TypeError):
            image_url = None

        try:
            product_url = item.select_one('a.product-img')['href']
        except (AttributeError, TypeError):
            product_url = None

        try:
            brand = item.select_one('.brand').text.strip()
        except AttributeError:
            brand = None

        products.append({
            'Name': name,
            'Price': price,
            'Image URL': image_url,
            'Product URL': f"https://www.ubuy.tn{product_url}" if product_url else None,
            'Brand': brand,
            'Website': 'Ubuy'
        })

    return products


# Function to store products in MongoDB
def store_products(products):
    for product in products:
        existing_product = collection.find_one({'Name': product['Name'], 'Website': product['Website']})
        if not existing_product:
            collection.insert_one(product)
            print(f"Product {product['Name']} from {product['Website']} saved to MongoDB.")
        else:
            print(f"Product {product['Name']} already exists in MongoDB.")


# Main function to run all scrapers and filter results
def main():
    print("Starting the scraping process...")

    # Scrape data from all three websites
    tdiscount_data = scrape_tdiscount()
    tunisianet_data = scrape_tunisianet()
    ubuy_data = scrape_ubuy()

    # Combine all the data into one list
    all_data = tdiscount_data + tunisianet_data + ubuy_data

    # Limit to at least 20 products
    if len(all_data) > 20:
        all_data = all_data[:20]

    # Store products in MongoDB
    store_products(all_data)

    # Display data
    for product in all_data:
        print(f"Name: {product['Name']}, Price: {product['Price']}, Website: {product['Website']}")

    print(f"Total products saved: {len(all_data)}")


# Run the main function
if __name__ == "__main__":
    main() """


""" import requests
from bs4 import BeautifulSoup
import sys
import json

# Lecture du paramètre passé (nom du produit)
product_name = sys.argv[1] if len(sys.argv) > 1 else ''

# Fonction pour scrapper TDISCOUNT
def scrape_tdiscount(product_name):
    url = "https://tdiscount.tn/smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        name = item.select_one('.product-title a').text.strip()
        if product_name.lower() in name.lower():  # Recherche par nom
            price = item.select_one('.price').text.strip()
            description = item.select_one('meta[itemprop="description"]')['content']
            image_url = item.select_one('meta[itemprop="image"]')['content']
            availability = item.select_one('meta[itemprop="availability"]')['content']
            url = item.select_one('.product-title a')['href']

            products.append({
                'Name': name,
                'Price': price,
                'Description': description,
                'Image URL': image_url,
                'Availability': availability,
                'URL': url,
                'Website': 'TDISCOUNT'
            })

    return products

# Fonction pour scrapper Tunisianet
def scrape_tunisianet(product_name):
    url = "https://www.tunisianet.com.tn/596-smartphone-tunisie"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.product-miniature'):
        name = item.select_one('.product-title a').text.strip()
        if product_name.lower() in name.lower():
            price = item.select_one('span.price').text.strip()
            description = item.select_one('.product-description').text.strip()
            image_url = item.select_one('img')['data-full-size-image-url']
            product_url = item.select_one('.product-title a')['href']
            availability = item.select_one('.in-stock').text.strip() if item.select_one('.in-stock') else "Out of stock"

            products.append({
                'Name': name,
                'Price': price,
                'Description': description,
                'Image URL': image_url,
                'Product URL': product_url,
                'Availability': availability,
                'Website': 'Tunisianet'
            })

    return products

# Fonction pour scrapper Ubuy
def scrape_ubuy(product_name):
    url = "https://www.ubuy.tn/en/category/mobile-phones-21453?ref=hm-explore-category"
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, 'html.parser')

    products = []

    for item in soup.select('.listing-product'):
        name = item.select_one('.product-title').text.strip()
        if product_name.lower() in name.lower():
            price = item.select_one('.product-price').text.strip().replace('TND', '').strip()
            image_url = item.select_one('img')['src']
            product_url = item.select_one('a.product-img')['href']
            brand = item.select_one('.brand').text.strip()

            products.append({
                'Name': name,
                'Price': price,
                'Image URL': image_url,
                'Product URL': f"https://www.ubuy.tn{product_url}" if product_url else None,
                'Brand': brand,
                'Website': 'Ubuy'
            })

    return products

# Scraping et collecte des données
def main():
    all_products = []

    if product_name:
        # Scraper les trois sites avec le nom de produit
        all_products += scrape_tdiscount(product_name)
        all_products += scrape_tunisianet(product_name)
        all_products += scrape_ubuy(product_name)

    print(json.dumps(all_products))  # Affiche la liste de tous les produits trouvés sous forme de JSON

if __name__ == "__main__":
    main()
 """