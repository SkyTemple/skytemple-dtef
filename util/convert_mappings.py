"""This converts the mapping file into a list for re-mapping the tiles on the tilesheet."""
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
from PIL import Image


def dir_name(x, y):
    if x == 0 and y == 0:
        return 'DmaNeighbor.NORTH_WEST'
    if x == 1 and y == 0:
        return 'DmaNeighbor.NORTH'
    if x == 2 and y == 0:
        return 'DmaNeighbor.NORTH_EAST'
    if x == 0 and y == 1:
        return 'DmaNeighbor.WEST'
    if x == 2 and y == 1:
        return 'DmaNeighbor.EAST'
    if x == 0 and y == 2:
        return 'DmaNeighbor.SOUTH_WEST'
    if x == 1 and y == 2:
        return 'DmaNeighbor.SOUTH'
    if x == 2 and y == 2:
        return 'DmaNeighbor.SOUTH_EAST'


def read_tile(img, ty, tx):
    strs = []
    for y in range(0, 3):
        for x in range(0, 3):
            if x == 1 and y == 1:
                continue
            px = img[tx * 3 + x, ty * 3 + y]
            if px == (0, 128, 128):
                # blank
                # nothing to do
                continue
            elif px == (1, 1, 1):
                # wall
                strs.append(dir_name(x, y))
            else:
                # skip
                return None
    return strs

def main():
    img: Image.Image = Image.open('./47_mappings.png').convert('RGB')

    tile_w = int(img.width / 3)
    tile_h = int(img.height / 3)

    print(f"TILESHEET_WIDTH = {tile_w}")
    print(f"TILESHEET_HEIGHT = {tile_h}")
    print()

    print("REMAP_RULES = [")

    data = img.load()

    for ty in range(0, tile_h):
        for tx in range(0, tile_w):
            t = read_tile(data, ty, tx)
            if t is None:
                print(f"    None,")
            elif len(t) < 1:
                print(f"    0,")
            else:
                print(f"    {' | '.join(t)},")
    print("]")


if __name__ == '__main__':
    main()
