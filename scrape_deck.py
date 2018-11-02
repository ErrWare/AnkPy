'''
Ad-hoc module for scraping from the Python docs
and executing ankiConnect actions

'''

import json
import requests
import bs4
from collections import namedtuple
import logging
from collections import defaultdict
import re
import time
logging.basicConfig(level=logging.INFO)

__all__ = ['getSoup', 'ankiAction', 'deckExists', 'dtContainingClass',
            'dtLink', 'clozeSub', 'dtCloze', 'scrapeAnkiNotes', 'AnkiResponse',
            'ankiAddNotes']

AnkiResponse = namedtuple('AnkiResponse', ['result', 'error'])

def getSoup(url):
    '''
    Gets soup from url
    '''
    try:
        res = requests.get(url)
        res.raise_for_status()
        return bs4.BeautifulSoup(res.content, features='html5lib')
    except Exception:
        print('exception')
    return None

def ankiAction(action, params=None):
    '''
    Execute anki action with optional parameter
    '''
    command = {}
    command['action'] = action
    command['version'] = 6
    if params is not None:
        command['params'] = params
    response = json.loads(requests.post('http://127.0.0.1:8765',json=command).text)
    return AnkiResponse(response['result'], response['error'])

def ankiAddNotes(deckName, notes):
    if not deckExists(deckName):
        ankiAction('createDeck',{'deck':deckName})
    for note in notes:
        note['deckName'] = deckName
        note['modelName'] = 'ClozePy'
    return ankiAction('addNotes', params={"notes": notes})
    

def deckExists(deckName):
    '''
    True if anki deck exists
    '''
    decks, _ = ankiAction('deckNames')
    return deckName in decks

def dtContainingClass(dt):
    '''
    Returns the class name containing the dt with the trailing '.'
    '''
    if 'id' not in dt.attrs or '.' not in dt.attrs['id']:
        return ''
    else:
        id_ = dt.attrs['id']
        last_dot = id_.rfind('.')
        return id_[0:last_dot+1]
        
def dtLink(dt, page):
    '''
    Returns an href based on page to the nearest tag with an id
    '''
    if 'id' in dt.attrs:
        page += '#' + dt.attrs['id']
    elif dt.find_parent(id=True) is not None:
        page += '#' + dt.find_parent(id=True).attrs['id']
    return page

def clozeSub(mo):
    '''
    Substitutes the second group in a match object with an anki cloze of itself.
    '''
    clozeSub.counter += 1
    return '{somechar}{{{{c{counter}::{text}}}}}'.format(
        somechar = mo.group(1),
        counter = clozeSub.counter,
        text = mo.group(2)
    )
clozeSub.counter = 0

def dtCloze(dt):
    '''
    Formats the signature information of a dt tag as an Anki Cloze
    '''
    clozeSub.counter=0
    normText = ''.join(c for c in dt.text if ord(c) < 128)
    normText = normText.strip()
    if dt.find('code', class_='descclassname') is None:
        normText = dtContainingClass(dt) + normText
    clozeText = re.sub(r'([^\*A-z]|^|\[)([a-zA-Z_]+)',clozeSub,normText)
    if 'tuple' in normText:
        time.sleep(15)
    return clozeText

def scrapeAnkiNotes(page):
    notes = []
    logging.info(f'anki scraping <{page}>')
    soup = getSoup(page)
    for dl in soup.find_all('dl'):
        try:
            if dl.p is not None:
                body = dl.p.text.replace('\n', ' ')
            else:
                continue
            tags = []
            try:
                tags = dl.attrs['class']
            except:
                pass
            
            for dt in dl.find_all('dt', recursive=False):
                note = defaultdict(dict)
                note['tags'] = tags
                note['fields']['Signature'] = dtCloze(dt)
                note['fields']['Body'] = body
                note['fields']['Link'] = dtLink(dt, page)
                notes.append(note)
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except:
            logging.exception('Exception scraping {}'.format(dl.text))
    return notes

if __name__ == '__main__':
    '''
    Initial attempt at structuring this workflow
    it now only serves as a proof of concept.

    To operate the project run scrapePython.py then,
    configure the directory/file hierarchy according to the deck separation desired then,
    run addNotes.py
    '''
    CONFIG_FILE = 'DeckConfTypes.json'

    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)

    logging.info(ankiAction('version'))
    logging.info(deckExists(config['name']))
    if not deckExists(config['name']):
        ankiAction('createDeck',{'deck':config['name']})
    logging.info(deckExists(config['name']))

    logging.info(ankiAction('modelNames'))

    notes = []

    for page in config['pages']:
        notes += scrapeAnkiNotes(page)

    for note in notes:
        note['deckName'] = config['name']
        note['modelName'] = 'ClozePy'


    logging.info(len(notes))

    result, error = ankiAction('addNotes', params={"notes": notes})
    for note, r in zip(notes, result):
        if r is None:
            logging.info(note['fields']['Signature'])
    logging.info(result)

    with open(config['name']+'_deck.json', 'w') as f:
        json.dump(notes, f)
