from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
import re
from collections import deque
import csv
import operator

OUT_FILENAME = 'RESULTS2018.csv'
MAX_DELAY_TIME = 10

class LoginPage():

    def __init__(self, browser):
        self.browser = browser
        self.username_box_id = 'username'
        self.password_box_id = 'password-input-password'
        self.login_btn_xpath = '//*[@title="Login"]'
        self.document_header_xpath = '//h1[@class="documentHeader"]'

    def login(self, username, password):

        '''
        With given username & pass (credentials)
        logs in Scopus system

        '''
        user_element = self.browser.find_element_by_id(self.username_box_id)   # Find the textboxes we'll send the credentials
        pass_element = self.browser.find_element_by_id(self.password_box_id)

        user_element.send_keys(username)    # send credentials to textboxes 
        pass_element.send_keys(password) 
        login_btn = self.browser.find_element_by_xpath(self.login_btn_xpath)    # find & click login button
        login_btn.click()

        try:
            # if document search text appears, login successful
            document_search_txt = WebDriverWait(self.browser, MAX_DELAY_TIME-(MAX_DELAY_TIME/2)).until(EC.presence_of_element_located((By.XPATH, self.document_header_xpath)))
            print('Login ok')
        except:
            print('Login failed, program exiting now...')
            browser.close()
            exit(1) 

class SearchPage():

    def __init__(self, browser):
        self.browser = browser
        self.advanced_ref_link_text = 'Advanced'
        self.search_field_id = 'searchfield'
        self.search_btn_id = 'advSearch'

    def search(self, query):
        '''
        Searches for sources, with given query
        in Scopus

        '''
        advanced_ref = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    # when page is loaded, click Advanced Search
            EC.presence_of_element_located((By.LINK_TEXT, self.advanced_ref_link_text)))
        advanced_ref.click()

        search_field = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    # when page is loaded, click query text box & send our query
            EC.presence_of_element_located((By.ID, self.search_field_id)))
        search_field.send_keys(query)

        search_btn = self.browser.find_element_by_id(self.search_btn_id)    # when query is sent, find & press the search button
        search_btn.click()

class DocumentPage():

    def __init__(self, browser):
        self.browser = browser
        self.percentile_categories_class_name = 'treeLineContainer'
        self.percentiles_xpath = '//*[contains(@class, "pull-left paddingLeftQuarter")]'
        self.metric_values_xpath = "//*[contains(@class, 'value fontMedLarge lineHeight2 blockDisplay')]"
        self.paging_ul_class_name = 'pagination'
        self.doc_source_class_name = 'ddmDocSource'      
        self.search_results_table_id = 'srchResultsList'
        self.doc_title_class_name = 'ddmDocTitle'
        self.authors_list_class_name = 'ddmAuthorList'
        self.pub_year_class_name = 'ddmPubYr'

    def analyze_documents(self):

        '''
        Scans every source & gets its rating
        Saves all percentiles, average of percentiles and name of source
        in a dictionary, which is appended in a list of dictionaries (all sources)

        '''
        final_lst = []
        curr_page = 1   # begin with page 1
        no_of_pages = self.get_number_of_pages() # get total number of pages
        document_rows = self.get_document_rows() # get all document names
        author_rows = self.get_author_rows() # get all author names
        source_rows = self.get_source_rows()    # get all source names
        year_rows = self.get_year_rows() # get all years
        i=1
        while True:

            try:
                document_name = document_rows.popleft() # pop the first one in list
                author_list = author_rows.popleft()
                source_name = source_rows.popleft()
                year = year_rows.popleft()

                if source_name['clickable']:
                    source = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
                        EC.presence_of_element_located((By.LINK_TEXT, source_name['name'])))   # go in document's page
                    source.click()

                    try:
                        categories = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
                            EC.presence_of_all_elements_located((By.CLASS_NAME, self.percentile_categories_class_name)))    # find categories names

                        categories = self.convert_to_txt(categories) # convert categories from web element to string

                        try:
                            percentiles = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
                                EC.presence_of_all_elements_located((By.XPATH, self.percentiles_xpath))) # find percentiles

                            percentiles = self.percentiles_to_num(self.convert_to_txt(percentiles))   # convert percentiles to number (int)

                            print(percentiles)

                        except:
                            print('no percentiles found')

                        #try:
                            
                            #metricLabels = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                            #   EC.presence_of_element_located((By.XPATH, "//*[contains(@class, 'h4 fontNormal noMargin Bottom metricLabel')]"))) # find metric labels

                            #print(metricLabels.text)

                            #metricLabels = WebDriverWait(browser, MAX_DELAY_TIME).until(    
                                #EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'fontNormal h4 noMarginBottom metricLabel')]"))) # find metric labels

                            #metricLabels = self.convert_to_txt(metricLabels) # convert to str

                            #metricLabels = self.remove_digits(metricLabels)  # remove digits (dates)

                            #metricLabels = self.remove_spaces(metricLabels)  # remove spaces

                            #metricLabels = self.remove_new_line(metricLabels)   # remove next line character

                            #print(metricLabels)

                        #except:
                            #print('no metric labels found')

                        try:

                            metric_values = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
                                EC.presence_of_all_elements_located((By.XPATH, self.metric_values_xpath))) # find metrics (num)

                            metric_values = self.convert_to_txt(metric_values)
                        
                        except:
                            print('no metric values found')

                        document_dict = self.create_dict(i, document_name, source_name['name'], year, author_list, self.get_number_of_authors(author_list), self.get_average_percentile(percentiles), zip(['CiteScore', 'SJR', 'SNIP'], metric_values))

                        final_lst.append(document_dict)

                        print(document_dict)

                        i+=1
                        browser.execute_script("window.history.go(-1)")
                    except:
                        document_dict = self.create_dict(i, document_name, source_name['name'], year, author_list, self.get_number_of_authors(author_list), 0, zip(['CiteScore', 'SJR', 'SNIP'], [0, 0, 0]))
                        final_lst.append(document_dict)
                        i+=1
                        print(document_dict)
                        browser.execute_script("window.history.go(-1)")
                else:
                    document_dict = self.create_dict(i, document_name, source_name['name'], year, author_list, self.get_number_of_authors(author_list), 0, zip(['CiteScore', 'SJR', 'SNIP'], [0, 0, 0]))
                    final_lst.append(document_dict)
                    i+=1
                    print(document_dict)
            except:
                try:
                    if curr_page < no_of_pages:
                        curr_page = self.change_page(curr_page)  # change page
                        document_rows = self.get_document_rows() # get all document names
                        author_rows = self.get_author_rows() # get all author names
                        source_rows = self.get_source_rows()    # get all source names
                        year_rows = self.get_year_rows() # get all years
                    else:
                        break
                except:
                    break
        browser.close()

        return final_lst

    def remove_digits(self, lst): 
        '''
        Takes a list of strings and
        removes digits from every element
        '''
        pattern = '[0-9]'
        lst = [re.sub(pattern, '', i) for i in lst]
        return lst

    def remove_spaces(self, lst):
        '''
        Takes a list of strings and
        removes spaces from every element
        '''
        lst = [x.strip(' ') for x in lst]
        return lst

    def remove_new_line(self, lst):
        '''
        Takes a list of strings and
        removes spaces from every element
        '''
        lst = [x.strip('\n.') for x in lst]
        return lst

    def create_dict(self, i, doc_name, source_name, year, authors, num_of_authors, avg_percentile, metrics):
        '''
        Takes some lists & a dictionary with info
        and creates a dictionary for each document with
        all the info needed
        '''
        dictionary = {'#': i, 'Document Name': doc_name, 'Source Name': source_name, 'Year': year, 'Authors': authors, '# Authors': num_of_authors, 'Average Percentile': avg_percentile}
        dictionary.update(metrics)
        return dictionary

    def get_number_of_authors(self, authors):
        '''
        Takes a string (author names) & returns
        an integer (total number of document's authors)
        '''
        split_authors = authors.split(',')
        return len([','.join(i) for i in zip(split_authors[::2], split_authors[1::2])])

    def convert_to_txt(self, lst):
        '''
        Takes a list of web elements & returns
        a list of strings (the string of each element)
        '''
        return [element.text for element in lst]

    def percentiles_to_num(self, lst):
        '''
        Takes a list of strings and takes the numbers
        from each element (percentiles). Returns a list of nums.
        '''
        percentiles_num = []
        for percentile in lst:
            percentiles_num.append(int(re.findall("\d+", percentile)[0]))
        return percentiles_num

    def get_average_percentile(self, percentiles):
        '''
        Takes a list of numbers (percentiles) 
        and returns their average
        '''
        return float(sum(percentiles) / len(percentiles)) 

    def change_page(self, curr_page):
        '''
        Takes a number of page (int) and finds the next page
        If a next page is found, goes to next page
        If not, script exits (no other pages left)
        Returns the new curr_page
        '''
        try:
            paging_ul = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    # when page is loaded, click query text box & send our query
                EC.presence_of_element_located((By.CLASS_NAME, self.paging_ul_class_name)))
            pages = paging_ul.find_elements_by_tag_name('li')

            next_page = next(page for page in pages if page.text == str(curr_page+1))

            next_page.click()

            return curr_page+1

        except:
            print('error')

    def get_number_of_pages(self):
        '''
        Returns total number of pages
        '''
        paging_ul = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    # when page is loaded, click query text box & send our query
                EC.presence_of_element_located((By.CLASS_NAME, self.paging_ul_class_name)))
        return len(paging_ul.find_elements_by_tag_name("li"))

    def get_number_of_rows(self):
        '''
        Returns the number of rows
        of a page (number of documents)
        '''
        elements = []
        i=0
        while True:
            try:
                elements.append(self.browser.find_element_by_xpath('//*[@id="resultDataRow'+str(i)+'"]'))
                i+=1
            except:
                break
        return len(elements)

    def get_source_rows(self):
        '''
        Fetches all sources (names)
        and returns a string queue (with all the names)
        '''
        rows = []

        no_of_rows = self.get_number_of_rows()    # number of rows of current page

        i=1
        while i<=no_of_rows:
            td = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
                EC.presence_of_element_located((By.XPATH, '//*[@id="resultDataRow'+str(i-1)+'"]/td[4]'))) 
            try:
                row = td.find_element(By.CLASS_NAME, self.doc_source_class_name)
                rows.append({'name': row.text, 'clickable': True})
                i+=1
            except:
                rows.append({'name': td.text.splitlines()[0], 'clickable': False})
                i+=1

        return deque(rows)

    def get_document_rows(self):
        '''
        Fetches all documents (names)
        and returns a string queue (with all the names)
        '''
        results = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
            EC.presence_of_element_located((By.ID, self.search_results_table_id))) # srchResultsList is the data table, from which we will get the documents' names
        rows = results.find_elements(By.CLASS_NAME, self.doc_title_class_name) # get all of the rows in the table
        rows = self.convert_to_txt(rows) # convert web elements to string
        return deque(rows)

    def get_author_rows(self):
        '''
        Fetches all authors (names)
        and returns a string queue (with all the names)
        '''
        results = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
            EC.presence_of_element_located((By.ID, self.search_results_table_id))) # srchResultsList is the data table, from which we will get the documents' names
        rows = results.find_elements(By.CLASS_NAME, self.authors_list_class_name) # get all of the rows in the table
        rows = self.convert_to_txt(rows) # convert web elements to string
        return deque(rows)

    def get_year_rows(self):
        '''
        Fetches all years
        and returns a string queue (with all the years)
        '''
        results = WebDriverWait(self.browser, MAX_DELAY_TIME).until(    
            EC.presence_of_element_located((By.ID, self.search_results_table_id))) # srchResultsList is the data table, from which we will get the documents' names
        rows = results.find_elements(By.CLASS_NAME, self.pub_year_class_name) # get all of the rows in the table
        rows = self.convert_to_txt(rows) # convert web elements to string
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

    query = '( AF-ID ( "Panepistimion Makedonias"   60001086 ) )  AND  ( LIMIT-TO ( PUBYEAR ,  2018 ) )  AND  ( LIMIT-TO ( SRCTYPE ,  "j" ) )'

    login_page = LoginPage(browser)
    login_page.login(username_str, password_str)

    search_page = SearchPage(browser)
    search_page.search(query)

    doc_page = DocumentPage(browser)
    doc_page.analyze_documents()

    write_to_csv(analyzed_docs)