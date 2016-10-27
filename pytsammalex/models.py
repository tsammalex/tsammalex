# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from functools import partial
from datetime import date

import attr
from dateutil.parser import parse
from six import string_types

from pytsammalex.util import split_ids


DATE_QUALIFIERS = re.compile('unknown|before|circa|ca\.|\(?\?\)?|[\xa0]+')
YEAR_RANGE = re.compile('[0-9]{4}-[0-9]{4}$')


def regex_validator(regex, instance, attribute, value, allow_empty=False):
    if allow_empty and not value:
        return
    if not re.match(regex, value):
        raise ValueError('{0} is not a valid {1}'.format(value, attribute.name))


def convert_date(s):
    s = DATE_QUALIFIERS.sub('', s).strip()
    if YEAR_RANGE.match(s):
        s = s.split('-')[1]
    try:
        return None if not s else parse(s).date()
    except:
        raise ValueError('{0} is not a valid date'.format(s))


def convert_gps(s):
    # return (lat, lon) tuple
    if not s:
        return None, None
    return tuple(map(float, s.split()))


def valid_coordinates(instance, attribute, value):
    lat, lon = value
    if lat is not None and lon is not None:
        if (not -90 < lat < 90) or (not -180 < lon < 180):
            raise ValueError('{0} are not a valid (lat, lon) tuple'.format(value))


class Model(object):
    __field_map__ = {}

    @classmethod
    def fromdict(cls, d):
        clean = {}
        for field in attr.fields(cls):
            clean[field.name] = d.get(cls.__field_map__.get(field.name, field.name)) or ''
        return cls(**clean)

    def csv_row(self):
        def serialize(obj):
            if obj is None:
                return ''
            if isinstance(obj, string_types):
                return obj
            if isinstance(obj, list):
                return ';'.join(obj)
            if isinstance(obj, tuple):
                if obj[0] is None:
                    return ''
                return '{0:.6f} {1:.6f}'.format(*obj)
            if isinstance(obj, date):
                return obj.isoformat()
            raise ValueError(obj)
        return [serialize(getattr(self, f.name)) for f in attr.fields(self.__class__)]


@attr.s
class Images(Model):
    id = attr.ib(validator=partial(regex_validator, '[a-f0-9]{32}$'))
    taxa__id = attr.ib(validator=partial(regex_validator, '[a-z0-9]+$'))
    tags = attr.ib(convert=split_ids)
    mime_type = attr.ib(validator=partial(regex_validator, 'image/', allow_empty=True))
    src = attr.ib()
    creator = attr.ib()
    date = attr.ib(convert=convert_date)
    place = attr.ib()
    gps = attr.ib(convert=convert_gps, validator=valid_coordinates)
    permission = attr.ib()
    source = attr.ib()
    comments = attr.ib()


@attr.s
class Taxa(Model):
    __field_map__ = {'class_': 'class'}
    id = attr.ib(validator=partial(regex_validator, '[a-z0-9]+$'))
    scientific_name = attr.ib()
    synonyms = attr.ib()
    description = attr.ib()
    english_name = attr.ib()
    kingdom = attr.ib()
    phylum = attr.ib()
    class_ = attr.ib()
    order = attr.ib()
    family = attr.ib()
    genus = attr.ib()
    characteristics = attr.ib()
    biotope = attr.ib()
    countries__ids = attr.ib(convert=split_ids)
    general_uses = attr.ib()
    notes = attr.ib()
    refs__ids = attr.ib(convert=partial(split_ids, sep=re.compile(';')))
    links = attr.ib()


@attr.s
class Languages(Model):
    __field_map__ = {'a2nd_languages': '2nd_languages'}
    id = attr.ib()
    name = attr.ib()
    glottocode = attr.ib()
    contributors__ids = attr.ib(convert=split_ids)
    description = attr.ib()
    lineages__id = attr.ib()
    latitude = attr.ib()
    longitude = attr.ib()
    region = attr.ib()
    a2nd_languages = attr.ib()


@attr.s
class Names(Model):
    id = attr.ib()
    name = attr.ib()
    languages__id = attr.ib()
    taxa__id = attr.ib()
    ipa = attr.ib()
    audio = attr.ib()
    grammatical_info = attr.ib()
    plural_form = attr.ib()
    stem = attr.ib()
    root = attr.ib()
    basic_term = attr.ib()
    meaning = attr.ib()
    literal_translation = attr.ib()
    usage = attr.ib()
    source_language = attr.ib()
    source_form = attr.ib()
    linguistic_notes = attr.ib()
    related_lexemes = attr.ib()
    categories__ids = attr.ib(convert=split_ids)
    habitats__ids = attr.ib(convert=split_ids)
    introduced = attr.ib()
    uses__ids = attr.ib(convert=split_ids)
    importance = attr.ib()
    associations = attr.ib()
    ethnobiological_notes = attr.ib()
    comment = attr.ib()
    source = attr.ib()
    refs__ids = attr.ib(convert=partial(split_ids, sep=re.compile(';')))
    original_source = attr.ib()
    source_id = attr.ib()


@attr.s
class Audios(Model):
    id = attr.ib()
    names__id = attr.ib()
    tags = attr.ib()
    mime_type = attr.ib()
    src = attr.ib()
    creator = attr.ib()
    date = attr.ib()
    place = attr.ib()
    permission = attr.ib()
    source = attr.ib()
    source_url = attr.ib()
    comments = attr.ib()


@attr.s
class Categories(Model):
    id = attr.ib()
    name = attr.ib()
    meaning = attr.ib()
    languages__id = attr.ib()
    notes = attr.ib()


@attr.s
class Contributors(Model):
    id = attr.ib()
    name = attr.ib()
    sections = attr.ib()
    editor_ord = attr.ib()
    editor_sections = attr.ib()
    affiliation = attr.ib()
    research_project = attr.ib()
    homepage = attr.ib()
    notes = attr.ib()


@attr.s
class Habitats(Model):
    id = attr.ib()
    name = attr.ib()
    meaning = attr.ib()
    languages__id = attr.ib()
    notes = attr.ib()


@attr.s
class Lineages(Model):
    id = attr.ib()
    name = attr.ib()
    description = attr.ib()
    glottocode = attr.ib()
    family = attr.ib()
    family_glottocode = attr.ib()
    color = attr.ib()


@attr.s
class Uses(Model):
    id = attr.ib()
    name = attr.ib()
    description = attr.ib()
