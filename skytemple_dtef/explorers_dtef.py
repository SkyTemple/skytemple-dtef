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

from math import floor, ceil
from typing import List, Dict
from xml.etree import ElementTree

from PIL import Image

from skytemple_dtef.dungeon_xml import DungeonXml, RestTileMapping, RestTileMappingEntry
from skytemple_dtef.rules import get_rule_variations, REMAP_RULES
from skytemple_files.graphics.dma.model import Dma, DmaType, DmaExtraType
from skytemple_files.graphics.dpc.model import Dpc, DPC_TILING_DIM
from skytemple_files.graphics.dpci.model import Dpci, DPCI_TILE_DIM
from skytemple_files.graphics.dpl.model import Dpl
from skytemple_files.graphics.dpla.model import Dpla


TILESHEET_WIDTH = 6
TILESHEET_HEIGHT = 8
TW = DPCI_TILE_DIM * DPC_TILING_DIM
VAR0_FN = 'tileset_0.png'
VAR1_FN = 'tileset_1.png'
VAR2_FN = 'tileset_2.png'
MORE_FN = 'tileset_more.png'


class ExplorersDtef:
    def __init__(self, dma: Dma, dpc: Dpc, dpci: Dpci, dpl: Dpl, dpla: Dpla):
        self.dma = dma
        self.dpc = dpc
        self.dpci = dpci
        self.dpl = dpl
        self.dpla = dpla

        chunks = self.dpc.chunks_to_pil(self.dpci, self.dpl.palettes, 1)
        self.var0 = Image.new('P', (TILESHEET_WIDTH * 3 * TW, TILESHEET_HEIGHT * TW))
        self.var1 = Image.new('P', (TILESHEET_WIDTH * 3 * TW, TILESHEET_HEIGHT * TW))
        self.var2 = Image.new('P', (TILESHEET_WIDTH * 3 * TW, TILESHEET_HEIGHT * TW))
        pal = chunks.getpalette()
        self.var0.putpalette(pal)
        self.var1.putpalette(pal)
        self.var2.putpalette(pal)

        def paste(fimg, chunk_index, x, y):
            fimg.paste(
                chunks.crop((0, chunk_index * TW, TW, chunk_index * TW + TW)),
                (x * TW, y * TW)
            )

        # Process tiles
        self._variation_map = [[], [], []]
        self._coord_map = {}
        # Pre-fill variation maps
        for ti, the_type in enumerate((DmaType.WALL, DmaType.WATER, DmaType.FLOOR)):
            for i, base_rule in enumerate(get_rule_variations(REMAP_RULES).keys()):
                if base_rule is None:
                    continue
                x = i % TILESHEET_WIDTH + (TILESHEET_WIDTH * ti)
                y = floor(i / TILESHEET_WIDTH)
                variations = self.dma.get(the_type, base_rule)
                already_printed = set()
                for img, iv in zip((self.var0, self.var1, self.var2), range(len(variations))):
                    variation = variations[iv]
                    if variation in already_printed:
                        continue
                    already_printed.add(variation)
                    self._coord_map[variation] = (x, y)
                    self._variation_map[iv].append(variation)

        # Non standard tiles
        self.rest_mappings: List[RestTileMapping] = []
        self._tiles_to_draw_on_more = []
        self._rest_mappings_idxes: Dict[int, int] = {}  # dpc -> rest_mappings index

        # Process all normal rule tiles (47-set and check 256-set extended)
        for ti, the_type in enumerate((DmaType.WALL, DmaType.WATER, DmaType.FLOOR)):
            for i, (base_rule, derived_rules) in enumerate(get_rule_variations(REMAP_RULES).items()):
                if base_rule is None:
                    continue
                x = i % TILESHEET_WIDTH + (TILESHEET_WIDTH * ti)
                y = floor(i / TILESHEET_WIDTH)
                variations = self.dma.get(the_type, base_rule)
                already_printed = set()
                for img, iv in zip((self.var0, self.var1, self.var2), range(len(variations))):
                    variation = variations[iv]
                    if variation in already_printed:
                        continue
                    already_printed.add(variation)
                    paste(img, variation, x, y)
                for other_rule in derived_rules:
                    if other_rule == base_rule:
                        continue
                    r_variations = self.dma.get(the_type, other_rule)
                    for index, (r_var, var) in enumerate(zip(r_variations, variations)):
                        if r_var != var:
                            # Process non-standard mappings
                            self._add_extra_mapping(other_rule, r_var, index)

        # Process all extra tiles
        for i, m in enumerate(self.dma.chunk_mappings[0x300 * 3:]):
            self._add_extra_mapping(0x300 * 3 + i, m, None)

        more_width = TILESHEET_WIDTH * 3 * TW
        more_height = max(TW, ceil(len(self._tiles_to_draw_on_more) / more_width) * TW)
        self.rest = Image.new('P', (more_width, more_height))
        for i, tile_more in enumerate(self._tiles_to_draw_on_more):
            x = i % (TILESHEET_WIDTH * 3)
            y = floor(i / (TILESHEET_WIDTH * 3))
            paste(self.rest, tile_more, x, y)
        self.rest.putpalette(pal)

    def get_xml(self) -> ElementTree.Element:
        return DungeonXml.generate(self.dpla, TW, self.rest_mappings)

    def get_tiles(self) -> List[Image.Image]:
        return [self.var0, self.var1, self.var2, self.rest]

    @staticmethod
    def get_filenames():
        return [VAR0_FN, VAR1_FN, VAR2_FN, MORE_FN]

    def _add_extra_mapping(self, i, m, variation):
        if m in self._variation_map[0]:
            fn = VAR0_FN
            x, y = self._coord_map[m]
        elif m in self._variation_map[1]:
            fn = VAR1_FN
            x, y = self._coord_map[m]
        elif m in self._variation_map[2]:
            fn = VAR2_FN
            x, y = self._coord_map[m]
        else:
            fn = MORE_FN
            oi = len(self._tiles_to_draw_on_more)
            x = oi % (TILESHEET_WIDTH * 3)
            y = floor(oi / (TILESHEET_WIDTH * 3))
        if m not in self._rest_mappings_idxes:
            if fn == MORE_FN:
                self._tiles_to_draw_on_more.append(m)
            self.rest_mappings.append(RestTileMapping(x, y, [], fn))
            self._rest_mappings_idxes[m] = len(self.rest_mappings) - 1
        mappings = self.rest_mappings[self._rest_mappings_idxes[m]].mappings
        if i < 0x300 * 3:
            # Normal
            dma_type = DmaType.WALL
            if i >= 0x200:
                dma_type = DmaType.FLOOR
            elif i >= 0x100:
                dma_type = DmaType.WATER
            mappings.append(RestTileMappingEntry(dma_type, i, variation))
        else:
            # Special
            typ = i % 3
            i_real = int(i / 3) - 0x300
            mappings.append(RestTileMappingEntry(DmaExtraType(typ), 0, i_real))
