# MyChip8Emulator
My try at a Chip-8 emulator, in Python with Pygame.

## How do I use it?

You need to have Python 3 installed (no prints are used, maybe it could work in Python 2 but I didn't try it and I don't know much of the differences between those 2 versions). You also need the Tkinter library to browse your files to choose a ROM (but I think it is installed by default) and Pygame for the rest of the UI (you can install it with PyPi).

You then just have to download CHIP8.py and beep.ogg in the same folder, run the script without any argument and it's done.

To interact with Chip-8, there are 16 available keys, in a square configuration. I mapped them as followed:

![Keyboard Layout](https://github.com/Tiwenty/MyChip8Emulator/raw/master/Chip8KeyLayout.png)

Note that with an AZERTY keyboard this layout will also work, due to the method I used from Pygame to treat the key events.

## What is Chip-8?

Chip-8 is an interpreted language, developed by Joseph Weisbecker. It was made to allow easier programming of video games for some type of computers.
Most of the popular games of this era had their Chip-8 version, be it Pong, Snake or Breakout.


## Why an emulator of Chip-8?

As I wanted to learn how do emulators work, and wanted to try my hand at one, Chip-8 is the go-to advice for beginners in this field. Even though it isn't a real machine such as a NES or a GB, it is like a simpler version of those. There are instructions to translate, registers and memory to manage, ROMs to load and a screen to display.

## What did you use to make this emulator?

I mainly used three documents, and a tutorial in French.

- [CHIP-8 - Wikipedia](https://en.wikipedia.org/wiki/CHIP-8) - Nice preview of what Chip-8 is.
- [Cowgod's Chip-8 Technical Reference](http://devernay.free.fr/hacks/chip8/C8TECH10.HTM) - Explains nicely and thoroughly how it works and how the opcodes are executed. But some of them are wrong and I used the next link to correct them.
- [mattmik : Mastering CHIP-8](http://mattmik.com/files/chip8/mastering/chip8.html) - Almost as complete as the previous link, and opcodes are considered working. At least those are the definitions I used.
- [Console emulation (FR)](https://openclassrooms.com/courses/l-emulation-console) - A French tutorial which helps you create a Chip-8 emulator in C with SDL, from the beginning. It helped me understand how it all works together.
