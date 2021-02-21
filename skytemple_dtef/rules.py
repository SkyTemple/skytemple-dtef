"""
This module contains the 47 base rules and a function to get the 209 derivations of it (for each of the base
rules). In total this makes 256 rules, each rule codes which of the 8 neighboring tiles have the same state as the
one affected by the rule.
"""
#  Copyright 2020-2021 Parakoopa and the SkyTemple Contributors
#
#  This file is part of SkyTemple.
#
#  SkyTemple is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SkyTemple is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SkyTemple.  If not, see <https://www.gnu.org/licenses/>.
from typing import Dict, Set, Iterable

from skytemple_files.graphics.dma.model import DmaNeighbor
from skytemple_files.common.i18n_util import _, f

# The 47 base rule-set, in the order as drawn on the tilesheet. PLEASE NOTE that there is one entry "None", which
# creates an empty tile on the tilesheet (= the list contains 48 entries, one is None).
# Use get_rule_variations to get the variations for these base rules.
REMAP_RULES = [
    DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.WEST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.WEST | DmaNeighbor.EAST,
    DmaNeighbor.WEST | DmaNeighbor.SOUTH,

    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH | DmaNeighbor.SOUTH,
    0,
    DmaNeighbor.NORTH | DmaNeighbor.WEST,

    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.EAST,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST,
    DmaNeighbor.NORTH | DmaNeighbor.EAST,
    DmaNeighbor.SOUTH,
    None,

    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.EAST,
    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.WEST,

    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST,
    DmaNeighbor.NORTH | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH,
    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.SOUTH,

    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,

    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST,
    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST,

    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
    DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH,
    DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST,
]


def get_rule_variations(input_rules: Iterable[int]) -> Dict[int, Set[int]]:
    """
    Returns all 256-set rules which encode the same tile in a reduced rule-set of 47 rules
    (including the rule passed in). If the rule passed in is None, an empty list is returned.
    Rules are ORed numbers created form DmaNeighbors. See REMAP_RULES for the 47 rule-set.
    The returned value is a dict, where each key is one of the input rules, and the values ALL matching 256-rules.
    """
    rules = {x: set() for x in input_rules}
    for rule in range(0, 256):
        orig_rule = rule
        if rule & DmaNeighbor.NORTH_WEST == DmaNeighbor.NORTH_WEST:
            if not rule & DmaNeighbor.NORTH == DmaNeighbor.NORTH or not rule & DmaNeighbor.WEST == DmaNeighbor.WEST:
                rule &= ~DmaNeighbor.NORTH_WEST

        if rule & DmaNeighbor.NORTH_EAST == DmaNeighbor.NORTH_EAST:
            if not rule & DmaNeighbor.NORTH == DmaNeighbor.NORTH or not rule & DmaNeighbor.EAST == DmaNeighbor.EAST:
                rule &= ~DmaNeighbor.NORTH_EAST

        if rule & DmaNeighbor.SOUTH_WEST == DmaNeighbor.SOUTH_WEST:
            if not rule & DmaNeighbor.SOUTH == DmaNeighbor.SOUTH or not rule & DmaNeighbor.WEST == DmaNeighbor.WEST:
                rule &= ~DmaNeighbor.SOUTH_WEST

        if rule & DmaNeighbor.SOUTH_EAST == DmaNeighbor.SOUTH_EAST:
            if not rule & DmaNeighbor.SOUTH == DmaNeighbor.SOUTH or not rule & DmaNeighbor.EAST == DmaNeighbor.EAST:
                rule &= ~DmaNeighbor.SOUTH_EAST

        if rule in rules:
            rules[rule].add(orig_rule)
        else:
            raise ValueError(f(_("No match found for rule {orig_rule}. Input set correct?")))

    return rules
