import json
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

base_url = 'http://www.carsurvey.org'

def extract_most_popular_brands(base_url = base_url):
  response = requests.get(base_url)
  soup = BeautifulSoup(response.text, 'html.parser')
  most_popular_section = soup.find('h2', class_='most-popular-header')
  manufacturer_list = most_popular_section.find_next('ol', class_='manufacturer-list')
  popular_makes = []
  for li in manufacturer_list.find_all('li'):
      a = li.find('a')
      if a:
          popular_makes.append({
              'name': a.text.strip(),
              'url': f"{base_url}{a['href'].strip()}"
          })
  return popular_makes

def extract_models(url, base_url=base_url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    model_table = soup.find('table', class_='model-list')
    if not model_table:
        raise ValueError("Couldn't find the table with class 'model-list'")

    models = []
    for tr in model_table.find_all('tr'):
        a = tr.find('a')
        if a:
            models.append(base_url+a['href'].strip())
    return models

def split_by_years(url, base_url=base_url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    model_year_table = soup.find('table', class_='model-year-list')
    if not model_year_table:
        return [url]

    models = []
    for tr in model_year_table.find_all('tr'):
        a = tr.find('a')
        if a:
            models.append(base_url + a['href'].strip())
    return models

def get_review_link(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    model_table = soup.find('table', class_='review-list-table')
    if not model_table:
        raise ValueError("model-list finding issue")

    models = []
    for tr in model_table.find_all('tr'):
        a = tr.find('a')
        if a and a.get('href'):
            models.append(base_url+a['href'].strip())
    return models

def get_all_reviews_for_brand(brand_info, base_url = base_url):
  res = []
  print(f"  Extract info for {brand_info['name']}")
  brand_link = brand_info['url']
  models = extract_models(brand_link)
  for model in models:
    models_by_years = split_by_years(model)
    for model_year in models_by_years:
      try:
        res += get_review_link(model_year)
      except:
        res.append(model_year)

  return res

def extract_json(link):
  res = {}
  response = requests.get(link)
  soup = BeautifulSoup(response.text, 'html.parser')
  article = soup.find('article', class_='cf single-review')
  if not article:
    return
  for topic in article.find_all('section'):
    topic_name = topic.find('h2')
    if not topic_name:
      continue
    topic_name = topic_name.get_text(strip=True)
    topic_text = topic.find_all('p')
    text = "".join([p.get_text(strip=True) for p in topic_text])
    res[topic_name] = text

  table = article.find('table')
  rows = table.find_all('tr')
  for row in rows:
      cells = row.find_all('td')
      if len(cells) == 2:
          key = cells[0].get_text(strip=True)
          value = cells[1].get_text(strip=True)
          res[key] = value
  return json.dumps(res, indent=2)

def get_all_reviews_in_json(brand_links):
  res = []
  for brand_link in tqdm(brand_links):
    reviews_links = get_all_reviews_for_brand(brand_link)
    for review_link in tqdm(reviews_links):
       res.append(extract_json(review_link))
  return res

brands = extract_most_popular_brands()
not_interested_brands = ['Buick', 'Mercury', 'Oldsmobile', 'Saturn', 'Pontiac']
brands_filtered = [brand for brand in brands if brand['name'] not in not_interested_brands]

json_reviews = get_all_reviews_in_json(brands_filtered)

with open("model-training/data/reviews_carsurvej.json", "w") as f:
    json.dump(json_reviews, f, indent=2)