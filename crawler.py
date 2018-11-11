""" Main file """
import os
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from config import timeout, dir_path, crawl_urls, credentials, cookie_file, screenshot_dir, domain, SEED
from database import Recomendation, SESSION, Recomendation

from bs4 import BeautifulSoup

from joblib import Parallel, delayed

from slugify import slugify

# Gets chrome driver path
chrome_driver_path = os.path.join(dir_path, 'chromedriver')

# To open BROWSER on incognito(private) mode
BROWSER_options = webdriver.ChromeOptions()
BROWSER_options.add_argument('--incognito')
# BROWSER_options.add_argument("--headless")

def init_browser():
    # Creates new instance of chrome
    BROWSER = webdriver.Chrome(
        executable_path=chrome_driver_path,
        chrome_options=BROWSER_options
    )
    return BROWSER

def crawler():

    def save_html(html_str, filename):
        Html_file= open(filename,"w")
        Html_file.write(html_str)
        Html_file.close()
        return True

    def save_record(SESSION, source_html, url, parent_id=None, visited=0):
        r = Recomendation()
        r.parent_id = parent_id
        r.url = url
        file = './pages/' + slugify(url.split('/')[4]) +'.html'
        r.file = file
        r.visited = visited
        #r.page_source = source_html
        if save_html(source_html, file):
            SESSION.add(r)
            SESSION.commit()
        return r

    def visit_page(url):
        print('Obtendo o perfil:',url)
        BROWSER = init_browser()

        BROWSER.get(url)

        cookies = pickle.load(open(cookie_file, "rb"))
        for cookie in cookies:
            BROWSER.add_cookie(cookie)

        BROWSER.refresh()

        BROWSER.get(url)

        WebDriverWait(BROWSER, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, 'pv-deferred-area__content'))
        )

        WebDriverWait(BROWSER, timeout).until(
            EC.visibility_of_element_located((By.ID, 'experience-section'))
        )

        WebDriverWait(BROWSER, timeout).until(
            EC.visibility_of_element_located((By.ID, 'education-section'))
        )

        WebDriverWait(BROWSER, timeout).until(
            EC.visibility_of_element_located((By.ID, 'education-section'))
        )

        page_source = BROWSER.page_source
        BROWSER.quit()

        return page_source

    def process_url(url_seed, parent_id):

        exists = SESSION.query(Recomendation).filter_by(url=url_seed).first()

        if not exists or exists.visited==0:

            print('Obtendo o perfil seed :',url_seed)
            page_source = visit_page(url_seed) 

            r = save_record(SESSION, page_source, url_seed,  parent_id=parent_id, visited=1)

            soup = BeautifulSoup(page_source, 'html.parser')
            ul = soup.find('ul', class_= 'pv-profile-section__section-info section-info browsemap mt4')

            links = []

            for a in ul.find_all('a', class_='pv-browsemap-section__member ember-view'):
                url = domain + a['href']
                if len(url) < 255:
                    links.append(url)

            visitados = []

            sources = Parallel(n_jobs=-1)(delayed(visit_page)(link) for link in links)

            #print('############',len(sources))

            for page_source, link in zip(sources, links):
                rr = save_record(SESSION, page_source, link, parent_id=r.id)
                visitados.append(rr)
            
            for v in visitados:
                v.visitado=1
                SESSION.commit()

    try:

        BROWSER = init_browser()
        # Login if cookie is not present
        if (not os.path.isfile(cookie_file)):
            print('--- Login ---')
            # Requests login page
            BROWSER.get(crawl_urls['login'])

            # Wait till the element is present on the DOM
            WebDriverWait(BROWSER, timeout).until(
                EC.visibility_of_element_located((By.ID, 'login-submit'))
            )

            # Does Authentication by filling form email and password and clicking on login button
            BROWSER.find_element_by_id('login-email').send_keys(credentials['email'])
            BROWSER.find_element_by_id('login-password').send_keys(credentials['password'])
            BROWSER.find_element_by_id('login-submit').click()

            # Wait till the 'core-rail' class is located
            WebDriverWait(BROWSER, timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'core-rail'))
            )

            # Saves the cookies
            pickle.dump(BROWSER.get_cookies() , open(cookie_file,"wb"))

            # Taking screenshot
            BROWSER.save_screenshot(screenshot_dir + 'homepage_from_auth.png')
        else: # restore SESSION from cookie
            print('--- From cookie ---')
            BROWSER.get(crawl_urls['home'])

            # Loads the cookies and refresh the page
            cookies = pickle.load(open(cookie_file, "rb"))
            for cookie in cookies:
                BROWSER.add_cookie(cookie)

            BROWSER.refresh()

            # Wait till the element is located
            WebDriverWait(BROWSER, timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, 'core-rail'))
            )

        process_url(SEED, None)

        for i in range(100):

            not_visited = SESSION.query(Recomendation).filter_by(visited=0).all()

            for v in not_visited:
                process_url(v.url, v.id)
        
        BROWSER.quit()

    except TimeoutException:
        print('Timed out waiting for page to load')
        # Taking screenshot
        BROWSER.save_screenshot(screenshot_dir + 'timeout_exception.png')
        BROWSER.quit()

crawler()
