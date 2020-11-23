#  Copyright 2020 Parakoopa
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
from typing import Optional, List, Union, Tuple, Dict
from xml.etree import ElementTree

from PIL import Image

from skytemple_dtef.dungeon_xml import DungeonXml, RestTileMapping, RestTileMappingEntry
from skytemple_files.common.tiled_image import TilemapEntry
from skytemple_files.common.types.file_types import FileType
from skytemple_files.graphics.dma.model import Dma, DmaNeighbor, DmaType, DmaExtraType
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


class Dtef:
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

        # Process standard tiles
        dpcs_unprocessed = set((i for i in dma.chunk_mappings))
        variation_map = [[], [], []]
        coord_map = {}
        for ti, the_type in enumerate((DmaType.WALL, DmaType.WATER, DmaType.FLOOR)):
            for i, rule in enumerate(REMAP_RULES):
                if rule is None:
                    continue
                x = i % TILESHEET_WIDTH + (TILESHEET_WIDTH * ti)
                y = floor(i / TILESHEET_WIDTH)
                variations = self.dma.get(the_type, rule)
                for img, iv in zip((self.var0, self.var1, self.var2), range(len(set(variations)))):
                    variation = variations[iv]
                    variation_map[iv].append(variation)
                    coord_map[variation] = (x, y)
                    if variation in dpcs_unprocessed:
                        dpcs_unprocessed.remove(variation)
                    paste(img, variation, x, y)
                i += 1

        # Process all non-standard tiles
        # TODO: WE NEED TO MAKE SURE THE REMAINING 209 CONFIGURATIONS ARE ALSO MAPPED CORRECTLY OR ADD THEM!
        self.rest_mappings: List[RestTileMapping] = []
        tiles_to_draw_on_more = []
        rest_mappings_idxes: Dict[int, int] = {}  # dpc -> rest_mappings index
        for i, m in enumerate(self.dma.chunk_mappings):
            # Collect all unprocessed and the DMA extra tiles
            if m not in rest_mappings_idxes and (m in dpcs_unprocessed or i >= 0x300 * 3):
                fn = MORE_FN
                if m not in dpcs_unprocessed:
                    if m in variation_map[0]:
                        fn = VAR0_FN
                    elif m in variation_map[1]:
                        fn = VAR1_FN
                    elif m in variation_map[2]:
                        fn = VAR2_FN
                    else:
                        raise ValueError("Invalid tile.")
                    x, y = coord_map[m]
                else:
                    oi = len(tiles_to_draw_on_more)
                    x = oi % (TILESHEET_WIDTH * 3)
                    y = floor(oi / (TILESHEET_WIDTH * 3))
                    tiles_to_draw_on_more.append(m)
                self.rest_mappings.append(RestTileMapping(x, y, [], fn))
                rest_mappings_idxes[m] = len(self.rest_mappings) - 1
                if m in dpcs_unprocessed:
                    dpcs_unprocessed.remove(m)
            if m in rest_mappings_idxes:
                mappings = self.rest_mappings[rest_mappings_idxes[m]].mappings
                if i < 0x300 * 3:
                    # Normal
                    variation = i % 3
                    i_real = int(i / 3)
                    dma_type = DmaType.WALL
                    if i_real >= 0x200:
                        dma_type = DmaType.FLOOR
                    elif i_real >= 0x100:
                        dma_type = DmaType.WATER
                    mappings.append(RestTileMappingEntry(dma_type, i_real, variation))
                else:
                    # Special
                    typ = i % 3
                    i_real = int(i / 3) - 0x300
                    mappings.append(RestTileMappingEntry(DmaExtraType(typ), 0, i_real))

        more_width = TILESHEET_WIDTH * 3 * TW
        more_height = max(1, ceil(len(tiles_to_draw_on_more) / more_width) * TW)
        self.rest = Image.new('P', (more_width, more_height))
        for i, tile_more in enumerate(tiles_to_draw_on_more):
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
