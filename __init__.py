from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

import json
from string import Template

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

def exportSpacing(e, forward):
	if e == None:
		return None;

	return {
		'KOMSpacingID': Template('$id-$direction').substitute(id=e.id, direction=('forward' if forward else 'backward')),
		'KOMSpacingDueDate': str(e.due),
		'KOMSpacingIsSuspended': e.queue == -1,
		'data': 'json.dumps(e)',
		'queue': e.queue,
	}

def exportCard(e, deckID, forward, backward):
	return {
		'KOMCardID': str(e.id),
		'KOMCardDeckID': deckID,
		'KOMCardFrontText': e.fields[0],
		'KOMCardRearText': e.fields[1],
		'KOMCardNotes': e.fields[2],
		'KOMCardCreationDate': str(e.id),
		'KOMCardModificationDate': str(e.mod),
		'KOMCardTags': e.tags,
		'$KOMCardSpacingForward': None if forward == None else forward,
		'$KOMCardSpacingBackward': None if backward == None else backward,
	}

def exportCards(spacingIDs, deckID):
	spacings = _map(mw.col.getCard, spacingIDs)

	cardDataByID = {}

	for e in spacings:
		item = e.note()

		if 'a' not in cardDataByID:
			cardDataByID[str(item.id)] = {
				'note': item,
				'forward': None,
				'backward': None,
			}

		if e.type != 2:
			cardDataByID[str(item.id)]['forward'] = e

		if e.type == 2:
			cardDataByID[str(item.id)]['backward'] = e

	def _exportCard(e):
		return exportCard(e['note'], deckID, exportSpacing(e['forward'], True), exportSpacing(e['backward'], False))

	return _map(_exportCard, cardDataByID.values())

def exportDeck(e):
	return {
		'KOMDeckID': str(e['id']),
		'KOMDeckName': e['name'],
		'KOMDeckCreationDate': str(e['id']),
		'KOMDeckModificationDate': str(e['mod']),
		'$KOMDeckCards': exportCards(mw.col.decks.cids(e['id'])[0:2], str(e['id'])),
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