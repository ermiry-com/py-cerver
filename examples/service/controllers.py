"""The controllers of the notes: each one takes the job of a request and returns
(error, errors, result), and the data lives in memory for the example.
"""

import threading
import time
import uuid

from cerver.http import validate_body_string, validate_body_list, validate_body_int
from cerver.http import validate_query_int, validate_query_string

from errors import SERVICE_ERROR_NONE, SERVICE_ERROR_BAD_REQUEST, SERVICE_ERROR_NOT_FOUND

TITLE_MAXIMUM = 128
TEXT_MAXIMUM = 4096
TAGS_MAXIMUM = 16

LIMIT_DEFAULT = 20
LIMIT_MAXIMUM = 100

# the seconds that a note lives without a ttl
TTL_DEFAULT = 3600
TTL_MAXIMUM = 86400

notes = {}
lock = threading.Lock ()

def note_values (note: dict) -> dict:
	"""The values of a note that a client gets."""
	return {key: value for key, value in note.items () if (key != "expires")}

def notes_list (job: dict) -> tuple:
	errors = {}
	limit = validate_query_int (job["query"], "limit", errors, required=False, default=LIMIT_DEFAULT, minimum=1, maximum=LIMIT_MAXIMUM)
	tag = validate_query_string (job["query"], "tag", errors, required=False)

	result = None
	if (not errors):
		with lock:
			selected = [note for note in notes.values () if ((tag is None) or (tag in note["tags"]))]

		result = {"notes": [note_values (note) for note in selected[:limit]], "count": len (selected)}

	return (SERVICE_ERROR_BAD_REQUEST if (errors) else SERVICE_ERROR_NONE, errors, result)

def note_create (job: dict) -> tuple:
	errors = {}
	body = job["body"]

	note = {
		"id": uuid.uuid4 ().hex,
		"title": validate_body_string (body, "title", errors, max_len=TITLE_MAXIMUM),
		"text": validate_body_string (body, "text", errors, required=False, default="", max_len=TEXT_MAXIMUM),
		"tags": validate_body_list (body, "tags", errors, required=False, default=[], item=str, max_items=TAGS_MAXIMUM),
		"created": int (time.time ())
	}

	ttl = validate_body_int (body, "ttl", errors, required=False, default=TTL_DEFAULT, minimum=1, maximum=TTL_MAXIMUM)

	result = None
	if (not errors):
		note["expires"] = note["created"] + ttl
		with lock:
			notes[note["id"]] = note

		result = note_values (note)

	return (SERVICE_ERROR_BAD_REQUEST if (errors) else SERVICE_ERROR_NONE, errors, result)

def note_get (job: dict) -> tuple:
	with lock:
		note = notes.get (job["params"]["id"])

	return (SERVICE_ERROR_NONE, None, note_values (note)) if (note) else (SERVICE_ERROR_NOT_FOUND, None, None)

def note_delete (job: dict) -> tuple:
	with lock:
		note = notes.pop (job["params"]["id"], None)

	return (SERVICE_ERROR_NONE, None, {"deleted": note["id"]}) if (note) else (SERVICE_ERROR_NOT_FOUND, None, None)

def notes_cleanup () -> int:
	"""Removes the notes that expired, returns how many."""
	now = int (time.time ())
	with lock:
		expired = [note_id for note_id, note in notes.items () if (note["expires"] <= now)]
		for note_id in expired:
			del notes[note_id]

	return len (expired)
