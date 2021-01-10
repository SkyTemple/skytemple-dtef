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

from itertools import chain
from typing import Tuple, Iterable, List, Optional
from xml.etree.ElementTree import Element

from PIL import Image

from skytemple_dtef.dungeon_xml import ANIMATION, ANIMATION__PALETTE, ANIMATION__DURATION, DIMENSIONS
from skytemple_dtef.explorers_dtef import VAR0_FN, VAR1_FN, VAR2_FN, MORE_FN


def apply_extended_animations(
        xml: Element, var0: Image.Image, var1: Image.Image, var2: Image.Image, rest: Image.Image, reduce_durations=True
) -> Iterable[Tuple[str, Image.Image]]:
    """
    Generates images for each frame of palette animation, yields filenames and images for the frames.
    Since the animations can have different speeds, the total number of frames will be the LCM of the durations
    of both animated palettes. If reduce_durations is True, odd durations are reduced by one to be even to potentially
    get a lower LCM and thus a lower amount of frames.
    All input images MUST have mode 'P'.
    """
    #  0,       1,        2,               3,                     4
    #  palette, duration, frames,          current frame counter, time in current frame
    #  int,     int,      List[List[int]], int,                   int
    anim_specs: List[List[any]] = []
    for node in xml:
        if node.tag == ANIMATION and len(node) > 0:
            anim_specs.append([
                int(node.attrib[ANIMATION__PALETTE]), int(node.attrib[ANIMATION__DURATION]),
                _get_pal_anim_frames(node), 0, 0
            ])
    # we only need to reduce durations if we have more than 1 animation.
    if reduce_durations and len(anim_specs) > 0:
        for spec in anim_specs:
            spec[1] = spec[1] if spec[1] % 2 == 0 else spec[1] - 1
    if len(anim_specs) > 0:
        lowest_duration = min(duration for _, duration, __, ___, ____ in anim_specs)
        highest_duration = max(duration for _, duration, __, ___, ____ in anim_specs)
    tile_dim = int(xml.attrib[DIMENSIONS])

    for base_fn, base_img in ((VAR0_FN, var0), (VAR1_FN, var1), (VAR2_FN, var2), (MORE_FN, rest)):
        # reset frame counters
        for spec in anim_specs:
            spec[3] = 0
            spec[4] = 0
        fi = 0
        affected_chunks = _get_chunks_in_palettes(base_img, [spec[0] for spec in anim_specs], tile_dim)
        if len(affected_chunks) < 1:
            yield base_fn, base_img
            continue
        # while any animation not finished
        while any(spec[3] < len(spec[2]) for spec in anim_specs):
            if fi == 0:
                # for the first frame we actually need to modify the base image
                out_fn = base_fn
                image = base_img
            else:
                out_fn = f'{base_fn[:-4]}_frame{fi - 1}.{lowest_duration}.png'
                image = Image.new('P', base_img.size)
                image.putpalette(base_img.getpalette())
                # Copy chunks to animate to image
                for x, y in affected_chunks:
                    image.paste(base_img.crop(
                        (x * tile_dim, y * tile_dim, (x + 1) * tile_dim, (y + 1) * tile_dim)),
                        (x * tile_dim, y * tile_dim)
                    )
            for spec in anim_specs:
                if spec[4] == 0:
                    # Replace colors with palette frame colors
                    palettes = image.getpalette()
                    palettes[spec[0] * 3 * 16:(spec[0] + 1) * 3 * 16] = spec[2][spec[3] % len(spec[2])]
                    image.putpalette(palettes)
                    # Increment palette frame counter.
                    spec[3] += 1
                spec[4] += highest_duration
                # Increment palette time in frame.
                if spec[4] >= spec[1]:
                    spec[4] = 0
            yield out_fn, image
            fi += 1


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


def _get_pal_anim_frames(xml_ani: Element) -> List[List[int]]:
    frames = []
    for frame in xml_ani:
        colors = []
        for color in frame:
            colors.append(convert_hex_str_color_to_tuple(color.text))
        frames.append(list(chain.from_iterable(colors)))

    return frames


def _get_chunks_in_palettes(base_img, pals, tile_tim) -> List[Tuple[int, int]]:
    if len(pals) < 1:
        return []
    chunks = set()
    for y in range(0, int(base_img.height / tile_tim)):
        for x in range(0, int(base_img.width / tile_tim)):
            for ty in range(0, 3):
                for tx in range(0, 3):
                    if floor(base_img.getpixel(
                            (x * tile_tim + (tx * int(tile_tim / 3)), y * tile_tim + (ty * int(tile_tim / 3)))
                    ) / 16) in pals:
                        chunks.add((x, y))
    return list(chunks)


def apply_alpha_transparency(img: Image.Image) -> Image.Image:
    mask = Image.new('L', img.size, color=255)
    mask.putdata([0 if x % 16 == 0 else 255 for x in img.getdata()])
    img = img.convert('RGBA')
    img.putalpha(mask)

    return img
