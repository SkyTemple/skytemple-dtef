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
from math import floor

from typing import Tuple, Iterable, List, Optional
from xml.etree.ElementTree import Element

from PIL import Image

from skytemple_dtef.dungeon_xml import ANIMATION, ANIMATION__PALETTE, ANIMATION__DURATION
from skytemple_dtef.explorers_dtef import VAR0_FN, VAR1_FN, VAR2_FN, MORE_FN


class ColorAnimInfo:
    def __init__(self, index: int, duration: int, frame_colors_hex: List[Tuple[int, int, int]]):
        self.index = index
        self.duration = duration
        self.frame_color_tuples = frame_colors_hex


def apply_extended_animations(
        xml: Element, var0: Image.Image, var1: Image.Image, var2: Image.Image, rest: Image.Image
) -> Iterable[Tuple[str, Image.Image]]:
    """
    Generates images for each frame of palette animation, yields filenames and images for the frames.
    Since the animations can have different speeds, the total number of frames will be the LCM of the durations
    of both animated palettes. If reduce_durations is True, odd durations are reduced by one to be even to potentially
    get a lower LCM and thus a lower amount of frames.
    All input images MUST have mode 'P'.
    """
    color_groups = _build_color_groups(xml)
    for base_fn, base_img in ((VAR0_FN, var0), (VAR1_FN, var1), (VAR2_FN, var2), (MORE_FN, rest)):
        # Apply first frame color to base image
        base_img = base_img.copy()
        palettes = base_img.getpalette()
        for color_group in color_groups:
            for color in color_group:
                palettes[color.index * 3:(color.index + 1) * 3] = color.frame_color_tuples[0]
        base_img.putpalette(palettes)
        yield base_fn, apply_alpha_transparency(base_img)
        cgi = 0
        for color_group in color_groups:
            layer_map = _get_pixels_with_indices(base_img, [c.index for c in color_group])
            if not any(layer_map):
                continue
            anything_was_replaced = False
            for fi in range(0, len(color_group[0].frame_color_tuples)):
                out_fn = f'{base_fn[:-4]}_frame{cgi}_{fi}.{color_group[0].duration}.png'
                image = base_img.copy()
                palettes = image.getpalette()
                something_was_replaced = False
                for color in color_group:
                    # We don't process this color if all color frames are the same as the original color
                    if all(c == tuple(palettes[color.index * 3:(color.index + 1) * 3]) for c in color.frame_color_tuples):
                        continue
                    anything_was_replaced = something_was_replaced = True
                    # Replace colors with color frame colors
                    palettes[color.index * 3:(color.index + 1) * 3] = color.frame_color_tuples[fi]
                if not something_was_replaced:
                    continue
                image.putpalette(palettes)
                mask = Image.new('L', base_img.size, color=255)
                mask.putdata([255 if m else 0 for m in layer_map])
                image = image.convert('RGBA')
                image.putalpha(mask)
                yield out_fn, image
            if anything_was_replaced:
                cgi += 1


def xml_filter_tags(xml: Element, tag_list) -> Element:
    new_nodes = []
    for node in xml:
        if node.tag not in tag_list:
            new_nodes.append(node)
    new_ele = Element(xml.tag, xml.attrib)
    for n in new_nodes:
        new_ele.append(n)
    return new_ele


def convert_hex_str_color_to_tuple(h: str) -> Optional[Tuple[int, int, int]]:
    if h is None:
        return None
    # noinspection PyTypeChecker
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _build_color_groups(xml: Element) -> List[List[ColorAnimInfo]]:
    colors_grouped = {}
    for node in xml:
        if node.tag == ANIMATION:
            ci_base = 16 * (int(node.attrib[ANIMATION__PALETTE]))
            colors_frame = None
            for frame in node:
                if colors_frame is None:
                    colors_frame = []
                    for ci, color in enumerate(frame):
                        duration = color.attrib[ANIMATION__DURATION]
                        c = ColorAnimInfo(ci_base + ci, duration, [])
                        colors_frame.append(c)
                        if (duration, len(node)) not in colors_grouped:
                            colors_grouped[(duration, len(node))] = []
                        colors_grouped[(duration, len(node))].append(c)
                for ci, color in enumerate(frame):
                    colors_frame[ci].frame_color_tuples.append(convert_hex_str_color_to_tuple(color.text))
    return list(colors_grouped.values())


def _get_pixels_with_indices(img, indices):
    pixels = img.load()
    m = []
    for j in range(img.size[1]):
        for i in range(img.size[0]):
            m.append(pixels[i, j] in indices)
    return m


def apply_alpha_transparency(img: Image.Image) -> Image.Image:
    mask = Image.new('L', img.size, color=255)
    mask.putdata([0 if x % 16 == 0 else 255 for x in img.getdata()])
    img = img.convert('RGBA')
    img.putalpha(mask)

    return img
