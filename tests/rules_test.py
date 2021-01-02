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
import os
import unittest
from itertools import chain

from skytemple_dtef.rules import *
from skytemple_files.common.types.file_types import FileType
from skytemple_files.graphics.dma.model import DmaType

NUMBER_COMBINATIONS = 256


class RulesTestCase(unittest.TestCase):
    """
    Tests that the REMAP_RULES and get_rule_variations function in the rules module return all possible 256
    neighbor configurations and uses a DMA file to check that rules which are effectively the same as reported by
    get_rule_variations are actually referencing the same DPC tile.
    """
    def test_get_rule_variations__all_rules_exist(self):
        combinations = list(chain.from_iterable(get_rule_variations(REMAP_RULES).values()))

        self.assertEqual(NUMBER_COMBINATIONS, len(set(combinations)),
                         f"There must be a match for all {NUMBER_COMBINATIONS} rules.")
        self.assertEqual(len(combinations), len(set(combinations)),
                         f"There must be no duplicate rules for the 47 base rules.")

    def test_get_rule_variations__dma_fixture_matches(self):
        with open(self.__fixture_path(), 'rb') as f:
            dma = FileType.DMA.deserialize(f.read())
        for rule, rule_vars in get_rule_variations(REMAP_RULES).items():
            items = [dma.get(DmaType.WALL, r)[0] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all wall var0 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.WALL, r)[1] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all wall var1 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.WALL, r)[2] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all wall var2 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.FLOOR, r)[0] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all floor var0 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.FLOOR, r)[1] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all floor var1 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.FLOOR, r)[2] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all floor var2 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.WATER, r)[0] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all water var0 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.WATER, r)[1] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all water var1 DMA entries must be the same for all reported variations.")
            items = [dma.get(DmaType.WATER, r)[2] for r in rule_vars]
            self.assertTrue(all(x == items[0] for x in items),
                            f"For rule {rule} all water var2 DMA entries must be the same for all reported variations.")

    @staticmethod
    def __fixture_path():
        return os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         'fixtures',
                         'dummy.dma')
        )
