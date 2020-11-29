Dungeon Tile Exchange Format (DTEF)
===================================
A specification / standard for dungeon tilesets.
A dungeon tileset is a rule-based image tileset for use in rogue-like generated dungeons. A tileset contains
tiles for floor tiles, wall tiles and one extra set of tiles ("secondary", usually used for water or lava).
A rule encodes the type of the tile itself and which of the 8 adjacent tiles have the same type as it. This
leads to 256 rules per type. DTEF encodes a subset of these rules (47-rule subset) in easy to modify tileset
files. The additional 209 rules are automatically mapped to these 47 rules
(see ``skytemple_dtef.rules.get_rule_variations``). The 47 rules are defined in ``skytemple_dtef.rules.REMAP_RULES``.

General
-------
A DTEF package is a directory or archive with at least one file named "tileset.dtef.xml" (the "XML file")
and some PNG files that contain the tile image data. The package defines the tileset.

Inside the XML file is a "DungeonTileset" node on the root level. This node has one attribute dimensions,
which contains the dimensions of each tile in this tileset as an integer.

The "DungeonTileset" node can have additional sub-nodes as explained further in this document.

Tileset PNGs
------------
Each DTEF package *should* contain at least one file named "tileset_0.png". This file contains the tiles for each
of the 47-base rules and their derivations. The file is split into three parts horizontally, which contain the three
different tile types (walls, secondary, floor; in that order). Each section has the dimensions of 6x8 tiles and
encodes the rules from ``skytemple_dtef.rules.REMAP_RULES`` (which is visualized in the "template.png" file in this
directory, this file is further explained in "SkyTemple.rst").

If the file is missing, all 47 base rules are undefined and all tile mappings should be assigned in the XML instead.

Additionally there can be more "tileset_X.png" files, with X being an integer greater than 0. Those additional tileset
files have the same format and are used as variants of the tiles. A tile in those files can be empty to mark, that
a variation does not exist and instead the variation from the previous file should be used.

There can also be more PNG files with tiles which can be referenced in the "AdditionalTiles" node of the XML.

The PNG files can either be indexed PNG files with 16x16 color palettes, of which the first color of each palettes is
treated as transparent / empty or a full color RGBA image. Please note that animations (see "XML: Animation") are only
supported for indexed images. All images must either have the same palettes if indexed or all must be RGBA.

The package may contain additional files, which are not part of this standard (documentation, extensions, templates,
etc.)

XML: Animation
--------------
Palette based animation for the tilesets. This is only supported for indexed tilesets. A tileset can have between 0 and
16 "Animation" nodes, each represents the animation for a single palette.

A "Animation" node has the palette number in its "palette" attribute and the duration to hold a single palette / frame
in the amount of frames (assuming 60FPS).

"Animation" nodes have an arbitrary amount of "Frame" sub-nodes. If it has no sub-nodes, then no animation exists (same
as if the "Animation" node didn't exist).

Each "Frame" must contain exactly 16 "Color" sub nodes, each representing a color in the palette that is being animated.
The color is encoded as a hexadecimal (HTML-Style, without "#": "rrggbb", "ab12ef").

XML: AdditionalTiles
--------------------
Each XML file can have one or no "AdditionalTiles" sub-node. This section encodes additional tiles and/or mappings
which either override the 209 rules not part of the base 47-rule subset or application specific "special mappings".

The node contains an arbitrary amount of "Tiles" sub nodes.

Tiles
~~~~~
Defines which file contains the tile that is being mapped and at which coordinate (relative to the tile dimensions)
it is stored inside this file ("file", "x" and "y" attributes).

A "Tile" node can have an arbitrary amount of "Mapping" and/or "SpecialMapping" sub nodes.

Mapping
~~~~~~~
Defines a rule by defining the state of the 8 neighboring tiles, the type of the tile and which variation of the tile it
is.

+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| Attribute | Values               | Description                                                                                       |
+===========+======================+===================================================================================================+
| type      | wall/floor/secondary | Type of the tile.                                                                                 |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| variation | Integer >= 0         | Which variation of this tile this is for, 0 being the default, see above for how variations work. |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| nw        | 0/1                  | Whether the tile north-west of this tile has the same type as this tile.                          |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| n         | 0/1                  | Whether the tile north of this tile has the same type as this tile.                               |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| ne        | 0/1                  | Whether the tile north-east of this tile has the same type as this tile.                          |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| e         | 0/1                  | Whether the tile east of this tile has the same type as this tile.                                |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| se        | 0/1                  | Whether the tile south-east of this tile has the same type as this tile.                          |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| s         | 0/1                  | Whether the tile south of this tile has the same type as this tile.                               |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| sw        | 0/1                  | Whether the tile south-west of this tile has the same type as this tile.                          |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+
| w         | 0/1                  | Whether the tile west of this tile has the same type as this tile.                                |
+-----------+----------------------+---------------------------------------------------------------------------------------------------+

The mapping can be for any of the 256 possible rules.

SpecialMapping
~~~~~~~~~~~~~~
A special, application-specific, tile mapping that doesn't fit into the usual 256 rules and/or the three base types.
The only attribute is "identifier", which is an application specific identifier that describes this mapping.

XML: Custom Nodes
-----------------
The XML file may contain additional nodes for additional information for import/export for specific
games / tools / frameworks.
