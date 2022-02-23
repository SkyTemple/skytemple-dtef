"""Example script to export all dungeon tilesets from Explorers of Sky as DTEF."""
#  Copyright 2020-2022 Capypara and the SkyTemple Contributors
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
import shutil

from ndspy.rom import NintendoDSRom

from skytemple_dtef import get_template_file
from skytemple_dtef.explorers_dtef import ExplorersDtef
from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_files.common.xml_util import prettify
from skytemple_files.container.dungeon_bin.handler import DungeonBinHandler
from skytemple_files.graphics.dma.protocol import DmaProtocol
from skytemple_files.graphics.dpc.protocol import DpcProtocol
from skytemple_files.graphics.dpci.protocol import DpciProtocol
from skytemple_files.graphics.dpl.protocol import DplProtocol
from skytemple_files.graphics.dpla.protocol import DplaProtocol

output_dir_base = os.path.join(os.path.dirname(__file__), 'dbg_output')
base_dir = os.path.join(os.path.dirname(__file__), '..')

rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy_us.nds'))

dungeon_bin_bin = rom.getFileByName('DUNGEON/dungeon.bin')
static_data = get_ppmdu_config_for_rom(rom)
dungeon_bin = DungeonBinHandler.deserialize(dungeon_bin_bin, static_data)

idx = 0
for i, dma in enumerate(dungeon_bin):
    fn = dungeon_bin.get_filename(i)
    if fn.endswith('.dma'):
        dpl: DplProtocol = dungeon_bin.get(fn.replace('.dma', '.dpl'))
        dpla: DplaProtocol = dungeon_bin.get(fn.replace('.dma', '.dpla'))
        dpci: DpciProtocol = dungeon_bin.get(fn.replace('.dma', '.dpci'))
        dpc: DpcProtocol = dungeon_bin.get(fn.replace('.dma', '.dpc'))
        print(fn)
        dtef = ExplorersDtef(dma, dpc, dpci, dpl, dpla)

        output_dir = os.path.join(output_dir_base, str(idx))
        os.makedirs(os.path.join(output_dir), exist_ok=True)

        # Write XML
        with open(os.path.join(output_dir, 'tileset.dtef.xml'), 'w') as f:
            f.write(prettify(dtef.get_xml()))
        # Write Tiles
        var0, var1, var2, rest = dtef.get_tiles()
        var0fn, var1fn, var2fn, restfn = dtef.get_filenames()
        var0.save(os.path.join(output_dir, var0fn))
        var1.save(os.path.join(output_dir, var1fn))
        var2.save(os.path.join(output_dir, var2fn))
        rest.save(os.path.join(output_dir, restfn))
        shutil.copy(get_template_file(), os.path.join(output_dir, 'template.png'))
        idx += 1
