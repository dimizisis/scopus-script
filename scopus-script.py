from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def login(username, password):
    user = browser.find_element_by_id('paywall_username')   # Find the textboxes we'll send the credentials
    passw = browser.find_element_by_id('paywall_password')

    user.send_keys(username)    # send credentials to textboxes 
    passw.send_keys(password)
    login_btn = browser.find_element_by_id('paywall_login_submit_button_element')   # find & click login button
    login_btn.click()

def search():
    advanced_ref = WebDriverWait(browser, 10).until(    # when page is loaded, click Advanced Search
        EC.presence_of_element_located((By.LINK_TEXT, 'Advanced')))
    advanced_ref.click()

    search_field = WebDriverWait(browser, 10).until(    # when page is loaded, click query text box & send our query
        EC.presence_of_element_located((By.ID, 'searchfield')))
    search_field.send_keys('( AF-ID ( "Panepistimion Makedonias"   60001086 ) )  AND  ( LIMIT-TO ( PUBYEAR ,  2018 ) )  AND  ( LIMIT-TO ( SRCTYPE ,  "j" ) )')

    search_btn = browser.find_element_by_id('advSearch')    # when query is sent, find & press the search button
    search_btn.click()

def scan_documents():
    table_id = WebDriverWait(browser, 10).until(    
        EC.presence_of_element_located((By.ID, 'srchResultsList'))) # srchResultsList is the data table, from which we will get the documents' names
    rows = table_id.find_elements(By.TAG_NAME, 'tr') # get all of the rows in the table

    for row in rows:
        try:        
            first_col = row.find_elements(By.TAG_NAME, 'td')[0] # get the first column of data table (document name)
            if 'View abstract' not in first_col.text:
                document_name = first_col.text # if there is no View Abstract Related Documents text (dirty col), it is a document name
        except:
            continue
        link = row.find_element_by_link_text(document_name)
        link.click()
        metrics_span = WebDriverWait(browser, 10).until(    
        EC.element_to_be_clickable((By.LINK_TEXT, 'View all metrics')))
        metrics_span.click()
        percentiles = []
        percentiles.append(browser.find_element_by_id('percentLabel'))
        ui_selector = WebDriverWait(browser, 10).until(    
        EC.element_to_be_clickable((By.ID, 'multipleOptions-button')))
        ui_selector.click()
        ui_list = browser.find_element_by_id('multipleOptions-menu')
        items = ui_list.find_elements_by_tag_name("li")
        for item in items:
            try:
                item.click()
                percentiles.append(browser.find_element_by_id('percentLabel'))
            except:
                continue
        break    


browser = webdriver.Chrome('C:/chromedriver.exe')

url = 'https://www.scopus.com/'

browser.get((url))

username_str = 'scopus_account' # login credentials
password_str = 'scopus_pass'

login(username_str, password_str)

search()

scan_documents()