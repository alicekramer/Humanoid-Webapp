import json
from collections import OrderedDict
from os import environ
import logging
import sys
from typing import Literal, Optional

""" SpeechDict = dict[str, list[str]]
Replacements = dict[str, str]
StatementsFunction = Literal["ui", "speech"] """
SUPPORTED_LANGUAGES = ["de", "en"]


def __get_replacements(lang):
    # type: (str) -> dict[str, str]
    path = "conf/speech_replacements/{0}.json".format(lang)
    res = {}
    try:
        with open(path, 'r') as file:
            res = json.load(file)
            logging.debug("loaded replacements from %s: %s", path, res)
    except FileNotFoundError as e:
        logging.warning("missing file: %s", path)
    except (IOError, Exception) as e:
        logging.error("replacements could not be loaded", exc_info=e)
    finally:
        return res or {}


def _patch_statements(statements, language):
    # type: (dict[str, list[str]], str) -> dict[str, list[str]]
    # Patch phrases with replacements to improve sound.
    replacements = __get_replacements(language)
    if replacements:
        def replace_all(string, replacements):
            # type: (str, dict[str, str]) -> str
            updated = False
            for (wrong, better) in replacements.items():
                if wrong in string:
                    updated = True
                    string = string.replace(wrong, better)
            if updated:
                logging.debug("updated string: %s", string)
            return string
        statements = {
            key: [replace_all(variant, replacements) for variant in variants] for (key, variants) in statements.items()
        }
        logging.debug("new statements: %s", statements)
    else:
        logging.warning("found no replacements for language '%s'", language)
    return statements


def _get_statements(func, section, lang, flavour=None):
    # type: (str, str, str, str|None) -> dict[str, list[str]]
    """Get phrases from a file and return it"""
    if environ.get('SHOWCASE_FLAVOUR') and (section == "showcase" or func == "speech") and not flavour:
        flavour = environ['SHOWCASE_FLAVOUR']
    if not flavour:
        flavour = "_default"
    path = "conf/{0}/{1}/{2}/{3}.json".format(func, section, flavour, lang)
    try:
        with open(path, 'r') as file:
            print("opened {0}".format(path))
            statements = json.load(file, object_pairs_hook=OrderedDict)
            return statements

    except IOError as e:
        logging.error("missing file in path: %s", path, exc_info=e)
        return {}
    except:
        logging.error("something else went wrong", exc_info=sys.exc_info())
        return {}


def get_statements_ui(section, lang):
    # type: (str, str) -> dict[str, list[str]]
    return _get_statements("ui", section, lang)


def get_statements_speech(section, lang):
    # type: (str, str) -> dict[str, list[str]]
    statements = _get_statements("speech", section, lang)
    statements = _patch_statements(statements, lang)
    return statements
