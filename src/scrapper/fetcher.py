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
  process_ratings = parsel.Selector(ratings_section).css('li::text').getall()
  ratings_list = [rating.replace('\n', '').replace('\t', '') for rating in process_ratings if rating.strip()]
  
  parsed_movie_title = re.sub(regex, '', raw_movie_title)
  ratings = {
    'rotten_tomatoes': ratings_list[0],
    'imdb': ratings_list[1]
  }
  
  
  movie_info = {
    'movie_title': parsed_movie_title,
    'tag_line': tag_line,
    'movie_cover': movie_cover,
    'summary': summary,
    'ratings': ratings,
    'genres': genres,
  }

  return movie_info
