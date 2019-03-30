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

browser = webdriver.Chrome('C:/Users/Dimitris/Desktop/chromedriver.exe')

url = 'https://www.scopus.com/'

browser.get((url))

username_str = 'scopus_account' # login credentials
password_str = 'scopus_pass'

login(username_str, password_str)

search()