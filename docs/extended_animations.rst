DTEF Variant: Extended Animations
=================================
This is an extension of the DTEF format explained in the other two documents.
It allowes for image based animations.

Frame Files
-----------
Additionally to the base tileset PNGs, additional files with the pattern ``basename_frameX.Y.png`` max exist, where X
is the frame number (starting at 0) and Y the duration of frames to hold this animation frame.

Conversion
----------
SkyTemple / EoS tilesets can be converted with the ``transform`` module.
