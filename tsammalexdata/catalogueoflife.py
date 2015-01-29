"""
Functionality to retrieve information from the Catalogue of Life Web Service

.. seealso:: http://webservice.catalogueoflife.org/col/webservice
"""
from __future__ import print_function, unicode_literals, absolute_import, division
import sys
import os
from xml.etree import cElementTree as et

import requests

from tsammalexdata.util import data_file, jsonload, jsondump, csv_items


def api(**kw):
    res = requests.get('http://www.catalogueoflife.org/col/webservice', params=kw)
    return et.fromstring(res.content).find('result')


def text(e, ee):
    ee = e.find(ee)
    return (ee.text if ee is not None else '') or ''


def get_id(name):
    result = api(name=name)
    if result:
        if text(result, 'name_status') == 'accepted name':
            return text(result, 'id')
        if result.find('accepted_name'):
            return text(result.find('accepted_name'), 'id')


class Taxon(object):
    def __init__(self, e):
        for attr in 'id name rank url'.split():
            setattr(self, attr, text(e, attr))

    def as_dict(self):
        return dict(id=self.id, name=self.name, url=self.url)


def get_info(id_):
    result = api(id=id_, response='full')
    if result:
        # classification: taxon.id name rank url
        # synonyms: synonym.name
        res = {k: text(result, k) for k in 'genus species author url'.split()}
        res['distribution'] = [
            region.split()[0] for region in
            text(result, 'distribution').split('; ') if region]
        if result.find('classification'):
            res['classification'] = {
                t.rank.lower(): t.as_dict() for t in
                [Taxon(e) for e in result.find('classification').findall('taxon')]}
        if result.find('synonyms'):
            res['synonyms'] = filter(
                None,
                [text(e, 'name') for e in result.find('synonyms').findall('synonym')])
        return {k: v for k, v in res.items() if v}


if __name__ == '__main__':
    args = sys.argv[1:]
    if args:
        print(get_id(args[0]))
    else:
        fname = data_file('external', 'catalogueoflife.json')
        if os.path.exists(fname):
            species = jsonload(fname)
        else:
            species = {}

        for item in csv_items('species.csv'):
            if item['id'] not in species:
                try:
                    id_ = get_id(item['scientific_name'])
                    if id_:
                        species[item['id']] = get_info(id_)
                    else:
                        raise ValueError
                except:
                    # we'll have to try again next time!
                    print('missing:', item['id'])
                    continue

        jsondump(species, fname)
