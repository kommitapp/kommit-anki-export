from aqt import mw
from aqt.utils import showInfo
from aqt.qt import *

import json
from string import Template
from anki import hooks
from anki import exporting
from datetime import datetime

# INTERFACE

def InterfaceMenuActionDidClick():
	ControlExportData()

# CONTROL

def _stringify(a):
	return json.dumps(a, separators=(',', ':'), default=str)

def _date(e):
	return datetime.utcfromtimestamp(e / 1000).strftime('%Y-%m-%dT%H:%M:%SZ')

def _map(a, b):
	return list(map(a, b))

def exportNotes(spacings):
	return _map(mw.col.getCard, spacingIDs)

def exportChronicle(e):
	return {
		'KOMChronicleDrawDate': _date(e[0] / 1000),
	}

def exportSpacing(e, forward):
	if e == None:
		return None;

	chronicles = _map(exportChronicle, mw.col.db.all("select * from revlog where cid = " + str(e.id)))

	return {
		'KOMSpacingID': Template('$id-$direction').substitute(id=e.id, direction=('forward' if forward else 'backward')),
		'KOMSpacingDrawDate': chronicles[0]['KOMChronicleDrawDate'],
		'KOMSpacingDueDate': str(e.due),
		'KOMSpacingInterval': e.ivl,
		'KOMSpacingMultiplier': e.factor / 1000,
		'KOMSpacingIsSuspended': e.queue == -1,
		'KOMSpacingChronicles': chronicles,
		'queue': e.queue,
		'reps': e.reps,
		'lapses': e.lapses,
		'left': e.left,
		'odue': e.odue,
		'odid': e.odid,
		'flags': e.flags,
		'data': e.data,
		'list': mw.col.db.all("select * from revlog where cid = " + str(e.id)),
	}

def exportCard(e, deckID, forward, backward):
	return {
		'KOMCardID': str(e.id),
		'KOMCardDeckID': deckID,
		'KOMCardFrontText': e.fields[0],
		'KOMCardRearText': e.fields[1],
		'KOMCardNotes': e.fields[2],
		'KOMCardCreationDate': _date(e.id),
		'KOMCardModificationDate': _date(e.mod * 1000),
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
		'KOMDeckCreationDate': _date(e['id']),
		'KOMDeckModificationDate': _date(e['mod']),
		'$KOMDeckCards': exportCards(mw.col.decks.cids(e['id'])[0:2], str(e['id'])),
	}

def getDecks():
	# return list(map(exportDeck, [n for n in mw.col.decks.all() if n['name'] != 'Default']))
	return list(map(exportDeck, [n for n in mw.col.decks.all() if n['name'] == 'english']))

def writeJSON(e):
	with open('/data/output.json', 'w') as outfile: 
		json.dump(e, outfile, indent="	") 

def ControlExportData():
	writeJSON(getDecks())

# SETUP

def SetupEverything():
	SetupMenuItem()

	SetupExportItem()

def SetupMenuItem():
	action = QAction('Export data to Kommit', mw)

	action.triggered.connect(InterfaceMenuActionDidClick)

	mw.form.menuTools.addAction(action)

def SetupExportItem():
	class KommitJSONExporter(exporting.Exporter):
		key = _('Kommit JSON')
		ext = '.json'
		includeHTML = False

		def __init__(self, col) -> None:
			exporting.Exporter.__init__(self, col)

		def doExport(self, file) -> None:
			out = 'data'
			self.count = len([])
			file.write(out.encode('utf-8'))

	def on_exporters_list_created(exporters):
		def id(obj):
			return ('%s (*%s)' % (obj.key, obj.ext), obj)

		exporters.append(id(KommitJSONExporter))

	hooks.exporters_list_created.append(on_exporters_list_created)

# LIFECYCLE

def LifecycleModuleDidLoad():
	SetupEverything()

LifecycleModuleDidLoad()