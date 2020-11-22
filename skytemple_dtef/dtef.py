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

"""
TODO

Parakoopaheute um 22:54 Uhr
So what I'm thinking is maybe this is a better idea even though importing this (in SkyTemple!) will be a nightmare:
- Export one XML file as currently planned
- Export three sheets like the second one I posted above, one for each variation. If in sheet 2 or 3 a tile is empty, variation 0 is used instead.
- No mappings file anymore.
And then keep the 47 tile logic and only write a new importer for that

Audinoheute um 23:14 Uhr
Youre keeping the variations in this spec right?
Parakoopaheute um 23:15 Uhr
Yeah I'd still built it so that all additional tiles will just be added to the bottom. And might as well have a mapping for those in the XML file
so if you have more than the 47 combinations you could still work with them if you want and you can also work with those extra ground tiles
Or actually
since I put the variations into three sheets, I'll make a separate one for all the extra ones
Even easier to work with if you don't need them
Audinoheute um 23:18 Uhr
Ah, so the variations will be in intuitive arrangements as well?
Parakoopaheute um 23:19 Uhr
yeah. For variation 0 it will be a full sheet with no empty tiles. Tile mappings that use the same graphics will just have the same exact graphics in there (the importing code would need to spot the identical ones... or not)
For variation 1 and 2 it's the exact same structure, but tiles can be empty. If so that variation is not used (in EoS for the mapping variation 0 will be used, for PMDO I'm not sure how this works currently)
and then there's a fourth sheet with everything left over
and that has a mapping in the XML file
So when editing them you can just open each of the variations as a separate layer. Might as well also allow alpha for empty ones to make it even easier to overlay
kinda like the SpriteBot stuff works in that regard

"""

from math import floor
from typing import Optional, List, Union, Tuple
from xml.etree import ElementTree

from PIL import Image

from skytemple_dtef.dungeon_xml import DungeonXml
from skytemple_files.common.tiled_image import TilemapEntry
from skytemple_files.common.types.file_types import FileType
from skytemple_files.graphics.dma.model import Dma, DmaNeighbor, DmaType, DmaExtraType
from skytemple_files.graphics.dpc.model import Dpc
from skytemple_files.graphics.dpci.model import Dpci
from skytemple_files.graphics.dpl.model import Dpl
from skytemple_files.graphics.dpla.model import Dpla


TILESHEET_WIDTH = 6
TILESHEET_HEIGHT = 8

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
        # TODO: Todo?
        self.dma, self.dpc = self._remap_tileset(dma, dpc)
        self.dpci = dpci
        self.dpl = dpl
        self.dpla = dpla

    def get_xml(self) -> ElementTree.Element:
        return DungeonXml.generate(self.dpla)

    def get_mappings(self) -> bytes:
        return FileType.DMA.serialize(self.dma)

    def get_tiles_img(self) -> Image.Image:
        # TODO: Todo.
        return self.dpc.chunks_to_pil(self.dpci, self.dpl.palettes, TILESHEET_WIDTH * 3)

    def _remap_tileset(self, dma: Dma, dpc: Dpc):
        new_chunks = [self._generate_empty_chunk()] * TILESHEET_WIDTH * 3 * TILESHEET_HEIGHT
        new_dma = Dma(bytes())
        new_dma.chunk_mappings = [0 for _ in range(0, len(dma.chunk_mappings))]  # todo -1

        # main DMA entries - 0 variation - walls
        self._insert_and_remap(new_chunks, new_dma, dma, dpc, DmaType.WALL, [(0, REMAP_RULES)], 0, 0, TILESHEET_WIDTH)
        # main DMA entries - 0 variation - water
        self._insert_and_remap(new_chunks, new_dma, dma, dpc, DmaType.WATER, [(0, REMAP_RULES)], TILESHEET_WIDTH, 0, TILESHEET_WIDTH)
        # main DMA entries - 0 variation - ground
        self._insert_and_remap(new_chunks, new_dma,  dma, dpc, DmaType.FLOOR, [(0, REMAP_RULES)], TILESHEET_WIDTH * 2, 0, TILESHEET_WIDTH)

        rest = [x for x in range(0, 256) if x not in REMAP_RULES]
        rest_mappings = [
            #(1, REMAP_RULES),
            #(2, REMAP_RULES),
            (0, rest),
            #(1, rest),
            #(2, rest),
        ]

        # main DMA entries, other variations, all rest DMA combinations and extra
        self._insert_and_remap(new_chunks, new_dma, dma, dpc, None, rest_mappings, 0, TILESHEET_HEIGHT, TILESHEET_WIDTH * 3, extra=True, leave_gap=False)

        dpc.chunks = new_chunks
        assert not any(x == -1 for x in new_dma.chunk_mappings)
        return new_dma, dpc

    def _insert_and_remap(
            self, new_chunks: List[Optional[List[TilemapEntry]]], new_dma: Dma,
            dma: Dma, dpc: Dpc, rtype: Optional[DmaType], rules: List[Tuple[int, List[int]]],
            x: int, y: int, w: int, extra=False, leave_gap=True
    ):
        i = 0

        if rtype is None:
            types = [DmaType.WALL, DmaType.WATER, DmaType.FLOOR]
        else:
            types = [rtype]
        for the_type in types:
            for v_index, the_rules in rules:
                for rule in the_rules:
                    if rule is None:
                        # if we are at variation index 0, leave a gap, we are filling the main grid probably
                        if leave_gap:
                            i += 1
                        continue
                    old_chunk = dma.get(the_type, rule)[v_index]
                    if dpc.chunks[old_chunk] in new_chunks:
                        self._remap_existing(new_dma, new_chunks.index(dpc.chunks[old_chunk]), the_type, rule, v_index)
                        if leave_gap:
                            i += 1
                        continue
                    self._remap_single(
                        new_chunks, new_dma, dpc.chunks[old_chunk], the_type, rule, v_index, x, y, w, i
                    )
                    i += 1

        if extra:
            for extra_type in (DmaExtraType.FLOOR1, DmaExtraType.WALL_OR_VOID, DmaExtraType.FLOOR2):
                for idx, old_chunk in enumerate(dma.get_extra(extra_type)):
                    if dpc.chunks[old_chunk] in new_chunks:
                        self._remap_existing(new_dma, new_chunks.index(dpc.chunks[old_chunk]), extra_type, idx, 0)
                        continue
                    self._remap_single(
                        new_chunks, new_dma, dpc.chunks[old_chunk], extra_type, idx, 0, x, y, w, i
                    )
                    i += 1

    def _remap_single(
            self, new_chunks: List[List[TilemapEntry]], new_dma: Dma,
            chunk: List[TilemapEntry], the_type: Union[DmaType, DmaExtraType], rule: int,
            v_idx: int, bx: int, by: int, w: int, off: int):
        x = bx + (off % w)
        y = by + floor(off / w)
        i = y * TILESHEET_WIDTH * 3 + x
        #assert i <= 0xFF, "This dungeon tileset contains too many unique tiles to convert."
        self._enlarge(new_chunks, i)
        self._remap_existing(new_dma, i, the_type, rule, v_idx)
        new_chunks[i] = chunk

    def _remap_existing(
            self, new_dma: Dma, i: int, the_type: Union[DmaType, DmaExtraType], rule: int, v_idx: int
    ):
        if isinstance(the_type, DmaType):
            new_dma.set(the_type, rule, v_idx, i)
        else:
            new_dma.set_extra(the_type, rule, i)

    def _enlarge(self, lst, i):
        if len(lst) <= i:
            lst += [self._generate_empty_chunk()] * (i - len(lst) + 1)

    def _generate_empty_chunk(self):
        return [TilemapEntry(0, False, False, 0)] * 9
