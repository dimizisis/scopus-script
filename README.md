# scopus-script

## Description

Script that logs in to scopus (must have account on www.scopus.com) and searches a specific query (for now it is a fix query).
Analyzes documents from query, and returns a dictionary of type:

```
{ #, document_name, source_name, year, author_list, number_of_authors (source), 
average_percentile (source), metrics (source) }
```

for every document

When analyzing is finished, a CSV file is exported, containing all the dictionaries mentioned above (documents with its info)

### Works for

1. Journal Sources
2. Conference Proceedings Sources
3. Book Series Sources

### Doesn't work for

1. Book Sources (yet)

## Prerequisites

1. Python 3
2. Correct version chromedriver (depends on your version of Chrome, for more see http://chromedriver.chromium.org/)
3. If using Windows, please add Chromedriver in PATH (for more see https://www.computerhope.com/issues/ch000549.htm)

### NOTE!

Script hasn't been tested in other browser drivers, rather than Chrome

## Usage

1. Scroll down in main

![alt text](https://i.imgur.com/3LBGQqi.png)

2. Enter your credentials

```
    username_str = 'your_scopus_account_email' # login credentials
    password_str = 'your_password'
```
3. Edit query

```
    query = 'your_search_query'
```
    
4. In cmd (or command line)

```
python scopus-script.py
```
