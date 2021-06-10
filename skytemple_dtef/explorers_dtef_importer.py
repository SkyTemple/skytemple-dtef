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
import re

from math import floor
from typing import List, Dict, Optional, Set, Tuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from PIL import Image

from skytemple_dtef.dungeon_xml import DUNGEON_TILESET, DIMENSIONS, \
    ANIMATION, ANIMATION__PALETTE, ANIMATION__DURATION, ADDITIONAL_TILES, COLOR, FRAME, TILE, TILE__X, TILE__Y, \
    TILE__FILE, MAPPING, SPECIAL_MAPPING, MAPPING__TYPE, MAPPING__TYPE__FLOOR, MAPPING__TYPE__WALL, \
    MAPPING__TYPE__SECONDARY, MAPPING__nw, MAPPING__n, MAPPING__ne, MAPPING__e, MAPPING__se, MAPPING__s, MAPPING__sw, \
    MAPPING__w, MAPPING__VARIATION, SPECIAL_MAPPING__IDENTIFIER
from skytemple_dtef.explorers_dtef import TILESHEET_WIDTH, TILESHEET_HEIGHT
from skytemple_dtef.rules import get_rule_variations, REMAP_RULES
from skytemple_files.common.i18n_util import _, f
from skytemple_files.common.xml_util import validate_xml_attribs, validate_xml_tag
from skytemple_files.graphics.dma.model import Dma, DmaType, DmaExtraType, DmaNeighbor
from skytemple_files.graphics.dpc.model import Dpc, DPC_TILING_DIM
from skytemple_files.graphics.dpci.model import Dpci, DPCI_TILE_DIM
from skytemple_files.graphics.dpl.model import Dpl
from skytemple_files.graphics.dpla.model import Dpla


CHUNK_DIM = DPC_TILING_DIM * DPCI_TILE_DIM
PATTERN_FLOOR1 = re.compile(r"EOS_EXTRA_FLOOR1_(\d+)")
PATTERN_FLOOR2 = re.compile(r"EOS_EXTRA_FLOOR2_(\d+)")
PATTERN_WALL_OR_VOID = re.compile(r"EOS_EXTRA_WALL_OR_VOID_(\d+)")
EMPTY_IMAGE = [0 for _ in range(CHUNK_DIM ** 2)]
FULL = DmaNeighbor.NORTH_WEST | DmaNeighbor.NORTH | DmaNeighbor.NORTH_EAST | DmaNeighbor.WEST | DmaNeighbor.EAST | DmaNeighbor.SOUTH_WEST | DmaNeighbor.SOUTH | DmaNeighbor.SOUTH_EAST


class ExplorersDtefImporter:
    def __init__(self, dma: Dma, dpc: Dpc, dpci: Dpci, dpl: Dpl, dpla: Dpla):
        self.dma = dma
        self.dpc = dpc
        self.dpci = dpci
        self.dpl = dpl
        self.dpla = dpla

        self._dirname = None
        self._tileset_file_map: Dict[str, Image.Image] = {}
        self._tileset_chunk_map: Dict[str, Dict[Tuple[int, int], int]] = {}
        self._xml: Optional[Element] = None

        # The individual
        self._chunks: List[Image.Image] = [Image.new('P', (CHUNK_DIM, CHUNK_DIM))]
        self._palette: Optional[bytes] = None
        self._dpla__colors: List[List[int]] = []
        self._dpla__durations_per_frame_for_colors: List[int] = []
        self._dma__original_chunk_mappings = dma.chunk_mappings
        self.dma.chunk_mappings = [0 for _ in range(0, len(dma.chunk_mappings))]

    def do_import(self, dirname: str, fn_xml: str, fn_var0: str, fn_var1: str, fn_var2: str):
        try:
            self.__init__(self.dma, self.dpc, self.dpci, self.dpl, self.dpla)  # reset

            self._dirname = dirname
            self._assert_file_exists(fn_xml)
            self._open_tileset(fn_var0)
            self._open_tileset(fn_var1)
            self._open_tileset(fn_var2)
            self._xml = ElementTree.parse(fn_xml).getroot()
            validate_xml_tag(self._xml, DUNGEON_TILESET)
            validate_xml_attribs(self._xml, [DIMENSIONS])
            if int(self._xml.attrib[DIMENSIONS]) != CHUNK_DIM:
                # noinspection PyUnusedLocal
                dim = self._xml.attrib[DIMENSIONS]
                raise ValueError(f(_("Invalid tileset. Tileset has chunk dimensions of {dim}px, "
                                     "but only {CHUNK_DIM}px are supported.")))

            var_map = get_rule_variations(REMAP_RULES)
            ts = [os.path.basename(fn_var0), os.path.basename(fn_var1), os.path.basename(fn_var2)]
            for i, fn in enumerate(ts):
                self._import_tileset(fn, var_map, DmaType.WALL, 0, 0, TILESHEET_WIDTH, TILESHEET_HEIGHT, i, ts[i-1] if i > 0 else None)
                self._import_tileset(fn, var_map, DmaType.WATER, TILESHEET_WIDTH, 0, TILESHEET_WIDTH, TILESHEET_HEIGHT, i, ts[i-1] if i > 0 else None)
                self._import_tileset(fn, var_map, DmaType.FLOOR, TILESHEET_WIDTH * 2, 0, TILESHEET_WIDTH, TILESHEET_HEIGHT, i, ts[i-1] if i > 0 else None)

            ani0 = [[] for __ in range(0, 16)]
            ani1 = [[] for __ in range(0, 16)]
            dur0 = [6 for __ in range(0, 16)]
            dur1 = [6 for __ in range(0, 16)]
            for child in self._xml:
                if child.tag == ANIMATION:
                    validate_xml_attribs(child, [ANIMATION__PALETTE])
                    if child.attrib[ANIMATION__PALETTE] == "10":
                        if len(child) > 0:
                            ani0, dur0 = self._prepare_import_animation(child)
                    elif child.attrib[ANIMATION__PALETTE] == "11":
                        if len(child) > 0:
                            ani1, dur1 = self._prepare_import_animation(child)
                    else:
                        raise ValueError(_("Invalid animation: Animation is only supported for palettes 10 and 11."))
                if child.tag == ADDITIONAL_TILES:
                    self._import_additional_tiles(child, dirname)
            self._import_animation(ani0, ani1, dur0, dur1)

            self._finalize()
        except BaseException:
            # Reset DMA
            self.dma.chunk_mappings = self._dma__original_chunk_mappings
            raise

    @staticmethod
    def _assert_file_exists(fn):
        if not os.path.exists(fn):
            raise ValueError(f(_("A required DTEF file is missing: {fn}. Please verify the DTEF package.")))

    def _open_tileset(self, fn):
        self._assert_file_exists(fn)
        basename = os.path.basename(fn)
        pil = self._tileset_file_map[basename] = Image.open(fn)
        self._tileset_chunk_map[basename] = {}
        if pil.mode != 'P':
            raise ValueError(f(_('Can not import image "{basename}" as dungeon tileset: '
                                 'Must be indexed image (=using a palette)')))
        if pil.palette.mode != 'RGB' or len(pil.palette.palette) != 256 * 3:
            raise ValueError(f(_('Can not import image "{basename}" as dungeon tileset: '
                                 'Palette must contain  256 RGB colors.')))
        if self._palette is None:
            self._palette = bytes(pil.palette.palette)
        if pil.palette.palette != self._palette:
            raise ValueError(f(_('Can not import images as dungeon tilesets: '
                                 'The palettes of the images do not match. First image read that didn\'t match: '
                                 '"{basename}"')))

    def _import_tileset(self, fn: str, rule_map: Dict[int, Set[int]], typ: DmaType, bx, by, w, h, var_id, prev_fn: str):
        assert fn in self._tileset_file_map, f(_("Logic error: Tileset file {fn} was not loaded."))
        assert fn in self._tileset_chunk_map, f(_("Logic error: Tileset file {fn} was not loaded."))
        tileset = self._tileset_file_map[fn]
        if tileset.height < by + h or tileset.width < bx + w:
            raise ValueError(f(_("Image '{fn}' is too small ({tileset.width}x{tileset.height}px), must be at least "
                                 "{bx+w}x{by+h}px.")))

        # We need to import the full wall tile first
        if typ == DmaType.WALL and var_id == 0:
            assert FULL in rule_map, _("A rule is missing in the import set")
            i = list(rule_map.keys()).index(FULL)
            x = bx + (i % w)
            y = by + floor(i / w)
            cropped = tileset.crop(
                (x * CHUNK_DIM, y * CHUNK_DIM, (x + 1) * CHUNK_DIM, (y + 1) * CHUNK_DIM)
            )
            chunk_index = self._insert_chunk_or_reuse(cropped)
            self._tileset_chunk_map[fn][(x, y)] = chunk_index
            # We don't need to assign the DMA index, we will do this below.

        for i, rules in enumerate(rule_map.values()):
            x = bx + (i % w)
            y = by + floor(i / w)
            cropped = tileset.crop(
                (x * CHUNK_DIM, y * CHUNK_DIM, (x + 1) * CHUNK_DIM, (y + 1) * CHUNK_DIM)
            )
            if var_id > 0 and list(cropped.getdata()) == EMPTY_IMAGE:
                # Empty tile in variation, use previous variation.
                chunk_index = self._tileset_chunk_map[prev_fn][(x, y)]
            else:
                chunk_index = self._insert_chunk_or_reuse(cropped)
            self._tileset_chunk_map[fn][(x, y)] = chunk_index
            for rule in rules:
                self.dma.set(typ, rule, var_id, chunk_index)

    def _insert_chunk_or_reuse(self, new_chunk):
        for i, chunk in enumerate(self._chunks):
            if chunk.getdata() == new_chunk.getdata():
                return i

        self._chunks.append(new_chunk)
        return len(self._chunks) - 1

    def _import_additional_tiles(self, xml: Element, dirname):
        for tile in xml:
            validate_xml_tag(tile, TILE)
            validate_xml_attribs(tile, [TILE__X, TILE__Y, TILE__FILE])
            chunk = self._read_additional_chunk_idx(tile.attrib[TILE__FILE],
                                                    int(tile.attrib[TILE__X]),
                                                    int(tile.attrib[TILE__Y]),
                                                    dirname)
            for mapping in tile:
                if mapping.tag == MAPPING:
                    validate_xml_attribs(mapping, [
                        MAPPING__TYPE, MAPPING__nw, MAPPING__n, MAPPING__ne, MAPPING__e,
                        MAPPING__se, MAPPING__s, MAPPING__sw, MAPPING__w, MAPPING__VARIATION
                    ])
                    n = 0
                    if bool(int(mapping.attrib[MAPPING__nw])):
                        n |= DmaNeighbor.NORTH_WEST
                    if bool(int(mapping.attrib[MAPPING__n])):
                        n |= DmaNeighbor.NORTH
                    if bool(int(mapping.attrib[MAPPING__ne])):
                        n |= DmaNeighbor.NORTH_EAST
                    if bool(int(mapping.attrib[MAPPING__e])):
                        n |= DmaNeighbor.EAST
                    if bool(int(mapping.attrib[MAPPING__se])):
                        n |= DmaNeighbor.SOUTH_EAST
                    if bool(int(mapping.attrib[MAPPING__s])):
                        n |= DmaNeighbor.SOUTH
                    if bool(int(mapping.attrib[MAPPING__sw])):
                        n |= DmaNeighbor.SOUTH_WEST
                    if bool(int(mapping.attrib[MAPPING__w])):
                        n |= DmaNeighbor.WEST

                    if mapping.attrib[MAPPING__TYPE] == MAPPING__TYPE__FLOOR:
                        typ = DmaType.FLOOR
                    elif mapping.attrib[MAPPING__TYPE] == MAPPING__TYPE__WALL:
                        typ = DmaType.WALL
                    elif mapping.attrib[MAPPING__TYPE] == MAPPING__TYPE__SECONDARY:
                        typ = DmaType.WATER
                    else:
                        # noinspection PyUnusedLocal
                        mapping_type = mapping.attrib[MAPPING__TYPE]
                        raise ValueError(f(_("Error when importing mapping. Unknown type: "
                                             "'{mapping_type}'.")))
                    var_idx = int(mapping.attrib[MAPPING__VARIATION])
                    if var_idx < 0 or var_idx > 2:
                        raise ValueError(f(_("Invalid variation index {var_idx}.")))

                    self.dma.set(typ, n, var_idx, chunk)

                elif mapping.tag == SPECIAL_MAPPING:
                    validate_xml_attribs(mapping, [SPECIAL_MAPPING__IDENTIFIER])
                    m = PATTERN_FLOOR1.match(mapping.attrib[SPECIAL_MAPPING__IDENTIFIER])
                    if m:
                        self.dma.set_extra(DmaExtraType.FLOOR1, int(m.group(1)), chunk)
                    m = PATTERN_FLOOR2.match(mapping.attrib[SPECIAL_MAPPING__IDENTIFIER])
                    if m:
                        self.dma.set_extra(DmaExtraType.FLOOR2, int(m.group(1)), chunk)
                    m = PATTERN_WALL_OR_VOID.match(mapping.attrib[SPECIAL_MAPPING__IDENTIFIER])
                    if m:
                        self.dma.set_extra(DmaExtraType.WALL_OR_VOID, int(m.group(1)), chunk)

    def _read_additional_chunk_idx(self, fn, x, y, dirname):
        if fn not in self._tileset_file_map:
            self._open_tileset(os.path.join(dirname, fn))
            tileset = self._tileset_file_map[fn]
            for iy in range(0, tileset.height, CHUNK_DIM):
                for ix in range(0, tileset.width, CHUNK_DIM):
                    chunk_index = self._insert_chunk_or_reuse(tileset.crop((ix, iy, ix + CHUNK_DIM, iy + CHUNK_DIM)))
                    self._tileset_chunk_map[fn][(floor(ix / CHUNK_DIM), floor(iy / CHUNK_DIM))] = chunk_index
        return self._tileset_chunk_map[fn][(x, y)]

    def _merge_chunks(self):
        new_img = Image.new('P', (CHUNK_DIM * len(self._chunks), CHUNK_DIM))
        new_img.putpalette(self._chunks[1].getpalette())
        for i, chunk in enumerate(self._chunks):
            new_img.paste(chunk, (i * CHUNK_DIM, 0))
        return new_img

    def _prepare_import_animation(self, child):
        colors = [[] for __ in range(0, 16)]
        color_animations = []
        # If we have an old XML with duration on animation
        if ANIMATION__DURATION in child.attrib:
            color_animations = [int(child.attrib[ANIMATION__DURATION])] * 16
        for frame in child:
            validate_xml_tag(frame, FRAME)
            if len(frame) != 16:
                raise ValueError(_("Error in the XML: One of the animation frames doesn't have 16 colors. Each frame "
                                   "must have a value for each color."))
            for i, color in enumerate(frame):
                validate_xml_tag(color, COLOR)
                colors[i] += self._convert_hex_str_color_to_tuple(color.text)
                if ANIMATION__DURATION in color.attrib:
                    color_animations.append(int(color.attrib[ANIMATION__DURATION]))
        if len(color_animations) != 16:
            raise ValueError(_("Error in the XML: Durations for a palette or it's colors are not correctly defined."))
        return colors, color_animations

    def _import_animation(self, ani0, ani1, dur0, dur1):
        self._dpla__colors = ani0 + ani1
        self._dpla__durations_per_frame_for_colors = dur0 + dur1

    def _finalize(self):
        tiles, palettes = self.dpc.pil_to_chunks(self._merge_chunks())
        self.dpl.palettes = palettes
        self.dpci.tiles = tiles
        self.dpla.colors = self._dpla__colors
        self.dpla.durations_per_frame_for_colors = self._dpla__durations_per_frame_for_colors

    @staticmethod
    def _convert_hex_str_color_to_tuple(h: str) -> Tuple[int, ...]:
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
