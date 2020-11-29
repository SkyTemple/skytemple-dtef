DTEF for SkyTemple / PMD Explorers of Sky
=========================================
*(This is a more specialized version of the information in the "format" document,
specific for Explorers of Sky / SkyTemple).
See "format.xml" for a more technical and generic description of this format.*

A specification / standard for dungeon tilesets.

General
-------
A DTEF package is a directory or archive with at least one file named "tileset.dtef.xml" (the "XML file")
and some PNG files that contain the tile image data. The package defines the tileset.

Inside the XML file is a "DungeonTileset" node on the root level. This node has one attribute dimensions,
which contains the dimensions of each tile in this tileset. It must be "24" for Explorers of Sky.

The "DungeonTileset" node can have additional sub-nodes as explained further in this document.

Tileset PNGs
------------
Each DTEF package *should* contain at least one file named "tileset_0.png". This file contains the tiles for each
of the 47-base rules and their derivations. The file is split into three parts horizontally, which contain the three
different tile types (walls, secondary, floor; in that order). Each section has the dimensions of 6x8 tiles and
encodes the rules from the "template.png`_" file in this directory (see below).

Additionally there can be up to two more "tileset_X.png" files, with X being 1 and/or 2. Those additional tileset
files have the same format and are used as variants of the tiles. A tile in those files can be empty to mark, that
a variation does not exist and instead the variation from the previous file should be used.

There can also be more PNG files with tiles which can be referenced in the "AdditionalTiles" node of the XML.

The PNG files must be indexed PNG files with 16x16 color palettes, of which the first color of each palettes is
treated as transparent. All images must have the same palettes.

template.png
~~~~~~~~~~~~

.. _tileset.png: https://github.com/SkyTemple/skytemple-dtef/blob/main/docs/tileset.png

The "`template.png`_" is a visual aid for the 47 base dungeon tileset rules. The "tileset_X.png" files are structured
like it. Each 24x24 section represents a dungeon tile rule.
The white block in the middle marks the position of the tile that the rule applies to.

The tile has 8 adjacent neighbors. The neighbors are either marked blue or black. Black means that this neighbor
has the same type as the tile itself (so if the tile is a wall, this neighbor is also a tile). Blue means, that this
neighbor has a different type.

The fully red tile is not used.

XML: Animation
--------------
Palette based animation for the tilesets. A tileset can have "Animation" nodes, each represents the animation for a
single palette.

A "Animation" node has the palette number in its "palette" attribute and the duration to hold a single palette / frame
in the amount of frames (assuming 60FPS). Only animation for palette "10" and "11" are supported.

"Animation" nodes have an arbitrary amount of "Frame" sub-nodes. If it has no sub-nodes, then no animation exists (same
as if the "Animation" node didn't exist).

Each "Frame" must contain exactly 16 "Color" sub nodes, each representing a color in the palette that is being animated.
The color is encoded as a hexadecimal (HTML-Style, without "#": "rrggbb", "ab12ef").

XML: AdditionalTiles
--------------------
Each XML file can have one or no "AdditionalTiles" sub-node. This section encodes additional tiles and/or mappings
which either override the 209 rules not part of the base 47-rule subset or "special mappings".

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
A set of special rules as listed below (attribute "identifier", what these do is unknown:

EOS_EXTRA_FLOOR1_X, EOS_EXTRA_WALL_OR_VOID_X, EOS_EXTRA_FLOOR2_X (replace X with a number from 0 to 15).
