from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

import json

# INTERFACE

def InterfaceMenuActionDidClick():
	ControlExportData()

# CONTROL

def _stringify(a):
	return json.dumps(a, separators=(',', ':'))

def _map(a, b):
	return list(map(a, b))

def exportNotes(spacings):
	return _map(mw.col.getCard, spacingIDs)

def exportNote(e):
	return {
		"KOMSpacingID": spacing.id,
		"data": 'json.dumps(item)',
	}

def exportCard(e, deckID):
	return {
		"KOMCardID": str(e.id),
		"KOMCardDeckID": deckID,
		"KOMCardFrontText": e.fields[0],
		"KOMCardRearText": e.fields[1],
		"KOMCardNotes": e.fields[2],
		"KOMCardCreationDate": str(e.id),
		"KOMCardModificationDate": str(e.mod),
		"KOMCardTags": e.tags,
	}

def exportCards(spacingIDs, deckID):
	spacings = _map(mw.col.getCard, spacingIDs)

	cardIDs = []
	cards = []

	for e in spacings:
		item = e.note()
		if item.id not in cardIDs:
			cardIDs.append(item.id)
			cards.append(exportCard(item, deckID))

	return cards

def exportDeck(e):
	return {
		"KOMDeckID": str(e['id']),
		"KOMDeckName": e['name'],
		"KOMDeckCreationDate": str(e['id']),
		"KOMDeckModificationDate": str(e['mod']),
		"$KOMDeckCards": exportCards(mw.col.decks.cids(e['id'])[0:2], str(e['id'])),
	}

def getDecks():
	# return list(map(exportDeck, [n for n in mw.col.decks.all() if n['name'] != 'Default']))
	return list(map(exportDeck, [n for n in mw.col.decks.all() if n['name'] == 'english']))

def ControlExportData():
	showInfo(_stringify(getDecks()))

# SETUP

def SetupEverything():
	SetupMenuItem()

def SetupMenuItem():
	action = QAction('Export data to Kommit', mw)

	action.triggered.connect(InterfaceMenuActionDidClick)

	mw.form.menuTools.addAction(action)
	
# LIFECYCLE

def LifecycleModuleDidLoad():
	SetupEverything()

LifecycleModuleDidLoad()