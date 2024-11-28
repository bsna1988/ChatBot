import requests
from bs4 import BeautifulSoup
import os

BASE_URL = "https://int.krok.edu.ua"
START_URL = BASE_URL + "/en/"
scraped_urls = {''}

def scrap(scrap_url, scraped_urls):
  if scrap_url in scraped_urls:
    return

  # to tell the website that we are not a bot we need to pass headers (using user-agent)
  HEADERS = {
    "User-Agent": "your user agent",
    "Accept-Language": "en-US, en;q=0.5",
  }

  # making request to the website
  webpage = requests.get(scrap_url, headers=HEADERS, timeout=10)
  if webpage.headers.get('Content-Type') == 'application/pdf':
    print("Skipping PDF file:", scrap_url)
    return

  print(scrap_url)
  # checking connection
  print(webpage.status_code)  # 200 means request is successful

  DIR = "content/"
  # Ensure the 'content' directory exists
  os.makedirs(DIR, exist_ok=True)

  # Remove the base URL and replace '/' with '_'
  file_name = scrap_url.replace(BASE_URL, "").replace("/", "_").replace(".", "_")
  file_path = os.path.join(DIR, file_name)

  # Write the webpage content to the file
  with open(file_path, "w", encoding="utf-8") as file:
    file.write(webpage.text)

  print(f"Webpage saved to {file_path}")
  scraped_urls.add(scrap_url)


  # printing the content of the webpage
  # print(webpage.content)  # but it gives response in bytes format

  # Now we need to use BeautifulSoup to parse the content of the webpage
  soup = BeautifulSoup(webpage.content, "html.parser")

  # find different links in the webpage
  links = soup.find_all("a")

  # Filter only relative URLs that start with "/en/"
  filtered_links = [link['href'] for link in links if link.get('href', '').startswith('/en/')]
  # print the links
  print(filtered_links)  # but the links are not complete

  for url in filtered_links:
    scrap(BASE_URL + url, scraped_urls)

scrap(START_URL, scraped_urls)