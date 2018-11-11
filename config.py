import os

# Domain name to crawl
domain = 'https://www.linkedin.com'

# Urls to crawl
crawl_urls = {
    'login': domain,
    'home': domain,
}

# User credentials
credentials = {
    'email': 'joaoavelardossantos@gmail.com',
    'password': 'Joao123456!'
}

# Wait time
timeout = 20

# Gets current directory path
dir_path = os.getcwd()

# Cookie file name to store cookies
cookie_name = 'cookies.pkl'

# Gets cookie file name
cookie_file = os.path.join(dir_path, cookie_name)

# Gets screenshot saving directory path
screenshot_dir = os.path.join(dir_path, 'screenshots' + os.sep)


PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(PROJECT_ROOT, 'db','recodb.db')
DATABASE_URI = 'sqlite:///' + DATABASE

SEED = "https://www.linkedin.com/in/ronaldo-ribeiro-739118/"