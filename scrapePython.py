'''
Scrapes notes from the python docs into json files corresponding
to the section they came from

'''

from scrape_deck import *
import logging
import json
import requests
import bs4
import os
logging.basicConfig(setlevel=logging.INFO)
logging.info('hello')

def firstTextIsCode(tag):
    try:
        return tag.text.startswith(tag.code.text)
    except:
        return False
    
pyNameSpace = 'https://docs.python.org/3/library/'
pypage = requests.get(pyNameSpace + 'index.html')
tocSoup = bs4.BeautifulSoup(pypage.text, features='html5lib')
contentSections = tocSoup.find_all('li',class_='toctree-l1')[1:-2]
NOTES_FOLDER = 'notes_dummy'
logging.info(len(contentSections))
for section in contentSections:
    sectionName = section.a.text.strip()
    logging.info('Section <{}>'.format(sectionName))
    if 'Python' in sectionName:
        deckName = sectionName
    else:
        deckName = 'Python ' + sectionName
    notes = scrapeAnkiNotes(pyNameSpace+section.a.attrs['href'])
    logging.info('Found {} li, {} have code first'.format(
        len(section.find_all('li')),
        len(list(1 for li in section.find_all('li') if firstTextIsCode(li)))
    ))
    for li in section.find_all('li'):
        if firstTextIsCode(li):
            notes += scrapeAnkiNotes(pyNameSpace + li.a.attrs['href'])
    
    filename = deckName + '.json'
    with open(os.path.join(NOTES_FOLDER,filename),'w') as f:
        json.dump(notes, f)
    
    logging.info('Dumped {} notes to {}'.format(len(notes), filename))