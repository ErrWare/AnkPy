'''
Adds the collected notes to the decks corresponding to the
file hierarchy

Expected hierarchy:

folder_1/
    deck_1/
        notes_1.json
        notes_2.json
        ...
    deck_2/
        notes_k.json
        notes_k+1.json
        ...
    ...
'''

from ankpy import ankiAddNotes
import os
import json
import textwrap

deckSection = 'Python::Native'
NOTES_DIR = 'notes'
for deckdir in os.listdir(NOTES_DIR):
    deckName = f'{deckSection}::{deckdir}'
    print(deckName)
    for d in os.listdir(os.path.join(NOTES_DIR,deckdir)):
        print('\t',d)
        with open(os.path.join(NOTES_DIR,deckdir,d),'r') as f:
            notes = json.load(f)
        result, _ = ankiAddNotes(deckName, notes)
        print(textwrap.indent(textwrap.fill(str(result),80),'\t\t'))