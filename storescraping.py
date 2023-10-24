import requests
import re
import pandas as pd
from bs4 import BeautifulSoup
import pykakasi

# each page execute javascript to embed googlemap
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# kakashi converter from Kanji to Alphabet
kks = pykakasi.kakasi()

def kana(s):
    r = []
    for kana in kks.convert(s):
        r.append(kana["hepburn"])
    return "-".join(r)

def get_store_list():
    stores = []
    shop_list = "https://www.kakuyasu.co.jp/store/app/shop/shop_list/"
    r = requests.get(shop_list)
    soup = BeautifulSoup(r.content, "html.parser")

    for area in soup.select("h4.base-h4"):
        div = area.find_next_sibling("div")

        for i, store in enumerate(div.select("a.base-normal-link")):
            url = "https://www.kakuyasu.co.jp" + store.attrs["href"]

            # https://www.kakuyasu.co.jp/store/app/shop/791-hachioujiyokamachi/
            r = get_each_store(url)
            if r:
                print(area.text)
                stores.append({
                    "area": area.text,
                    "area-e": kana(area.text),                    
                    "name": store.text,
                    "name-e": kana(store.text),                    
                    "addr": r[0],
                    "lat": r[1],
                    "lon": r[2]
                })

    return stores

def get_each_store(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--log-level=3")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    lat, lng = None, None

    html = driver.page_source

    # find lat/lan in this format: google.maps.LatLng(35.65998681198234, 139.3300387559684)
    m = re.search("google\.maps\.LatLng\(([\d\.]+), ([\d\.]+)\)", html)
    if m:
        latlng = m.groups(1)
        lat = float(latlng[0])
        lng = float(latlng[1])
    else:
        print("LAT/LNG not found!!")

    addr = None
    try:
        table = driver.find_element(By.CLASS_NAME, "base-table-confirm")
        rows = table.find_elements(By.TAG_NAME, "tr")
        addr = rows[1].text
    except NoSuchElementException:
        print("no table found")
    

    return (addr, lat, lng)


stores = get_store_list()
df = pd.DataFrame(stores)
df.to_csv("stores.csv")

