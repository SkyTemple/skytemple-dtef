"""
Example script to export all dungeon tilesets from Explorers of Sky as "extended animations" DTEF for use in PMDO.
Mapping from https://docs.google.com/spreadsheets/d/1CBytuPKNaK-NITssa7TZdZNrK8NdOBx_0etyDckF6ZI/edit#gid=0
"""
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
import csv
import os
from io import StringIO
from xml.etree.ElementTree import Element, Comment

from ndspy.rom import NintendoDSRom

from skytemple_dtef.dungeon_xml import ANIMATION, ADDITIONAL_TILES
from skytemple_dtef.explorers_dtef import ExplorersDtef
from skytemple_dtef.transform import apply_extended_animations, xml_filter_tags
from skytemple_files.common.types.file_types import FileType
from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_files.common.xml_util import prettify


# PMDO ID,EoS ID,Name,Type
MAPPING = """PMDO ID,EoS ID,Name,Type
0,0,TestDungeon,wall
1,0,TestDungeon,ground
2,0,TestDungeon,water
3,78,TinyWoods,wall
4,78,TinyWoods,ground
5,78,TinyWoods,water
6,114,ThunderwaveCave,wall
7,114,ThunderwaveCave,ground
8,114,ThunderwaveCave,water
9,103,MtSteel1,wall
10,103,MtSteel1,ground
11,103,MtSteel1,water
12,104,MtSteel2,wall
13,104,MtSteel2,ground
14,104,MtSteel2,water
15,105,GrassMaze,wall
16,105,GrassMaze,ground
17,105,GrassMaze,water
18,116,UproarForest,wall
19,116,UproarForest,ground
20,116,UproarForest,water
21,71,ElectricMaze,wall
22,71,ElectricMaze,ground
23,71,ElectricMaze,water
24,96,WaterMaze,wall
25,96,WaterMaze,ground
26,96,WaterMaze,water
27,97,PoisonMaze,wall
28,97,PoisonMaze,ground
29,97,PoisonMaze,water
30,69,RockMaze,wall
31,69,RockMaze,ground
32,69,RockMaze,water
33,66,SilentChasm,wall
34,66,SilentChasm,ground
35,66,SilentChasm,water
36,106,MtThunder,wall
37,106,MtThunder,ground
38,106,MtThunder,water
39,107,MtThunderPeak,wall
40,107,MtThunderPeak,ground
41,107,MtThunderPeak,water
42,108,GreatCanyon,wall
43,108,GreatCanyon,ground
44,108,GreatCanyon,water
45,109,LapisCave,wall
46,109,LapisCave,ground
47,109,LapisCave,water
48,121,SouthernCavern2,wall
49,121,SouthernCavern2,ground
50,121,SouthernCavern2,water
51,122,WishCave2,wall
52,122,WishCave2,ground
53,122,WishCave2,water
54,102,RockPathRB,wall
55,102,RockPathRB,ground
56,102,RockPathRB,water
57,94,NorthernRange1,wall
58,94,NorthernRange1,ground
59,94,NorthernRange1,water
60,110,MtBlaze,wall
61,110,MtBlaze,ground
62,110,MtBlaze,water
63,88,SnowPath,wall
64,88,SnowPath,ground
65,88,SnowPath,water
66,100,FrostyForest,wall
67,100,FrostyForest,ground
68,100,FrostyForest,water
69,111,MtFreeze,wall
70,111,MtFreeze,ground
71,111,MtFreeze,water
72,79,IceMaze,wall
73,79,IceMaze,ground
74,79,IceMaze,water
75,123,MagmaCavern2,wall
76,123,MagmaCavern2,ground
77,123,MagmaCavern2,water
78,112,MagmaCavern3,wall
79,112,MagmaCavern3,ground
80,112,MagmaCavern3,water
81,125,HowlingForest2,wall
82,125,HowlingForest2,ground
83,125,HowlingForest2,water
84,99,SkyTower,wall
85,99,SkyTower,ground
86,99,SkyTower,water
87,77,DarknightRelic,wall
88,77,DarknightRelic,ground
89,77,DarknightRelic,water
90,85,DesertRegion,wall
91,85,DesertRegion,ground
92,85,DesertRegion,water
93,115,HowlingForest1,wall
94,115,HowlingForest1,ground
95,115,HowlingForest1,water
96,119,SouthernCavern1,wall
97,119,SouthernCavern1,ground
98,119,SouthernCavern1,water
99,74,WyvernHill,wall
100,74,WyvernHill,ground
101,74,WyvernHill,water
102,95,SolarCave1,wall
103,95,SolarCave1,ground
104,95,SolarCave1,water
105,80,WaterfallPond,wall
106,80,WaterfallPond,ground
107,80,WaterfallPond,water
108,113,StormySea1,wall
109,113,StormySea1,ground
110,113,StormySea1,water
111,118,StormySea2,wall
112,118,StormySea2,ground
113,118,StormySea2,water
114,,SilverTrench3,wall
115,,SilverTrench3,ground
116,,SilverTrench3,water
117,89,BuriedRelic1,wall
118,89,BuriedRelic1,ground
119,89,BuriedRelic1,water
120,,BuriedRelic2,wall
121,,BuriedRelic2,ground
122,,BuriedRelic2,water
123,81,BuriedRelic3,wall
124,81,BuriedRelic3,ground
125,81,BuriedRelic3,water
126,93,LightningField,wall
127,93,LightningField,ground
128,93,LightningField,water
129,73,NorthwindField,wall
130,73,NorthwindField,ground
131,73,NorthwindField,water
132,83,MtFaraway2,wall
133,83,MtFaraway2,ground
134,83,MtFaraway2,water
135,82,MtFaraway4,wall
136,82,MtFaraway4,ground
137,82,MtFaraway4,water
138,98,NorthernRange2,wall
139,98,NorthernRange2,ground
140,98,NorthernRange2,water
141,70,PitfallValley1,wall
142,70,PitfallValley1,ground
143,70,PitfallValley1,water
144,76,JoyousTower,wall
145,76,JoyousTower,ground
146,76,JoyousTower,water
147,75,PurityForest2,wall
148,75,PurityForest2,ground
149,75,PurityForest2,water
150,117,PurityForest4,wall
151,117,PurityForest4,ground
152,117,PurityForest4,water
153,120,PurityForest6,wall
154,120,PurityForest6,ground
155,120,PurityForest6,water
156,124,PurityForest7,wall
157,124,PurityForest7,ground
158,124,PurityForest7,water
159,,PurityForest8,wall
160,,PurityForest8,ground
161,,PurityForest8,water
162,,PurityForest9,wall
163,,PurityForest9,ground
164,,PurityForest9,water
165,67,WishCave1,wall
166,67,WishCave1,ground
167,67,WishCave1,water
168,68,MurkyCave,wall
169,68,MurkyCave,ground
170,68,MurkyCave,water
171,91,WesternCave1,wall
172,91,WesternCave1,ground
173,91,WesternCave1,water
174,87,WesternCave2,wall
175,87,WesternCave2,ground
176,87,WesternCave2,water
177,92,MeteorCave,wall
178,92,MeteorCave,ground
179,92,MeteorCave,water
180,72,RescueTeamMaze,wall
181,72,RescueTeamMaze,ground
182,72,RescueTeamMaze,water
183,1,BeachCave,wall
184,1,BeachCave,ground
185,1,BeachCave,water
186,2,DrenchedBluff,wall
187,2,DrenchedBluff,ground
188,2,DrenchedBluff,water
189,3,MtBristle,wall
190,3,MtBristle,ground
191,3,MtBristle,water
192,4,WaterfallCave,wall
193,4,WaterfallCave,ground
194,4,WaterfallCave,water
195,5,AppleWoods,wall
196,5,AppleWoods,ground
197,5,AppleWoods,water
198,6,CraggyCoast,wall
199,6,CraggyCoast,ground
200,6,CraggyCoast,water
201,7,SidePath,wall
202,7,SidePath,ground
203,7,SidePath,water
204,8,MtHorn,wall
205,8,MtHorn,ground
206,8,MtHorn,water
207,9,RockPathTDS,wall
208,9,RockPathTDS,ground
209,9,RockPathTDS,water
210,10,FoggyForest,wall
211,10,FoggyForest,ground
212,10,FoggyForest,water
213,11,ForestPath,wall
214,11,ForestPath,ground
215,11,ForestPath,water
216,12,SteamCave,wall
217,12,SteamCave,ground
218,12,SteamCave,water
219,13,UnusedSteamCave,wall
220,13,UnusedSteamCave,ground
221,13,UnusedSteamCave,water
222,14,AmpPlains,wall
223,14,AmpPlains,ground
224,14,AmpPlains,water
225,15,FarAmpPlains,wall
226,15,FarAmpPlains,ground
227,15,FarAmpPlains,water
228,16,ZeroIsleSouth2,wall
229,16,ZeroIsleSouth2,ground
230,16,ZeroIsleSouth2,water
231,17,NorthernDesert1,wall
232,17,NorthernDesert1,ground
233,17,NorthernDesert1,water
234,18,NorthernDesert2,wall
235,18,NorthernDesert2,ground
236,18,NorthernDesert2,water
237,19,QuicksandCave,wall
238,19,QuicksandCave,ground
239,19,QuicksandCave,water
240,20,QuicksandPit,wall
241,20,QuicksandPit,ground
242,20,QuicksandPit,water
243,21,QuicksandUnused,wall
244,21,QuicksandUnused,ground
245,21,QuicksandUnused,water
246,22,CrystalCave1,wall
247,22,CrystalCave1,ground
248,22,CrystalCave1,water
249,23,CrystalCave2,wall
250,23,CrystalCave2,ground
251,23,CrystalCave2,water
252,24,CrystalCrossing,wall
253,24,CrystalCrossing,ground
254,24,CrystalCrossing,water
255,25,ZeroIsleSouth1,wall
256,25,ZeroIsleSouth1,ground
257,25,ZeroIsleSouth1,water
258,26,ChasmCave1,wall
259,26,ChasmCave1,ground
260,27,ChasmCave2,wall
261,27,ChasmCave2,ground
262,28,DarkHill1,wall
263,28,DarkHill1,ground
264,28,DarkHill1,water
265,29,DarkHill2,wall
266,29,DarkHill2,ground
267,29,DarkHill2,water
268,30,SealedRuin,wall
269,30,SealedRuin,ground
270,30,SealedRuin,water
271,31,DeepSealedRuin,wall
272,31,DeepSealedRuin,ground
273,31,DeepSealedRuin,water
274,32,SkyPeakSummitPass,wall
275,32,SkyPeakSummitPass,ground
276,32,SkyPeakSummitPass,water
277,33,DuskForest1,wall
278,33,DuskForest1,ground
279,33,DuskForest1,water
280,34,DuskForest2,wall
281,34,DuskForest2,ground
282,34,DuskForest2,water
283,35,DeepDuskForest1,wall
284,35,DeepDuskForest1,ground
285,35,DeepDuskForest1,water
286,36,DeepDuskForest2,wall
287,36,DeepDuskForest2,ground
288,36,DeepDuskForest2,water
289,37,TreeshroudForest1,wall
290,37,TreeshroudForest1,ground
291,37,TreeshroudForest1,water
292,38,TreeshroudForest2,wall
293,38,TreeshroudForest2,ground
294,38,TreeshroudForest2,water
295,39,BrineCave,wall
296,39,BrineCave,ground
297,39,BrineCave,water
298,40,LowerBrineCave,wall
299,40,LowerBrineCave,ground
300,40,LowerBrineCave,water
301,41,UnusedBrineCave,wall
302,41,UnusedBrineCave,ground
303,41,UnusedBrineCave,water
304,42,HiddenLand,wall
305,42,HiddenLand,ground
306,42,HiddenLand,water
307,43,HiddenHighland,wall
308,43,HiddenHighland,ground
309,43,HiddenHighland,water
310,44,SouthernJungle,wall
311,44,SouthernJungle,ground
312,44,SouthernJungle,water
313,45,TemporalTower,wall
314,45,TemporalTower,ground
315,45,TemporalTower,water
316,46,TemporalSpire,wall
317,46,TemporalSpire,ground
318,46,TemporalSpire,water
319,47,TemporalUnused,wall
320,47,TemporalUnused,ground
321,47,TemporalUnused,water
322,48,MystifyingForest,wall
323,48,MystifyingForest,ground
324,48,MystifyingForest,water
325,49,RockAegisCave,wall
326,49,RockAegisCave,ground
327,49,RockAegisCave,water
328,50,ConcealedRuins,wall
329,50,ConcealedRuins,ground
330,50,ConcealedRuins,water
331,51,SurroundedSea,wall
332,51,SurroundedSea,ground
333,51,SurroundedSea,water
334,52,MiracleSea,wall
335,52,MiracleSea,ground
336,52,MiracleSea,water
337,53,MtTravail,wall
338,53,MtTravail,ground
339,53,MtTravail,water
340,54,TheNightmare,wall
341,54,TheNightmare,ground
342,54,TheNightmare,water
343,55,SpacialRift1,wall
344,55,SpacialRift1,ground
345,55,SpacialRift1,water
346,56,SpacialRift2,wall
347,56,SpacialRift2,ground
348,56,SpacialRift2,water
349,57,DarkCrater,wall
350,57,DarkCrater,ground
351,57,DarkCrater,water
352,58,DeepDarkCrater,wall
353,58,DeepDarkCrater,ground
354,58,DeepDarkCrater,water
355,59,WorldAbyss2,wall
356,59,WorldAbyss2,ground
357,59,WorldAbyss2,water
358,60,GoldenChamber,wall
359,60,GoldenChamber,ground
360,60,GoldenChamber,water
361,61,MysteryJungle2,wall
362,61,MysteryJungle2,ground
363,61,MysteryJungle2,water
364,62,MysteryJungle1,wall
365,62,MysteryJungle1,ground
366,62,MysteryJungle1,water
367,63,ZeroIsleEast3,wall
368,63,ZeroIsleEast3,ground
369,63,ZeroIsleEast3,water
370,64,ZeroIsleEast4,wall
371,64,ZeroIsleEast4,ground
372,64,ZeroIsleEast4,water
373,65,TinyMeadow,wall
374,65,TinyMeadow,ground
375,65,TinyMeadow,water
376,84,FinalMaze2,wall
377,84,FinalMaze2,ground
378,84,FinalMaze2,water
379,86,UnusedWaterfallPond,wall
380,86,UnusedWaterfallPond,ground
381,86,UnusedWaterfallPond,water
382,90,LushPrairie,wall
383,90,LushPrairie,ground
384,90,LushPrairie,water
385,126,IceAegisCave,wall
386,126,IceAegisCave,ground
387,126,IceAegisCave,water
388,127,SteelAegisCave,wall
389,127,SteelAegisCave,ground
390,127,SteelAegisCave,water
391,128,MurkyForest,wall
392,128,MurkyForest,ground
393,128,MurkyForest,water
394,129,DeepBoulderQuarry,wall
395,129,DeepBoulderQuarry,ground
396,129,DeepBoulderQuarry,water
397,130,LimestoneCavern,wall
398,130,LimestoneCavern,ground
399,130,LimestoneCavern,water
400,131,DeepLimestoneCavern,wall
401,131,DeepLimestoneCavern,ground
402,131,DeepLimestoneCavern,water
403,132,BarrenValley,wall
404,132,BarrenValley,ground
405,132,BarrenValley,water
406,133,DarkWasteland,wall
407,133,DarkWasteland,ground
408,133,DarkWasteland,water
409,134,FutureTemporalTower,wall
410,134,FutureTemporalTower,ground
411,134,FutureTemporalTower,water
412,135,FutureTemporalSpire,wall
413,135,FutureTemporalSpire,ground
414,135,FutureTemporalSpire,water
415,136,SpacialCliffs,wall
416,136,SpacialCliffs,ground
417,136,SpacialCliffs,water
418,137,DarkIceMountain,wall
419,137,DarkIceMountain,ground
420,137,DarkIceMountain,water
421,138,DarkIceMountainPeak,wall
422,138,DarkIceMountainPeak,ground
423,138,DarkIceMountainPeak,water
424,139,IcicleForest,wall
425,139,IcicleForest,ground
426,139,IcicleForest,water
427,140,VastIceMountain,wall
428,140,VastIceMountain,ground
429,140,VastIceMountain,water
430,141,VastIceMountainPeak,wall
431,141,VastIceMountainPeak,ground
432,141,VastIceMountainPeak,water
433,142,4thStationPass,wall
434,142,4thStationPass,ground
435,142,4thStationPass,water
436,143,7thStationPass,wall
437,143,7thStationPass,ground
438,143,7thStationPass,water
439,,ForestArea,wall
440,,ForestArea,ground
441,,ForestArea,water
442,,HighCaveArea,wall
443,,HighCaveArea,ground
444,,HighCaveArea,water
445,,SkyRuinsArea,wall
446,,SkyRuinsArea,ground
447,,SkyRuinsArea,water
448,,CraggyPeak,wall
449,,CraggyPeak,ground
450,,CraggyPeak,water
451,,SkyRuins,wall
452,,SkyRuins,ground
453,,SkyRuins,water
454,101,BuriedRelic2Sky,wall
455,101,BuriedRelic2Sky,ground
456,101,BuriedRelic2Sky,water"""

output_dir_base = os.path.join(os.path.dirname(__file__), 'dbg_output_pmdo_full_ani')
base_dir = os.path.join(os.path.dirname(__file__), '..')

rom = NintendoDSRom.fromFile(os.path.join(base_dir, 'skyworkcopy_us.nds'))

dungeon_bin_bin = rom.getFileByName('DUNGEON/dungeon.bin')
static_data = get_ppmdu_config_for_rom(rom)
dungeon_bin = FileType.DUNGEON_BIN.deserialize(dungeon_bin_bin, static_data)

eos_dungeons = []
print("Reading dungeon data...")
idx = 0
for i, dma in enumerate(dungeon_bin):
    fn = dungeon_bin.get_filename(i)
    if fn.endswith('.dma'):
        dpl = dungeon_bin.get(fn.replace('.dma', '.dpl'))
        dpla = dungeon_bin.get(fn.replace('.dma', '.dpla'))
        dpci = dungeon_bin.get(fn.replace('.dma', '.dpci'))
        dpc = dungeon_bin.get(fn.replace('.dma', '.dpc'))
        print(fn)
        eos_dungeons.append(ExplorersDtef(dma, dpc, dpci, dpl, dpla))

print("Processing mapping and outputting...")
data = {}
reader = csv.DictReader(StringIO(MAPPING))
for row in reader:
    if row['EoS ID'] != '':
        eos_id = int(row['EoS ID'])
        if eos_id not in data:
            data[eos_id] = {}
            data[eos_id]['Name'] = row['Name']
            data[eos_id]['Types'] = {}
        data[eos_id]['Types'][row['Type']] = row['PMDO ID']

for dungeon_id, dungeon_spec in data.items():
    dtef = eos_dungeons[dungeon_id]
    print(dungeon_spec['Name'])
    name = dungeon_spec['Name']
    wall = dungeon_spec['Types']['wall']
    floor = dungeon_spec['Types']['ground']
    secondary = dungeon_spec['Types']['water'] if 'water' in dungeon_spec['Types'] else None

    output_dir = os.path.join(output_dir_base, name)
    os.makedirs(os.path.join(output_dir), exist_ok=True)

    xml = dtef.get_xml()
    pmdo = Element('RogueEssence')
    xwall = Element('Wall')
    xwall.text = str(wall)
    pmdo.append(xwall)
    xfloor = Element('Floor')
    xfloor.text = str(floor)
    pmdo.append(xfloor)
    if secondary is not None:
        xsecondary = Element('Secondary')
        xsecondary.text = str(secondary)
        pmdo.append(xsecondary)
    xml.append(pmdo)

    file_list = list(apply_extended_animations(xml, *dtef.get_tiles()))
    print(len(file_list))

    # Write XML
    xml = xml_filter_tags(xml, [ANIMATION, ADDITIONAL_TILES, Comment])
    with open(os.path.join(output_dir, 'tileset.dtef.xml'), 'w') as f:
        f.write(prettify(xml))

    # Write Tiles
    for file_name, file in file_list:
        file.save(os.path.join(output_dir, file_name))
    idx += 1
