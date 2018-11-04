'''
Scrapes notes from the python docs into json files corresponding
to the section they came from

'''

from ankpy import *
import logging
import json
import requests
import bs4
import os
logging.basicConfig(level=logging.INFO)
logging.info('hello')

def firstTextIsCode(tag):
    try:
        return tag.text.startswith(tag.code.text)
    except:
        return False

def pypage(page):
    return pypage._ns + page
pypage._ns = 'https://docs.python.org/3/library/'
NOTES_FOLDER = 'notes_dummy'
if not os.path.exists(NOTES_FOLDER):
    os.makedirs(NOTES_FOLDER)
    
indexSoup = getSoup(pypage('index.html'))
contentSections = indexSoup.find_all('li',class_='toctree-l1')[1:-2]
for section in contentSections:
    sectionName = section.a.text.strip()
    logging.info('Section <{}>'.format(sectionName))
    notes = scrapeAnkiNotes(pypage(section.a.attrs['href']))
    logging.info('Found {} li, {} have code first'.format(
        len(section.find_all('li')),
        len(list(1 for li in section.find_all('li') if firstTextIsCode(li)))
    ))
    for li in section.find_all('li'):
        if firstTextIsCode(li):
            notes += scrapeAnkiNotes(pypage(li.a.attrs['href']))
    
    filename = sectionName + '.json'
    with open(os.path.join(NOTES_FOLDER,filename),'w') as f:
        json.dump(notes, f)
    
    logging.info(f'Dumped {len(notes)} notes to {filename}')