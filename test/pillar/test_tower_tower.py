# -*- coding: utf-8 -*-

import inspect
import pytest
import six

from test.conftest import __pillars__


@pytest.fixture
def mod():
    return inspect.getmodule(__pillars__['tower'])


@pytest.fixture
def tower(mod):
    return mod.Tower('minion-id', 'base', {
        'pillar': {
            'key': 'value',
            'list': [1, 2]
        }
    })


def test_get_traverse(tower):
    assert tower.get('pillar:key') == 'value'

def test_get_default(tower):
    assert tower.get('pillar:none') == None

def test_get_default_value(tower):
    assert tower.get('pillar:none', default=5) == 5


def test_update(tower):
    tower.update({
        'pillar': {
            'key': 'new_value',
            'list': [3]
        }
    })

    assert tower == {
        'pillar': {
            'key': 'new_value',
            'list': [1, 2, 3]
        }
    }

def test_update_override(tower):
    '''
    Merging different types will override
    '''
    tower.update({'pillar': {'list': 'fake'}})

    assert tower['pillar']['list'] == 'fake'


def test_merge(tower):
    tgt = {'a': True, 'b': [1]}
    ret = tower.merge(tgt, {'b': [2]})

    assert ret is tgt
    assert ret == {'a': True, 'b': [1, 2]}


def test_merge_copy(tower):
    tgt = {}
    mod = {'a': {'b': 2}}

    tower.merge(tgt, mod)

    assert tgt == {'a': {'b': 2}}
    assert tgt['a'] is not mod['a']


def test_merge_copy_list(tower):
    tgt = [{'a': 1}]
    mod = [{'b': 2}]

    tower.merge(tgt, mod)

    assert tgt == [{'a': 1}, {'b': 2}]
    assert tgt[1] is not mod[0]


def test_merge_list_strategy_remove(tower):
    tgt = ['a', 'b']
    mod = [{'__': 'remove'}, 'a']

    tower.merge(tgt, mod)

    assert tgt == ['b']


def test_merge_list_strategy_remove_non_existant(tower):
    tgt = ['a', 'b']
    mod = [{'__': 'remove'}, 'c']

    tower.merge(tgt, mod)

    assert tgt == ['a', 'b']


def test_merge_list_strategy_merge_first(tower):
    tgt = ['a', 'b']
    mod = [{'__': 'merge-first'}, 'c']

    tower.merge(tgt, mod)

    assert tgt == ['c', 'a', 'b']


def test_merge_list_strategy_merge_overwrite(tower):
    tgt = ['a', 'b']
    mod = [{'__': 'overwrite'}, 'c']

    tower.merge(tgt, mod)

    assert tgt == ['c']


def test_format(tower):
    tower.update({'app': {'name': 'MyApp'}})

    assert tower.format('X{app.name}X') == 'XMyAppX'


if six.PY3:
    def test_format_bytes(tower):
        tower.update({'app': {'name': 'MyApp'}})

        assert tower.format(b'X{app.name}X') == b'X{app.name}X'


def test_format_dict(tower):
    tower.update({'ports': [80, 443]})

    assert tower.format({'bind': '0.0.0.0:{ports.0}'}) \
        == {'bind': '0.0.0.0:80'}


def test_format_list(tower):
    tower.update({'ports': [80, 443]})

    assert tower.format(['{ports.0}', '{ports.1}']) == ['80', '443']


def test_format_arg(tower):
    assert tower.format({'app': '{name}'}, name='APP') == {'app': 'APP'}
