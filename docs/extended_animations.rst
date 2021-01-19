DTEF Variant: Extended Animations
=================================
This is an extension of the DTEF format explained in the other two documents.
It allowes for image based animations.

Frame Files
-----------
Additionally to the base tileset PNGs, additional files with the pattern ``basename_frameX_Y.Z.png`` max exist, where Y
is the frame number (starting at 0) and Z the duration of frames to hold this animation frame. X is the layer number,
animation frames must be overlayed on the base image and each layer has it's own animation.

Conversion
----------
SkyTemple / EoS tilesets can be converted with the ``transform`` module.
