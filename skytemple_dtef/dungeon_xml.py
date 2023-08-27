#  Copyright 2020-2023 Capypara and the SkyTemple Contributors
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
from typing import List, Union, Tuple, Literal
from xml.etree.ElementTree import Element, Comment

from skytemple_files.graphics.dma.protocol import DmaType, DmaExtraType, DmaNeighbor
from skytemple_files.graphics.dpla import DPLA_COLORS_PER_PALETTE
from skytemple_files.graphics.dpla.protocol import DplaProtocol, chunk

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
    def __init__(self, dmatype_name: Union[Literal["normal"], Literal["extra"]], dmatype_idx: int, neighbors: int, variation_or_index: int):
        self.dmatype_name = dmatype_name
        self.dmatype_idx = dmatype_idx
        self.neighbors = neighbors
        self.variation_or_index = variation_or_index

    def get_element(self):
        if self.dmatype_name == "extra":
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
        return f'EOS_EXTRA_{self._dma_type_extra_name()}_{self.variation_or_index}'

    def _get_mapping_type(self):
        if self.dmatype_idx == DmaType.WALL:
            return MAPPING__TYPE__WALL
        if self.dmatype_idx == DmaType.FLOOR:
            return MAPPING__TYPE__FLOOR
        return MAPPING__TYPE__SECONDARY

    def _dma_type_extra_name(self):
        if self.dmatype_idx == DmaExtraType.FLOOR1:
            return 'FLOOR1'
        if self.dmatype_idx == DmaExtraType.FLOOR2:
            return 'FLOOR2'
        return 'WALL_OR_VOID'


class RestTileMapping:
    def __init__(self, x: int, y: int, mappings: List[RestTileMappingEntry], file_name: str):
        self.x = x
        self.y = y
        self.mappings = mappings
        self.file_name = file_name


class DungeonXml:
    @classmethod
    def generate(cls, dpla: DplaProtocol, dungeon_tile_dimensions: int, rest_tile_mappings: List[RestTileMapping]) -> Element:
        dungeon_tileset = Element(DUNGEON_TILESET, {DIMENSIONS: str(dungeon_tile_dimensions)})
        dungeon_tileset.append(Comment(" Dungeon Tile Exchange Format (DTEF) - SkyTemple PMD Explorers of Sky Export.\n"
                                       "       This XML file contains additional metadata for the tileset.\n"
                                       "       The main tiles can be found in tileset_0.png, variations if it "
                                       "(if they exist) in tileset_1.png and tileset_2.png.\n       "
                                       "This XML file may define additional tile mappings, see below.\n       "
                                       "For more information, see the documentation at "
                                       "https://github.com/SkyTemple/skytemple-dtef/blob/main/docs/SkyTemple.rst "))
        dungeon_tileset.append(Comment(" Palette Animations.\n       "
                                       "The palettes 10 and 11 can be animated. How long a color will be held "
                                       "is controlled by the 'duration' attribute for the colors in the first frame.\n       "
                                       "Each 'Frame' is a list of the 16 colors for this frame as HTML-style color "
                                       "codes. "))
        dungeon_tileset.append(cls._insert_palette_anim(dpla, 0))
        dungeon_tileset.append(cls._insert_palette_anim(dpla, 1))
        dungeon_tileset.append(Comment(" Additional Tile Mappings.\n       "
                                       "The tileset_X.png files define the main 47 rules for dungeon tiles. In theory "
                                       "there can be way more however.\n       "
                                       "This is due to the way the rules work, there can actually be 256 "
                                       "different rules. Those 256 combinations are usually collapsed into the 47 rules."
                                       "\n       If however a tile rule that is not on the tileset PNGs was assigned "
                                       "a different tile, it is defined here.\n       \n       "
                                       "Each entry here defines a tile, which file it is from and at which coordinate"
                                       " it can be found in that file.\n       "
                                       "For the additional rule mappings, the following syntax is used:"
                                       '\n              <Mapping type="wall" variation="0" nw="0" n="1" ne="1" e="0" se="1" s="0" sw="1" w="1"/>'
                                       '\n       "type" can be "wall"/"floor"/"secondary" and variation a number from '
                                       '0-2. The rest define the rule as adjacencies (cardinal directions).'
                                       '\n       \n       '
                                       'In addition to these 256 rules, special additional mappings can be added.\n'
                                       '       Explorers of Sky has some special rules like these, which are listed '
                                       'here as well.\n       '
                                       'The following syntax is used for those:'
                                       '\n              <SpecialMapping identifier="EOS_EXTRA_WALL_OR_VOID_1"/>'
                                       '\n       (The purpose of these is unknown.) '))
        rest = Element(ADDITIONAL_TILES)
        for r in rest_tile_mappings:
            tile = Element(TILE, {TILE__FILE: r.file_name, TILE__X: str(r.x), TILE__Y: str(r.y)})
            for mapping in r.mappings:
                tile.append(mapping.get_element())
            rest.append(tile)
        dungeon_tileset.append(rest)
        return dungeon_tileset

    @classmethod
    def _insert_palette_anim(cls, dpla: DplaProtocol, idx):
        animation = Element(ANIMATION, {
            ANIMATION__PALETTE: str(idx + 10)
        })
        if dpla.has_for_palette(idx):
            for fi in range(0, dpla.get_frame_count_for_palette(idx)):
                frame = Element(FRAME)
                for ci, (r, g, b) in enumerate(chunk(dpla.get_palette_for_frame(idx, fi), 3)):
                    color = Element(COLOR)
                    if fi == 0:
                        color.attrib[ANIMATION__DURATION] = str(
                            dpla.durations_per_frame_for_colors[idx * DPLA_COLORS_PER_PALETTE + ci]
                        )
                    color.text = f'{r:02x}{g:02x}{b:02x}'
                    frame.append(color)
                animation.append(frame)
        return animation
