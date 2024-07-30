import requests as rs
from bs4 import BeautifulSoup
import os
import csv
from urllib.parse import urljoin


def get_apartment_data(min_price=0, max_price=0, min_sqm=0, max_sqm=999, out_dir="./"):
    base_url = "https://www.4zida.rs/"
    parameters = f"prodaja-stanova?jeftinije_od={max_price}eur&vece_od={min_sqm}m2&manje_od=60m2{max_sqm}m2&skuplje_od={min_price}eur"

    os.makedirs(out_dir, exist_ok=True)

    page = 1
    while True:
        url = urljoin(base_url, parameters + f"&strana={page}")
        response = rs.get(url)
        
        if len(response.text) < 200000:
            print(f"Seems like list is over\nPage {page}")
            break
        
        filename = os.path.join(out_dir, f"out{page}.txt")
        try:
            with open(filename, "w") as file:
                file.write(response.text)
        except Exception as e:
            print(f"An error occurred: {e}")
            break
        
        page += 1
    
    total_processed, total_added = aggregate_csv(out_dir)
    print(f"Total processed: {total_processed}, Total added: {total_added}")


def list_txts(path):
    return [f for root, dirs, files in os.walk(path) for f in files if f.endswith('.txt')]


def extract_apartment_data(file_name, output_file='output.csv'):
    with open(file_name, 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    cards = soup.select('div[class^="relative flex h-[180px]"]')
    apartments = []

    for card in cards:
        link_tag = card.find('a', class_='flex justify-between gap-1')
        if link_tag:
            link = link_tag['href']
            if not link.startswith("https://www.4zida.rs"):
                link = "https://www.4zida.rs" + link
        else:
            link = 'No link'
        #link_formula = '=HYPERLINK(' + '"' + link + '"' + ', "Link")'

        preview_tag = card.find('img', class_='object-cover')
        preview = preview_tag['src'] if preview_tag else 'No image'
        #preview_formula = '=IMAGE(' + '"' + preview + '"' + ',, 1)'

        address_tag = card.find('p', class_='line-clamp-2 text-wrap text-xs !leading-tight text-foreground/60 desk:line-clamp-3 desk:text-sm')
        address = address_tag.text.strip() if address_tag else 'No address'
        address = clean_address(address)

        price_tag = card.find('p', class_='rounded-tl bg-spotlight px-2 py-1 text-lg font-bold desk:text-2xl')
        price = price_tag.text.strip() if price_tag else 'No price'
        price = price.replace('.', '').replace('€', '').strip()

        price_per_sqm_tag = card.find('p', class_='rounded-bl border border-spotlight bg-spotlight-300 px-2 text-2xs font-medium text-spotlight-700 desk:text-xs')
        price_per_sqm = price_per_sqm_tag.text.strip() if price_per_sqm_tag else 'No price per sqm'
        price_per_sqm = price_per_sqm.replace('.', '').replace('€/m²', '').strip()

        try:
            area = round(int(price) / int(price_per_sqm))
        except ValueError:
            area = 'No area'

        apartments.append({
            'Preview': preview,
            'Address': address,
            'Price': price,
            'Price per square': price_per_sqm,
            'Area': area,
            'Link': link,
        })

    added_count = write_to_csv(apartments, output_file)
    return len(apartments), added_count


def clean_address(address):
    address = address.replace('"', '').replace('Gradske lokacije,', '').strip()
    if address.endswith(','):
        address = address[:-1].strip()
    address_parts = address.split(',')
    address_parts = [part.strip() for part in address_parts if part.strip()]
    return ', '.join(reversed(address_parts))


def write_to_csv(apartments, output_file):
    added_count = 0
    with open(output_file, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Preview', 'Address', 'Price', 'Price per square', 'Area', 'Link', 'Posted']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if csvfile.tell() == 0:
            writer.writeheader()
        
        existing_links = set()
        if os.path.exists(output_file):
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                existing_links = {row['Link'] for row in reader}

        for apartment in apartments:
            if apartment['Link'] not in existing_links:
                writer.writerow(apartment)
                added_count += 1
    
    return added_count


def aggregate_csv(in_path="./"):
    total_processed = 0
    total_added = 0
    for file_name in list_txts(in_path):
        processed, added = extract_apartment_data(os.path.join(in_path, file_name))
        total_processed += processed
        total_added += added
        os.remove(os.path.join(in_path, file_name))
    return total_processed, total_added


get_apartment_data(20000, 50000, 40, 100, "./Temp/")
