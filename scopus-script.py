from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import re
from collections import deque
import csv
import operator

OUT_FILENAME = 'RESULTS2017.csv'
MAX_DELAY_TIME = 10

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

    try:
        # if login text still exists, login wasn't successful
        login_txt = WebDriverWait(browser, MAX_DELAY_TIME-(MAX_DELAY_TIME/2)).until(EC.presence_of_element_located((By.XPATH, '//*[@id="headerWrapper"]/div[12]/h1')))
        return False
    except:
        return True  

def search(browser, query):
    '''
    Searches for sources, with given query
    in Scopus

    '''
    advanced_ref = WebDriverWait(browser, MAX_DELAY_TIME).until(    # when page is loaded, click Advanced Search
        EC.presence_of_element_located((By.LINK_TEXT, 'Advanced')))
    advanced_ref.click()

    search_field = WebDriverWait(browser, MAX_DELAY_TIME).until(    # when page is loaded, click query text box & send our query
        EC.presence_of_element_located((By.ID, 'searchfield')))
    search_field.send_keys(query)

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

            if source_name['clickable']:
                source = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                    EC.presence_of_element_located((By.LINK_TEXT, source_name['name'])))   # go in document's page
                source.click()

                try:
                    categories = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                        EC.presence_of_all_elements_located((By.CLASS_NAME, 'treeLineContainer')))    # find categories names

                    categories = convert_to_txt(categories) # convert categories from web element to string

                    try:
                        percentiles = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                            EC.presence_of_all_elements_located((By.XPATH, '//*[contains(@class, "pull-left paddingLeftQuarter")]'))) # find percentiles

                        percentiles = percentiles_to_num(convert_to_txt(percentiles))   # convert percentiles to number (int)

                        print(percentiles)

                    except:
                        print('no percentiles found')

                    #try:
                        
                        #metricLabels = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                         #   EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'h4 fontNormal noMargin Bottom metricLabel')]"))) # find metric labels

                        #print(metricLabels.text)

                        #metricLabels = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                            #EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'fontNormal h4 noMarginBottom metricLabel')]"))) # find metric labels

                        #metricLabels = convert_to_txt(metricLabels) # convert to str

                        #metricLabels = remove_digits(metricLabels)  # remove digits (dates)

                        #metricLabels = remove_spaces(metricLabels)  # remove spaces

                        #metricLabels = remove_new_line(metricLabels)   # remove next line character

                        #print(metricLabels)

                    #except:
                        #print('no metric labels found')

                    try:

                        metricValues = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                            EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'value fontMedLarge lineHeight2 blockDisplay')]"))) # find metrics (num)

                        metricValues = convert_to_txt(metricValues)

                        print(metricValues)
                    
                    except:
                        print('no metric values found')

                    document_dict = create_dict(i, document_name, source_name['name'], year, author_list, get_number_of_authors(author_list), get_average_percentile(percentiles), zip(['CiteScore', 'SJR', 'SNIP'], metricValues))

                    final_lst.append(document_dict)

                    print(document_dict)

                    i+=1
                    browser.execute_script("window.history.go(-1)")
                except:
                    document_dict = create_dict(i, document_name, source_name['name'], year, author_list, get_number_of_authors(author_list), 0, zip(['CiteScore', 'SJR', 'SNIP'], [0, 0, 0]))
                    final_lst.append(document_dict)
                    i+=1
                    print(document_dict)
                    browser.execute_script("window.history.go(-1)")
            else:
                document_dict = create_dict(i, document_name, source_name['name'], year, author_list, get_number_of_authors(author_list), 0, zip(['CiteScore', 'SJR', 'SNIP'], [0, 0, 0]))
                final_lst.append(document_dict)
                i+=1
                print(document_dict)
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

def remove_digits(lst): 
    '''
    Takes a list of strings and
    removes digits from every element
    '''
    pattern = '[0-9]'
    lst = [re.sub(pattern, '', i) for i in lst]
    return lst

def remove_spaces(lst):
    '''
    Takes a list of strings and
    removes spaces from every element
    '''
    lst = [x.strip(' ') for x in lst]
    return lst

def remove_new_line(lst):
    '''
    Takes a list of strings and
    removes spaces from every element
    '''
    lst = [x.strip('\n.') for x in lst]
    return lst

def create_dict(i, doc_name, source_name, year, authors, num_of_authors, avg_percentile, metrics):
    '''
    Takes some lists & a dictionary with info
    and creates a dictionary for each document with
    all the info needed
    '''
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
        paging_ul = WebDriverWait(browser, MAX_DELAY_TIME).until(    # when page is loaded, click query text box & send our query
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
    paging_ul = WebDriverWait(browser, MAX_DELAY_TIME).until(    # when page is loaded, click query text box & send our query
            EC.presence_of_element_located((By.CLASS_NAME, 'pagination')))
    return len(paging_ul.find_elements_by_tag_name("li"))

def get_number_of_rows(browser):
    '''
    Returns the number of rows
    of a page (number of documents)
    '''
    elements = []
    i=0
    while True:
        try:
            elements.append(browser.find_element_by_xpath('//*[@id="resultDataRow'+str(i)+'"]'))
            i+=1
        except:
            break
    return len(elements)

def get_source_rows(browser):
    '''
    Fetches all sources (names)
    and returns a string queue (with all the names)
    '''
    rows = []

    no_of_rows = get_number_of_rows(browser)    # number of rows of current page

    i=1
    while i<=no_of_rows:
        td = WebDriverWait(browser, MAX_DELAY_TIME).until(    
            EC.presence_of_element_located((By.XPATH, '//*[@id="resultDataRow'+str(i-1)+'"]/td[4]'))) 
        try:
            row = td.find_element(By.CLASS_NAME, 'ddmDocSource')
            rows.append({'name': row.text, 'clickable': True})
            i+=1
        except:
            rows.append({'name': td.text.splitlines()[0], 'clickable': False})
            i+=1

    return deque(rows)

def get_document_rows(browser):
    '''
    Fetches all documents (names)
    and returns a string queue (with all the names)
    '''
    table_id = WebDriverWait(browser, MAX_DELAY_TIME).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, 'ddmDocTitle') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

def get_author_rows(browser):
    '''
    Fetches all authors (names)
    and returns a string queue (with all the names)
    '''
    table_id = WebDriverWait(browser, MAX_DELAY_TIME).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.CLASS_NAME, ' ddmAuthorList') # get all of the rows in the table
    rows = convert_to_txt(rows) # convert web elements to string
    return deque(rows)

def get_year_rows(browser):
    '''
    Fetches all years
    and returns a string queue (with all the years)
    '''
    table_id = WebDriverWait(browser, MAX_DELAY_TIME).until(    
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
    with open(OUT_FILENAME, 'w', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
        print('written to csv')

if __name__ == "__main__":

    analyzed_docs = []

    browser = webdriver.Chrome()

    url = 'https://www.scopus.com/customer/authenticate/loginfull.uri'

    browser.get((url))

    username_str = 'scopus_email' # login credentials
    password_str = 'scopus_password'

    query = '( AF-ID ( "Panepistimion Makedonias"   60001086 ) )  AND  ( LIMIT-TO ( PUBYEAR ,  2018 ) )  AND  ( LIMIT-TO ( SRCTYPE ,  "k" ) )'

    # if login successful
    if login(browser, username_str, password_str):
        print('Login ok')
    else:
        print('Login failed, program exiting now...')

    search(browser, query)

    analyzed_docs = analyze_documents(browser)

    write_to_csv(analyzed_docs)