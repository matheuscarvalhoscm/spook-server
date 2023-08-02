from dotenv import load_dotenv
import os
import requests
import parsel
import re

load_dotenv()

source = os.getenv('SOURCE_URL')

def fetch(url):
  try:
    response = requests.get(url)
    if response.status_code != 200:
      return 'Failed to fetch :('
    return response.text
  except requests.ReadTimeout:
    return None

def get_movies_url(html):
  selector = parsel.Selector(text=html)
  urls = selector.css('.col-md-9 h4 a::attr(href)').getall()
  return urls

def get_next_page(html):
    if type(html) is not str:
      return 'Invalid content!'

    selector = parsel.Selector(text=html)
    next_page_url = selector.css('.page-numbers li a::attr(href)').get()
    return next_page_url

def get_movie_info(html):
  selector = parsel.Selector(html)
  regex = r'\([^)]*\)'

  raw_movie_title = selector.css('.movie-name::text').get()
  tag_line = selector.css('.movie-tag-line i::text').get()
  movie_cover = selector.css('img.movie-trailer-photos::attr(src)').get()
  summary = selector.css('#tmdb-movie-series-other-related-data p::text').get()
  genres = selector.css('.tmdb-movie-chapeau li a button::text').getall()

  ratings_section = selector.css('.star-rating-section ~ ul.tmdb-movies-stats').get()
  ratings = { 'rotten_tomatoes': 'N/A', 'imdb': 'N/A' }

  if ratings_section is not None:
    process_ratings = parsel.Selector(ratings_section).css('li::text').getall()
    ratings_list = [rating.replace('\n', '').replace('\t', '') for rating in process_ratings if rating.strip()]
    
    ratings['rotten_tomatoes'] = ratings_list[0]
    ratings['imdb'] = ratings_list[1]

  raw_additional_info = selector.css('.tmdb-movie-stats li::text').getall()
  additional_info = [info.replace('\n', '').replace('\t', '') for info in raw_additional_info if info.strip()]

  raw_additional_info_with_links = selector.css('.tmdb-movie-stats a::text').getall()
  
  release_date = None
  movie_rate, movie_length = None, None
  
  if ratings_section is None:
    parsed_additional_info = re.findall(r':(.*?)(?=\|)', additional_info[1])

    release_date = additional_info[0].replace(' Release Date: ', '')
    movie_rate, movie_length = parsed_additional_info[0], parsed_additional_info[1]
  else:
    parsed_additional_info = re.findall(r':(.*?)(?=\|)', additional_info[3])
    
    release_date = additional_info[2].replace(' Release Date: ', '')
    movie_rate, movie_length  = parsed_additional_info[0], parsed_additional_info[1]
  
  parsed_movie_title = re.sub(regex, '', raw_movie_title)
  
  movie_info = {
    'title': parsed_movie_title,
    'tag_line': tag_line,
    'cover': movie_cover,
    'summary': summary,
    'ratings': ratings,
    'genres': genres,
    'release_date': release_date,
    'movie_rate': movie_rate,
    'runtime': movie_length,
    'director': raw_additional_info_with_links
  }

  return movie_info
