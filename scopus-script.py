from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import re
from collections import deque
import csv
import operator

OUT_FILENAME = 'list.csv'

def login(browser, username, password):

    '''
    With given username & pass (credentials)
    logs in Scopus system

    '''
    user = browser.find_element_by_id('username')   # Find the textboxes we'll send the credentials
    passw = browser.find_element_by_id('password-input-password')

    user.send_keys(username)    # send credentials to textboxes 
    passw.send_keys(password)
    login_btn = browser.find_element(By.XPATH, '//*[@title="Login"]')   # find & click login button
    login_btn.click()

def search(browser):
    '''
    Searches for sources, with given query
    in Scopus

    '''
    advanced_ref = WebDriverWait(browser, 6).until(    # when page is loaded, click Advanced Search
        EC.presence_of_element_located((By.LINK_TEXT, 'Advanced')))
    advanced_ref.click()

    search_field = WebDriverWait(browser, 6).until(    # when page is loaded, click query text box & send our query
        EC.presence_of_element_located((By.ID, 'searchfield')))
    search_field.send_keys('( AF-ID ( "Panepistimion Makedonias"   60001086 ) )  AND  ( LIMIT-TO ( PUBYEAR ,  2018 ) )  AND  ( LIMIT-TO ( SRCTYPE ,  "j" ) )')

    search_btn = browser.find_element_by_id('advSearch')    # when query is sent, find & press the search button
    search_btn.click()

def analyze_documents(browser):

    '''
    Scans every source & gets its rating
    Saves all percentiles, average of percentiles and name of source
    in a dictionary, which is appended in a list of dictionaries (all sources)

    '''
    final_lst = []
    curr_page = 1   # begin with page 1
    no_of_pages = get_number_of_pages(browser) # get total number of pages
    document_rows = get_document_rows(browser) # get all document names
    author_rows = get_author_rows(browser) # get all author names
    source_rows = get_source_rows(browser)    # get all source names
    year_rows = get_year_rows(browser) # get all years
    i=1
    while True:

        try:
            document_name = document_rows.popleft() # pop the first one in list
            author_list = author_rows.popleft()
            source_name = source_rows.popleft()
            year = year_rows.popleft()

            source = WebDriverWait(browser, 6).until(    
                EC.presence_of_element_located((By.LINK_TEXT, source_name)))   # go in document's page
            source.click()

            try:
                categories = WebDriverWait(browser, 6).until(    
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'treeLineContainer')]")))    # find categories names

                categories = convert_to_txt(categories) # convert categories from web element to string

                percentiles = WebDriverWait(browser, 6).until(    
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'pull-left paddingLeftQuarter')]"))) # find percentiles

                percentiles = percentiles_to_num(convert_to_txt(percentiles))   # convert percentiles to number (int)

                metricLabels = WebDriverWait(browser, 6).until(    
                    EC.presence_of_all_elements_located((By.XPATH, './/span[@class = "metricLabel"]'))) # find metric labels

                metricLabels = convert_to_txt(metricLabels)

                metricValues = WebDriverWait(browser, 6).until(    
                    EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'value fontMedLarge  lineHeight2')]"))) # find metrics (num)

                metricValues = convert_to_txt(metricValues)

                document_dict = create_dict(i, document_name, source_name, year, author_list, get_number_of_authors(author_list), get_average_percentile(percentiles), zip(metricLabels, metricValues))

                final_lst.append(document_dict)
                print(document_dict)

                i+=1
                browser.execute_script("window.history.go(-1)")
            except:
                i+=1
                browser.execute_script("window.history.go(-1)")
        except:
            try:
                if curr_page < no_of_pages:
                    curr_page = change_page(browser, curr_page)  # change page
                    document_rows = get_document_rows(browser) # get all document names
                    author_rows = get_author_rows(browser) # get all author names
                    source_rows = get_source_rows(browser)    # get all source names
                    year_rows = get_year_rows(browser) # get all years
                else:
                    break
            except:
                break
    browser.close()

    return final_lst

def create_dict(i, doc_name, source_name, year, authors, num_of_authors, avg_percentile, metrics):

    dictionary = {'#': i, 'Document Name': doc_name, 'Source Name': source_name, 'Year': year, 'Authors': authors, '# Authors': num_of_authors, 'Average Percentile': avg_percentile}
    dictionary.update(metrics)
    return dictionary

def get_number_of_authors(authors):
    '''
    Takes a string (author names) & returns
    an integer (total number of document's authors)
    '''
    split_authors = authors.split(',')
    return len([','.join(i) for i in zip(split_authors[::2], split_authors[1::2])])

def convert_to_txt(lst):
    '''
    Takes a list of web elements & returns
    a list of strings (the string of each element)
    '''
    return [element.text for element in lst]

def percentiles_to_num(lst):
    '''
    Takes a list of strings and takes the numbers
    from each element (percentiles). Returns a list of nums.
    '''
    percentiles_num = []
    for percentile in lst:
        percentiles_num.append(int(re.findall("\d+", percentile)[0]))
    return percentiles_num

def get_average_percentile(percentiles):
    '''
    Takes a list of numbers (percentiles) 
    and returns their average
    '''
    return float(sum(percentiles) / len(percentiles)) 

def change_page(browser, curr_page):
    '''
    Takes a number of page (int) and finds the next page
    If a next page is found, goes to next page
    If not, script exits (no other pages left)
    Returns the new curr_page
    '''
    try:
        paging_ul = WebDriverWait(browser, 6).until(    # when page is loaded, click query text box & send our query
            EC.presence_of_element_located((By.CLASS_NAME, 'pagination')))
        pages = paging_ul.find_elements_by_tag_name('li')

        next_page = next(page for page in pages if page.text == str(curr_page+1))

        next_page.click()

        return curr_page+1

    except:
        print('error')

def get_number_of_pages(browser):
    '''
    Returns total number of pages
    '''
    paging_ul = WebDriverWait(browser, 6).until(    # when page is loaded, click query text box & send our query
            EC.presence_of_element_located((By.CLASS_NAME, 'pagination')))
    return len(paging_ul.find_elements_by_tag_name("li"))

def get_source_rows(browser):
    '''
    Fetches all sources (names)
    and returns a string queue (with all the names)
    '''
    table_id = WebDriverWait(browser, 6).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, 'ddmDocSource') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

def get_document_rows(browser):
    '''
    Fetches all documents (names)
    and returns a string queue (with all the names)
    '''
    table_id = WebDriverWait(browser, 6).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, 'ddmDocTitle') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

def get_author_rows(browser):
    '''
    Fetches all authors (names)
    and returns a string queue (with all the names)
    '''
    table_id = WebDriverWait(browser, 6).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, ' ddmAuthorList') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

def get_year_rows(browser):
    '''
    Fetches all years
    and returns a string queue (with all the years)
    '''
    table_id = WebDriverWait(browser, 6).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, ' ddmPubYr') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

def write_to_csv(data):
    '''
    Takes a list of dictionaries (sources)
    and writes all the info to csv file
    '''
    keys = data[0].keys()
    with open(OUT_FILENAME, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        print('written to csv')

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