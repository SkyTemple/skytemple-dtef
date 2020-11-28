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
from typing import List, Union
from xml.etree.ElementTree import Element

from skytemple_files.graphics.dma.model import DmaType, DmaExtraType, DmaNeighbor
from skytemple_files.graphics.dpla.model import Dpla, chunks

DUNGEON_TILESET = "DungeonTileset"
DIMENSIONS = "dimensions"
ANIMATION = "Animation"
ANIMATION__PALETTE = "palette"
ANIMATION__DURATION = "duration"
FRAME = "Frame"
COLOR = "Color"
ADDITIONAL_TILES = "AdditionalTiles"
TILE = "Tile"
TILE__X = "x"
TILE__Y = "y"
TILE__FILE = "file"
MAPPING = "Mapping"
MAPPING__TYPE = "type"
MAPPING__TYPE__FLOOR = "floor"
MAPPING__TYPE__WALL = "wall"
MAPPING__TYPE__SECONDARY = "secondary"
MAPPING__nw = "nw"
MAPPING__n = "n"
MAPPING__ne = "ne"
MAPPING__e = "e"
MAPPING__se = "se"
MAPPING__s = "s"
MAPPING__sw = "sw"
MAPPING__w = "w"
MAPPING__VARIATION = "variation"
SPECIAL_MAPPING = "SpecialMapping"
SPECIAL_MAPPING__IDENTIFIER = "identifier"


class RestTileMappingEntry:
    def __init__(self, dmatype: Union[DmaType, DmaExtraType], neighbors: int, variation_or_index: int):
        self.dmatype = dmatype
        self.neighbors = neighbors
        self.variation_or_index = variation_or_index

    def get_element(self):
        if isinstance(self.dmatype, DmaExtraType):
            return Element(
                SPECIAL_MAPPING,
                {
                    SPECIAL_MAPPING__IDENTIFIER: self._get_special_identifier()
                }
            )
        return Element(
            MAPPING,
            {
                MAPPING__TYPE: self._get_mapping_type(),
                MAPPING__VARIATION: str(self.variation_or_index),
                MAPPING__nw: "1" if self.neighbors & DmaNeighbor.NORTH_WEST == DmaNeighbor.NORTH_WEST else "0",
                MAPPING__n: "1" if self.neighbors & DmaNeighbor.NORTH == DmaNeighbor.NORTH else "0",
                MAPPING__ne: "1" if self.neighbors & DmaNeighbor.NORTH_EAST == DmaNeighbor.NORTH_EAST else "0",
                MAPPING__e: "1" if self.neighbors & DmaNeighbor.EAST == DmaNeighbor.EAST else "0",
                MAPPING__se: "1" if self.neighbors & DmaNeighbor.SOUTH_EAST == DmaNeighbor.SOUTH_EAST else "0",
                MAPPING__s: "1" if self.neighbors & DmaNeighbor.SOUTH == DmaNeighbor.SOUTH else "0",
                MAPPING__sw: "1" if self.neighbors & DmaNeighbor.SOUTH_WEST == DmaNeighbor.SOUTH_WEST else "0",
                MAPPING__w: "1" if self.neighbors & DmaNeighbor.WEST == DmaNeighbor.WEST else "0"
            }
        )

    def _get_special_identifier(self):
        return f'EOS_EXTRA_{self.dmatype.name}_{self.variation_or_index}'

    def _get_mapping_type(self):
        if self.dmatype == DmaType.WALL:
            return MAPPING__TYPE__WALL
        if self.dmatype == DmaType.FLOOR:
            return MAPPING__TYPE__FLOOR
        return MAPPING__TYPE__SECONDARY


class RestTileMapping:
    def __init__(self, x: int, y: int, mappings: List[RestTileMappingEntry], file_name: str):
        self.x = x
        self.y = y
        self.mappings = mappings
        self.file_name = file_name


class DungeonXml:
    @classmethod
    def generate(cls, dpla: Dpla, dungeon_tile_dimensions: int, rest_tile_mappings: List[RestTileMapping]) -> Element:
        dungeon_tileset = Element(DUNGEON_TILESET, {DIMENSIONS: str(dungeon_tile_dimensions)})
        dungeon_tileset.append(cls._insert_palette_anim(dpla, 0))
        dungeon_tileset.append(cls._insert_palette_anim(dpla, 1))
        rest = Element(ADDITIONAL_TILES)
        for r in rest_tile_mappings:
            tile = Element(TILE, {TILE__FILE: r.file_name, TILE__X: str(r.x), TILE__Y: str(r.y)})
            for mapping in r.mappings:
                tile.append(mapping.get_element())
            rest.append(tile)
        dungeon_tileset.append(rest)
        return dungeon_tileset

    @classmethod
    def _insert_palette_anim(cls, dpla: Dpla, idx):
        animation = Element(ANIMATION, {
            ANIMATION__DURATION: str(dpla.get_duration_for_palette(idx)),
            ANIMATION__PALETTE: str(idx + 10)
        })
        if dpla.has_for_palette(idx):
            for fi in range(0, dpla.get_frame_count_for_palette(idx)):
                frame = Element(FRAME)
                for r, g, b in chunks(dpla.get_palette_for_frame(idx, fi), 3):
                    color = Element(COLOR)
                    color.text = f'{r:02x}{g:02x}{b:02x}'
                    frame.append(color)
                animation.append(frame)
        return animation
