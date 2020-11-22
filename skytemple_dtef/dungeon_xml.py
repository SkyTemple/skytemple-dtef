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
from xml.etree.ElementTree import Element

from skytemple_files.graphics.dpla.model import Dpla, chunks

DUNGEON_TILESET = "DungeonTileset"
ANIMATION = "Animation"
ANIMATION__PALETTE = "palette"
ANIMATION__DURATION = "duration"
FRAME = "Frame"
COLOR = "Color"


class DungeonXml:
    @classmethod
    def generate(cls, dpla: Dpla) -> Element:
        dungeon_tileset = Element(DUNGEON_TILESET)
        dungeon_tileset.append(cls._insert_palette_anim(dpla, 0))
        dungeon_tileset.append(cls._insert_palette_anim(dpla, 1))
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
