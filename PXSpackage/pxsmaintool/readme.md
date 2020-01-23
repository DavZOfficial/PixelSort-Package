How to use this tool:


Open this up in Visual Studio Code. Run the script without any arguments (i know, dumb of me), and then write your arguments in the format <absolute-directory-to-input-file> and then parameters seperated by the | character. 

For example:

E:/Images/something.png|-t 0.2|-c 20

This python file is based off of https://github.com/satyarth/pixelsort, so go check that out. It's way easier to sort images using this.
I just converted the file into a bunch of classes, and if i ever want to add more modification stuff (such as changing HSV values of the image as it's sorting) then i can add that later. 


Also """TRIED""" to mess around with making gifs, but it just takes way too long.

Dependencies:
- Pillow (or PIL, but use pillow unless you physically can't)
- argparse
- numpy
- scipy (not sure why)
