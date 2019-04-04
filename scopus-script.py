from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions

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
    row = table_id.find_element(By.CLASS_NAME, 'ddmDocTitle') # get all of the rows in the table

    try:
        doc = WebDriverWait(browser, 20).until(    
            EC.presence_of_element_located((By.LINK_TEXT, row.text)))   # go in document's page
        doc.click()
    except:
        exit(1)

    while True:

        try:
            metrics_span = WebDriverWait(browser, 5).until(    
            EC.element_to_be_clickable((By.LINK_TEXT, 'View all metrics')))
            metrics_span.click() # click & go to metrics page (for the specific document)
        except:
            next_span = WebDriverWait(browser, 5).until(    
                EC.element_to_be_clickable((By.LINK_TEXT, 'Next'))) # go to next document
            if not next_span: exit(0) # if there is no other document, exit
            next_span.click()
        percentiles = [] # initialize the percentiles list
        try:
            doc_title = browser.find_element_by_id('altmet_article').find_element_by_tag_name('h3').text    # get document title
            percentiles.append(browser.find_element_by_id('percentLabel').text) # get the first percentile
            try:
                menu = browser.find_element_by_id('multipleOptions-menu')   # if dropdown list has multiple options
                button = browser.find_element_by_id('multipleOptions-button')
                button.click()
            except:
                menu = browser.find_element_by_id('subjectArea-menu')   # if dropdown list has only one option
                button = browser.find_element_by_id('subjectArea-button')
                
            items = menu.find_elements_by_tag_name('div')   # find items of dropdown list
            for item in items:  # get the rest percentiles
                try:
                    button.click()  # click button to see options
                    item.click()    # click on every option of dropdown list
                    percentiles.append(browser.find_element_by_id('percentLabel').text) # append percentile to list 
                except:
                    continue
            print(doc_title)    # printing
            for percentile in percentiles:  
                print(percentile)
            browser.find_element_by_xpath("//*[text()='Back to document']").click() # got the percentiles, go back
            next_span = WebDriverWait(browser, 5).until(    
                EC.element_to_be_clickable((By.LINK_TEXT, 'Next'))) # go to next document
            if not next_span: exit(0) # if there is no other document, exit
            next_span.click()
        except:
            browser.find_element_by_xpath("//*[text()='Back to document']").click() # if document has no metrics to fetch
            next_span = WebDriverWait(browser, 5).until(    
                EC.element_to_be_clickable((By.LINK_TEXT, 'Next'))) # go to next document
            if not next_span: exit(0) # if there is no other document, exit
            next_span.click()  

browser = webdriver.Chrome()

url = 'https://www.scopus.com/'

browser.get((url))

username_str = 'scopus_account' # login credentials
password_str = 'scopus_pass'

login(username_str, password_str)

search()

scan_documents()