from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import re
from collections import deque

def login(username, password):
    user = browser.find_element_by_id('paywall_username')   # Find the textboxes we'll send the credentials
    passw = browser.find_element_by_id('paywall_password')

    user.send_keys(username)    # send credentials to textboxes 
    passw.send_keys(password)
    login_btn = browser.find_element_by_id('paywall_login_submit_button_element')   # find & click login button
    login_btn.click()

def search():
    advanced_ref = WebDriverWait(browser, 4).until(    # when page is loaded, click Advanced Search
        EC.presence_of_element_located((By.LINK_TEXT, 'Advanced')))
    advanced_ref.click()

    search_field = WebDriverWait(browser, 4).until(    # when page is loaded, click query text box & send our query
        EC.presence_of_element_located((By.ID, 'searchfield')))
    search_field.send_keys('( AF-ID ( "Panepistimion Makedonias"   60001086 ) )  AND  ( LIMIT-TO ( PUBYEAR ,  2018 ) )  AND  ( LIMIT-TO ( SRCTYPE ,  "j" ) )')

    search_btn = browser.find_element_by_id('advSearch')    # when query is sent, find & press the search button
    search_btn.click()

def scan_documents():

    curr_page = 1   # begin with page 1
    no_of_pages = get_number_of_pages() # get total number of pages
    done_sources = []   # list of checked sources
    rows = get_source_rows()    # get all source names
    while True:

        try:
            source_name = rows.popleft()    # pop the first one in list
            while source_name in done_sources:  # if the one we popped is in done_sources, pop the next one
                source_name = rows.popleft()
            done_sources.append(source_name)    # add the source we're checking in list
            doc = WebDriverWait(browser, 4).until(    
                EC.presence_of_element_located((By.LINK_TEXT, source_name)))   # go in document's page
            doc.click()

            try:
                categories = WebDriverWait(browser, 4).until(    
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'treeLineContainer')]")))    # find categories names

                categories = convert_to_txt(categories) # convert categories from web element to string

                percentiles = WebDriverWait(browser, 4).until(    
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'pull-left paddingLeftQuarter')]"))) # find percentiles

                percentiles = percentiles_to_num(convert_to_txt(percentiles))   # convert percentiles to number (int)

                citescores = dict(zip(categories, percentiles))    # create a dictionary <category name, percentile, avg(percentile), <name>
                citescores['Average'] =  get_average_percentile(percentiles)
                citescores['Name'] = source_name

                citescore_lst.append(citescores)
                print(citescores)

                browser.execute_script("window.history.go(-1)")
            except:
                browser.execute_script("window.history.go(-1)")
        except:
            try:
                change_page(curr_page)  # change page
                curr_page += 1
                rows = get_source_rows()    # get the new source names
            except:
                break

def convert_to_txt(lst):
    return [element.text for element in lst]

def percentiles_to_num(lst):
    percentiles_num = []
    for percentile in lst:
        percentiles_num.append(int(re.findall("\d+", percentile)[0]))
    return percentiles_num

def get_average_percentile(percentiles):
    return float(sum(percentiles) / len(percentiles)) 

def remove_duplicates(lst):
    return {frozenset(item.items()) : item for item in lst}.values() 

def change_page(curr_page):
    try:
        paging_ul = WebDriverWait(browser, 4).until(    # when page is loaded, click query text box & send our query
            EC.presence_of_element_located((By.CLASS_NAME, 'pagination')))
        pages = paging_ul.find_elements_by_tag_name('li')

        next_page = next(page for page in pages if page.text == str(curr_page+1))

        next_page.click()

    except:
        exit(0)

def get_number_of_pages():
    paging_ul = WebDriverWait(browser, 4).until(    # when page is loaded, click query text box & send our query
            EC.presence_of_element_located((By.CLASS_NAME, 'pagination')))
    return len(paging_ul.find_elements_by_tag_name("li"))

def get_source_rows():
    table_id = WebDriverWait(browser, 4).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, 'ddmDocSource') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

if __name__ == "__main__":

    citescore_lst = []

    browser = webdriver.Chrome()

    url = 'https://www.scopus.com/home.uri'

    browser.get((url))

    username_str = 'scopus_acc' # login credentials
    password_str = 'scopus_pass'

    login(username_str, password_str)

    search()

    scan_documents()