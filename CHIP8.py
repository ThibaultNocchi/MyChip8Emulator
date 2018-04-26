from random import randint
import pygame
from pygame.locals import *
from tkinter.filedialog import askopenfilename
from tkinter import *

def bitLen(value): 	# Gives the length of an unsigned value in bits
	length = 0
	while (value):
		value >>= 1
		length += 1
	return(length)

def getMSB(value, size): 	# Gets the MSB of an unsigned value in a size-bit format
	length = bitLen(value)
	if(length == size):
		return 1
	else:
		return 0

def getLSB(value): 	# Gets the LSB of a value
	return (value & 0x1)

class Screen: 	# Screen class to interact with the screen

	def __init__(self, Upscaling = 10):

		self.XSize = 64 	# Number of original pixels on the X axis
		self.YSize = 32 	# Number of original pixels on the Y axis

		self.SXSize = 0 	# Number of pixels for the screen on the X axis (stands for Screen X Size)
		self.SYSize = 0 	# Number of pixels for the screen on the Y axis (stands for Screen Y Size)

		self.XMargin = 200 	# Number of pixels of margin to the right of the game screen to display the debugger
		self.YMargin = 105 	# Number of pixels of maring on the bottom of the game screen to display the debugger

		self.upscaling = Upscaling 	# Upscaling ratio

		self.pixels = [] 	# Map of initial screen pixels
		self.clear() 		# Initialize the 2D list of pixels by clearing the screen

		self.white = (255, 255, 255) 	# Defining the white color
		self.black = (0, 0, 0) 			# Defining the black color

		self.regs = [0]*16 				# Store the register values to compare them against latest values
		self.regsPos = [(0,0)]*16 		# Store the positions of register values on screen
		self.regsSizes = [(0,0)]*16 	# Store the sizes of register values on screen

		self.vars = [("", 0)]*5 	# Store the different special registers to compare them against latest values
		self.vars[0] = ("DT",0) 	# Delay Timer
		self.vars[1] = ("ST",0) 	# Sound Timer
		self.vars[2] = ("I",0) 		# I register
		self.vars[3] = ("PC",0) 	# Program Counter
		self.vars[4] = ("SP",0) 	# Stack Pointer
		self.varsPos = [(0,0)]*5 	# Store the positions of those values on screen
		self.varsSizes = [(0,0)]*5 	# Store the sizes of thos values on screen

		self.mem = {} 		# Store the memory values displayed on screen, to compare them against latest values
		self.memPos = {} 	# Store the position of displayed memory values
		self.memSizes = {} 	# Store the size of displayed memory values
		self.memY = 0 		# Starting Y position for the memory debugger because commands are displayed above it
		self.PCPos = () 	# Store the position of the indicator showing the current memory adress

		self.pause = (0,0,0,0) 	# Store the position and size of the pause label

		pygame.init() 	# Initialize Pygame

		self.beep = pygame.mixer.Sound("beep.ogg") 							# Load the beep sample
		self.font = pygame.font.Font(pygame.font.get_default_font(), 14) 	# Load a font to display text for the debugger

	def __str__(self): 	# Used to debug the class by displaying each pixel value with its coordinates
		result = "" 															# String that will be returned
		for x in range(0, self.XSize): 											# For each X
			for y in range(0, self.YSize): 										# For each Y
				result += "({}, {}) = {}\n".format(x, y, self.pixels[x][y]) 	# We print the coordinates and the value of the X - Y pixel
		return result

	########################################################################################################

	def clear(self): 	# Clears the game screen by resetting the 2D list of pixels to 0

		# A 2D list representing the pixels of the game screen with a format of pixels[X][Y]
		self.pixels = [[0]*self.YSize for i in range(self.XSize)]

	########################################################################################################

	def startScreen(self): 	# Initialize the whold window with the game screen and provides upscaling because the window is resizable

		self.SXSize = (self.XSize * self.upscaling) + self.XMargin 	# Calculating the window size by upscaling the game screen and adding the X and Y margins
		self.SYSize = (self.YSize * self.upscaling) + self.YMargin

		self.window = pygame.display.set_mode((self.SXSize, self.SYSize), RESIZABLE) 	# Initialize the window with Pygame, enables resizing
		pygame.display.set_caption("Chip-8 Emulator by Tiwenty") 	# Caption

		# Draw 2 lines on the bottom and right of the game screen in white, to separate the game with the debugger
		# First point is bottom left of game screen
		# Second one is bottom right of game screen
		# Third one is top right of game screen
		pygame.draw.lines(self.window, self.white, False, [(0,self.YSize*self.upscaling), (self.XSize*self.upscaling, self.YSize*self.upscaling), (self.XSize*self.upscaling, 0)])
	
		self.memY = self.initCommands() 	# Display the available commands and retrieve at which Y position it ended (to display memory debugger under it)
		self.initRegsAndVars() 				# Initialize the labels of all registers (VX and special registers) under the game screen
		self.refreshScreen() 				# Refresh the window with all our new displayed magic


	########################################################################################################

	def destroyScreen(self): 	# Well it quits Pygame
		pygame.quit()

	########################################################################################################

	def resizeScreen(self, newX, newY): 	# Calculates new upscaling values when the window is resized, and resets it

		newX -= self.XMargin 						# Calculate X and Y available pixels for the game screen. We do it by taking the total new window size, and removing the necessary margins for the debugger
		newY -= self.YMargin
		XUpscale = newX // self.XSize 				# Calculate the upscaling we can provide for both the X and Y axis based of the available game screen with the new window
		YUpscale = newY // self.YSize
		self.upscaling = min(XUpscale, YUpscale) 	# Selecting the minimum of the X and Y upscaling in order to not increase the size of the new window
		self.startScreen() 							# Reset the screen with the new upscaling

	########################################################################################################

	def refreshScreen(self): 	# Refreshes the game screen

		for x in range(0, self.XSize): 			# For each X
			for y in range(0, self.YSize):		# For each Y
				if(self.pixels[x][y] == 0): 	# If the pixel is 0 (black)
					color = self.black 			# The color chosen will be our defined black color
				else:
					color = self.white 			# Or if the pixel is not 0 (so 1 or any unintended value which souldn't happen) we chose our defined white color

				# We draw our upscaled pixel, which is just a square with a length equals to our upscaling value starting with a position taking into account the upscaling
				# We are using the previously defined color based on our if
				pygame.draw.rect(self.window, color, (self.upscaling*x, self.upscaling*y, self.upscaling, self.upscaling))

		pygame.display.flip() 	# Updates the screen

	########################################################################################################

	def drawText(self, text, X, Y): # Draw a text at X and Y position, and returns the size it takes

		self.window.blit(self.font.render(text, True, self.white), (X, Y)) 	# Renders the text and adds it to the window
		return self.font.size(text) 										# Returns the text size

	########################################################################################################

	def togglePause(self, toggle): 	# Displays or remove the PAUSED label when the game is on pause

		if(self.pause[0] != 0): 	# If the X position of the label is not 0, it means we already drew it once and even if it isn't actually displayed, we erase it with a black rectangle
			pygame.draw.rect(self.window, self.black, (self.pause[0], self.pause[1], self.pause[2], self.pause[3])) 	# The black rectangle uses the X, Y position of the label and its size

		if toggle: 	# If we want to display the label

			text = "PAUSED" 							# Defining the text
			size = self.font.size(text) 				# Saving its size
			
			x = self.XSize * self.upscaling - size[0] 	# Calculating its position to be just under the bottom right corner of the game screen
			y = self.YSize * self.upscaling + 10
			
			size = self.drawText(text, x, y) 			# Displaying the text
			self.pause = (x, y, size[0], size[1]) 		# Saving its position and size in the object

	########################################################################################################

	def initRegsAndVars(self): 	# Displays the registers labels

		initialY = self.YSize*self.upscaling + 10 	# Calculate the initial Y value (right under the game screen)
		y = initialY 								# Saves the initial Y to the variable that will be used to move the drawing cursor
		x = 10 										# The cursor for the X axis
		xMargin = 50 								# Margin the X axis between labels

		maxX = 0 	# Maximum X size taken by labels on the row to have some sort of alignement and no label writing on each other

		for i in range(len(self.regs)): 	# For each index of V registers

			size = self.drawText("V{:X}=".format(i), x, y) 	# Display the label with its hexadecimal index at the current X and Y position
			maxX = max(maxX, size[0]) 						# Compare the X size to the maximum

			self.regsPos[i] = (x+size[0], y) 	# Gets the X and Y values where the register value will be displayed. The X value is the current position + the label size

			self.regsSizes[i] = self.drawText("#{:0=4X}".format(self.regs[i]), self.regsPos[i][0], self.regsPos[i][1]) 	# Display the current register value next to its label with the previoulsy calculated coordinates

			if(y + 2*size[1] < self.SYSize): 	# If the next register can still be displayed under our current one. We add twice our label height because we take into account the current one (our cursor is still above it), and the next one.
				y += size[1] 					# We then move our Y cursor under our current lable
			else: 								# The next register label can't be displayed under the current one
				x += maxX + xMargin 			# We move our X cursor to the right by our defined margin (which takes the register value size into account) and the max X size of our labels in the column
				maxX = 0 						# We reset the max X size because we are switching to another column
				y = initialY 					# We reset the Y cursor position

		y = initialY 			# Once we have displayed the V registers, we reset the Y cursor poisition because special registers will be displayed on another column
		x += maxX + 2*xMargin 	# We move our X cursor position by the standard margin but with some more in order to differentiate those two types of registers
		maxX = 0 				# We reset the max X size

		for idx in range(len(self.vars)): 	# For each special register

			size = self.drawText("{} = ".format(self.vars[idx][0]), x, y) 	# Display the label at the current X and Y position
			maxX = max(maxX, size[0]) 										# Compare the X size to the maximum

			self.varsPos[idx] = (x+size[0], y) 	# Gets the X and Y values where the register value will be displayed. The X value is the current position + the label size

			self.varsSizes[idx] = self.drawText("#{:0=4X}".format(self.vars[idx][1]), self.varsPos[idx][0], self.varsPos[idx][1]) 	# Display the current register value next to its label with the previoulsy calculated coordinates

			if(y + 2*size[1] < self.SYSize): 	# Same idea as the above if statement, we check if we can write another register under our current one, if not we move it to the next column
				y += size[1]
			else:
				x += maxX + 50
				maxX = 0
				y = initialY

	########################################################################################################

	def displayRegsAndVars(self, regs, DT, ST, I, PC, SP): 	# Displays the V and special registers
		
		for idx, val in enumerate(regs): 	# For each V register

			if(val != self.regs[idx]): 	# If the current CPU value is different than the one stored by the screen
				self.regs[idx] = val 	# We update the stored one
				pygame.draw.rect(self.window, self.black, (self.regsPos[idx][0], self.regsPos[idx][1], self.regsSizes[idx][0], self.regsSizes[idx][1])) 	# We erase the displayed value with a black rectangle using the previously saved size and position
				self.regsSizes[idx] = self.drawText("#{:0=4X}".format(self.regs[idx]), self.regsPos[idx][0], self.regsPos[idx][1]) 	# We redraw the text on the screen and save its new size

		otherVars = [DT, ST, I, PC, SP] 	# We list all needed special registers values to ease the process with a for loop

		for idx, val in enumerate(otherVars): 	# For each special register, we do the exact same thing as the above for statement

			if(val != self.vars[idx][1]):
				self.vars[idx] = (self.vars[idx][0], val)
				pygame.draw.rect(self.window, self.black, (self.varsPos[idx][0], self.varsPos[idx][1], self.varsSizes[idx][0], self.varsSizes[idx][1]))
				self.varsSizes[idx] = self.drawText("#{:0=4X}".format(self.vars[idx][1]), self.varsPos[idx][0], self.varsPos[idx][1])

	########################################################################################################

	def displayMemory(self, memory): 	# Displays the memory on the right of the game screen
		
		# As we can't display all the memory cells, we show a list containing the current memory adress. But if it isn't in the list anymore, we refresh the list starting with the current one

		replaceMemory = False 	# Boolean to check if we need to refresh the list
		pc = self.vars[3][1] 	# Gets the current PC value
		redSquare = 8 			# Size in pixels of the red square indicating the current memory adress

		try: 					# This try statement is used to check if the current PC adress is in the displayed memory adresses
			if(self.mem[pc]): 	# If it is already displayed, we do nothing and continue the function
				pass
		except KeyError: 		# If it isn't displayed, we will have to replace the memory displayed so we switch the boolean to True
			replaceMemory = True

		if replaceMemory: 	# If we need to refresh the displayed memory

			y = self.memY 							# We set the Y cursor at the available Y position given when initiating the window (because the memory list is displayed under the commands)
			x = self.XSize * self.upscaling + 20 	# Initial X cursor is set 20 pixels on the right of the game screen

			self.mem = {} 		# We reset the memory dictionnary storing the displayed memory adresses
			self.memPos = {} 	# We reset the positions dictionnary
			self.memSizes = {} 	# We reset the sizes dictionnary

			# Erase the whole memory panel
			# We start it at x-10 so we also erase the red indicator
			# The new black panel goes all the way to the right and bottom
			pygame.draw.rect(self.window, self.black, (x-10, y, self.SXSize - x + 1, self.SYSize - y + 1))

			for idx, val in enumerate(memory): 	# For each value in memory (even those not displayed)
				
				if idx < pc: 	# If the adress being checked is inferior to the current PC one we pass it because we want to start displaying at our current PC value
					continue

				if idx % 2 == 1: 	# If the adress being checked isn't an even number, we pass it because an adress stores an 8 bit value, and we are interested by displaying 16 bits for each one because the opcodes are in 16 bits
					continue

				opcode = (val << 8) + memory[idx+1] 						# Calculate the opcode value
				text = "PC: #{:0=4X} || Op: #{:0=4X}".format(idx, opcode) 	# Define the text to display the adress and associated opcode
				size = self.font.size(text) 								# Save the size of the to-be-displayed text

				if y + size[1] > self.SYSize: 	# If we have reached the bottom of the window we won't display any new memory adress, neither this one
					break

				if idx == pc: 																						# If the adress being checked is the current PC
					self.PCPos = (x-10, y+(size[1]-redSquare)/2) 													# Calculate the position of the red indicator
					pygame.draw.rect(self.window, (255,0,0), (self.PCPos[0], self.PCPos[1], redSquare, redSquare)) 	# Draw the red square on the left of the adress line

				self.mem[idx] = val 							# Save the value associated to the adress being checked
				self.memPos[idx] = (x, y) 						# Save the X and Y position of the text
				self.memSizes[idx] = self.drawText(text, x, y) 	# Draw the text and save its size

				self.mem[idx+1] = memory[idx+1] 	# Also save the next memory value because we are skipping odd memory adresses because they are not displayed and we still need it to compare against new values

				y += size[1] 	# Move the Y cursor under the newly displayed text

		else: 	# If we don't need to refresh the displayed memory values

			for idx, val in self.mem.items(): 	# For each displayed value

				if idx % 2 == 1: 	# If it is an odd memory adress we skip it
					continue

				if idx == pc: 	# If the adress being checked is the current PC

					pygame.draw.rect(self.window, self.black, (self.PCPos[0], self.PCPos[1], redSquare, redSquare)) 	# Erase the previous red indicator
					newPCy = self.memPos[idx][1]+(self.memSizes[idx][1]-redSquare)/2 									# Calculate the new Y position of the indicator
					self.PCPos = (self.PCPos[0], newPCy) 																# Save the new X and Y position of the indicator
					pygame.draw.rect(self.window, (255,0,0), (self.PCPos[0], self.PCPos[1], redSquare, redSquare)) 		# Draw the red square on the left of the adress line

				if self.mem[idx] != memory[idx] or self.mem[idx+1] != memory[idx+1]: 	# If the value of the adress being checked, or the next one (opcodes are 16 bits) changed, we refresh its value on screen

					self.mem[idx] = memory[idx] 						# Save current and next value
					self.mem[idx+1] = memory[idx+1]
					opcode = (self.mem[idx] << 8) + self.mem[idx+1] 	# Calculate opcode

					pos = self.memPos[idx] 	# Retrieve the position of current memory adress on the screen

					pygame.draw.rect(self.window, self.black, (pos[0], pos[1], self.memSizes[idx][0], self.memSizes[idx][1])) 	# Erase the currently displayed value

					text = "PC: #{:0=4X} || Op: #{:0=4X}".format(idx, opcode) 	# Create the displayed text

					self.memSizes[idx] = self.drawText(text, pos[0], pos[1]) 	# Draw the text and save its size

	########################################################################################################

	def initCommands(self): 	# Display the available commands
		
		initialX = self.XSize * self.upscaling + 10 	# Initial X is on the right of the game screen
		x = initialX 									# Sets the X cursor to the initial X value
		y = 10 											# Y cursor is on the top of the window

		y += self.drawText("ESC: Quit", x, y)[1] 			# We draw the commands text and move the Y cursor by the text's size
		y += self.drawText("F1: Change ROM", x, y)[1]
		y += self.drawText("F2: Reboot ROM", x, y)[1]
		y += self.drawText("F3: Pause / Unpause", x, y)[1]
		y += self.drawText("F4: Next step", x, y)[1]
		y += self.drawText("F5: Sound ON / OFF", x, y)[1]

		y += 10 																	# Move the cursor 10px downward
		pygame.draw.line(self.window, self.white, (x, y), (self.SXSize - 10, y)) 	# To draw a separation line between commands and memory which is under

		return y+10 	# Return the Y position 10px under our drawn line



############################################################################################################


class UnsignedBitsArray: 	# Class designed to be a list of cellsNbr values, which are cellLength bits unsigned integers.

	def __init__(self, cellLength, cellsNbr):

		self._cellLength = abs(cellLength) 	# Storing the absolute values of the length and number of bits, those can't be negative right?
		self._cellsNbr = abs(cellsNbr)
		self._arr = [0] * self._cellsNbr 	# Initialize the list of unsigned values

	def __str__(self): 	# Displays each cell with its index and value, in hexadecimal
		result = ""
		for idx, val in enumerate(self._arr):
			result += "{} : {}\n".format(hex(idx), hex(val))
		return result

	def __getitem__(self, idx): 	# Getting a value is straightforward, we do not treat it

		return self._arr[idx]

	def __setitem__(self, idx, value): 	# When setting a value it stays withing the boudaries of an unsigned cellLength bits integer. If it overflows we just truncate the Most Significant Bits to take the length down to cellLength. The modulo does it well.

		self._arr[idx] = value % (2**self._cellLength)

############################################################################################################

class CHIP8: 	# Chip 8 core of the emulator, with reading ROMs, decoding opcodes and executing them

	def __init__(self, romPath, Speed = 1024): 	# Speed in Hz

		
		self.speed = Speed 		# Speed of CPU in Hz
		self.romPath = romPath 	# Path to the ROM file
		self.changeRom = False 	# Boolean to put to True when the user wants to change the ROM. It allows the program to not end when unloading the current ROM

		self.initVars() 		# Initialize all the emulator variables which are resetted when changing a ROM, so we don't have to destroy our CHIP8 object when rebooting the current ROM

		self.started = False 	# Boolean to check if the game is launched
		self.paused = False 	# Boolean to pause the emulator
		self.nextStep = False 	# Boolean to allow the emulator to jump to the next step

		self.DELAYSOUNDTIMER = USEREVENT + 1 	# Pygame event for the 60Hz timers and the screen refreshing

		self.sound = True 		# Boolean to allow sound to be played

		self.screen = Screen() 	# Initialize the screen

	########################################################################################################

	# Those are properties used to manage the registers which have a maximum bit size and are unsigned
	# So no treatment is done when getting them
	# But when setting them we apply a modulo to keep the value in its boundaries

	@property
	def I(self):
		return self.__I

	@I.setter
	def I(self, value):
		self.__I = value % (2**16)

	@property
	def delay_timer(self):
		return self.__delay_timer

	@delay_timer.setter
	def delay_timer(self, value):
		self.__delay_timer = value % (2**8)

	@property
	def sound_timer(self):
		return self.__sound_timer

	@sound_timer.setter
	def sound_timer(self, value):
		self.__sound_timer = value % (2**8)

	@property
	def PC(self):
		return self.__PC

	@PC.setter
	def PC(self, value):
		self.__PC = value % (2**16)

	@property
	def SP(self):
		return self.__SP

	@SP.setter
	def SP(self, value):
		self.__SP = value % (2**8)

	########################################################################################################

	def initVars(self): 	# Initializes the variables used to run the emulator

		self.memory = UnsignedBitsArray(8, 4096) 	# Memory of 4096 * 8 bits
		self.V = UnsignedBitsArray(8, 16) 			# V[X] register. 16 * 8 bits
		self.I = 0 									# I register
		self.delay_timer = 0 						# Delay Timer. Should be decremented to 0 at a rate of 60Hz
		self.sound_timer = 0 						# Sound Timer. Should be decremented to 0 at a rate of 60Hz
		self.PC = 512 								# Program Counter. Starts at 0x200
		self.SP = 0 								# Stack Pointer
		self.stack = UnsignedBitsArray(16, 16) 		# Stack pile. 16 * 16 bits

		self.key = [False for i in range(16)] 		# List of pressed keys, max 16 keys

		self.loadFonts() 							# Load fonts in memory

	########################################################################################################

	def loadGame(self): 	# Loads the game from the ROM into memory

		i = 0x200 															# Default adress to store the program

		with open(self.romPath, "rb") as f: 								# Opening the ROM
			while 1: 														# While the universe is working
				byte = f.read(1) 											# We get a byte
				if not byte: 												# If it is empty we reached the EOF
					break													# Breaking out of the loop
				self.memory[i] = int.from_bytes(byte, "big", signed=False) 	# Storing into the memory at the i position the value of the byte we just read
				i += 1 														# Increasing the counter

	########################################################################################################

	def startGame(self): 	# Starts the game

		self.screen.startScreen() 	# Start the screen

		pygame.time.set_timer(self.DELAYSOUNDTIMER, round((1/60)*1000)) 	# Sets up the 60Hz timer

		self.started = True 	# Sets the started boolean to True

		while self.started: 	# While the emulator is started

			self.listen() 									# Checks all Pygame events on queue (timers, window resizing, quitting the program or most of all pressing keys)
			self.executeOpcode(self.getCurrentOpcode()) 	# Retrieve and execute the current opcode

			while self.paused and self.started: 	# If the game is on pause

				self.nextStep = False 	# We reset the boolean value
				self.listen() 			# We listen to the events (to not block the program if we want to quit or anything) but we are mainly waiting for the next step key to be pressed
				if self.nextStep: 		# If the next step key was pressed
					break 				# We break out of the paused loop so we can execute the next opcode. But as the game is paused, if will immediatly go back into this loop right after the next opcode, to wait for the next step
				pygame.time.delay(50) 	# Delay of 50ms, to avoid using too much useless CPU time (I guess we don't really care but hey 20Hz to wait for a key event for the next step or quitting is nice enough)

			pygame.time.delay(round((1/self.speed)*1000)) 	# Delay allowing us to execute opcodes at the specified speed

		self.screen.destroyScreen() 	# When out of the loop, we are quitting so we destroy the screen
		return self.changeRom 			# Returning to the main program whether to quit or not to quit

	########################################################################################################

	def rebootGame(self): 	# Reboots the game

		self.initVars() 	# Initialize variables
		self.screen.clear() # Clear the screen
		self.loadGame() 	# Reload the game into memory

	########################################################################################################

	def listen(self): 	# Goes through all Pygame events on queue

		for event in pygame.event.get(): 	# For each event in the queue

			if event.type == QUIT: 						# QUIT
				self.started = False 	# We stop the game
			
			elif event.type == self.DELAYSOUNDTIMER: 	# 60Hz timer
				self.timeout60Hz() 	# Function refreshing screen and managing Chip 8 timers

			elif event.type == VIDEORESIZE: 			# Resizing the screen
				self.screen.resizeScreen(event.w, event.h) 	# Function to resize the screen and reset it

			elif event.type == KEYDOWN: 				# Pressing a key
				
				# GAME KEYS
				# When a key is pressed, we set the associated value to 1
				if event.key == K_1:
					self.key[0x1] = 1
				elif event.key == K_2:
					self.key[0x2] = 1
				elif event.key == K_3:
					self.key[0x3] = 1
				elif event.key == K_4:
					self.key[0xC] = 1
				elif event.key == K_q:
					self.key[0x4] = 1
				elif event.key == K_w:
					self.key[0x5] = 1
				elif event.key == K_e:
					self.key[0x6] = 1
				elif event.key == K_r:
					self.key[0xD] = 1
				elif event.key == K_a:
					self.key[0x7] = 1
				elif event.key == K_s:
					self.key[0x8] = 1
				elif event.key == K_d:
					self.key[0x9] = 1
				elif event.key == K_f:
					self.key[0xE] = 1
				elif event.key == K_z:
					self.key[0xA] = 1
				elif event.key == K_x:
					self.key[0x0] = 1
				elif event.key == K_c:
					self.key[0xB] = 1
				elif event.key == K_v:
					self.key[0xF] = 1

				# MENU KEYS
				elif event.key == K_ESCAPE:
					self.started = False
				elif event.key == K_F1:
					self.started = False
					self.changeRom = True
				elif event.key == K_F2:
					self.rebootGame()
				elif event.key == K_F3:
					self.paused = not self.paused
					self.screen.togglePause(self.paused)
				elif event.key == K_F4:
					self.nextStep = True
				elif event.key == K_F5:
					self.sound = not self.sound

			elif event.type == KEYUP:
				
				# GAME KEYS
				# When a key is released, we set the associated value to 0
				if event.key == K_1:
					self.key[0x1] = 0
				elif event.key == K_2:
					self.key[0x2] = 0
				elif event.key == K_3:
					self.key[0x3] = 0
				elif event.key == K_4:
					self.key[0xC] = 0
				elif event.key == K_q:
					self.key[0x4] = 0
				elif event.key == K_w:
					self.key[0x5] = 0
				elif event.key == K_e:
					self.key[0x6] = 0
				elif event.key == K_r:
					self.key[0xD] = 0
				elif event.key == K_a:
					self.key[0x7] = 0
				elif event.key == K_s:
					self.key[0x8] = 0
				elif event.key == K_d:
					self.key[0x9] = 0
				elif event.key == K_f:
					self.key[0xE] = 0
				elif event.key == K_z:
					self.key[0xA] = 0
				elif event.key == K_x:
					self.key[0x0] = 0
				elif event.key == K_c:
					self.key[0xB] = 0
				elif event.key == K_v:
					self.key[0xF] = 0

	########################################################################################################

	def timeout60Hz(self): 	# To be called at a frequency of 60Hz. Decrements the emulator timers and refreshes the screen

		if(self.delay_timer > 0): 	# We decrement the delay timer if it isn't 0
			self.delay_timer -= 1

		if(self.sound_timer > 0): 	# Same for the sound timer
			self.sound_timer -= 1
			if self.sound: 	# And if it isn't 0 and we are allowing the sound to be played, we play a beep
				self.screen.beep.play()

		if self.started: 																							# If the game is started
			self.screen.displayRegsAndVars(self.V, self.delay_timer, self.sound_timer, self.I, self.PC, self.SP) 	# We update the debugger values with our registers
			self.screen.displayMemory(self.memory) 																	# Same with our memory
			self.screen.refreshScreen() 																			# We refresh the screen

	########################################################################################################

	def dumpMemoryAndReg(self): 	# Dumps the whole memory and register values to a file named "memdump.txt" in the script folder

		result = "Opcode: {}\nPC: {}\nI: {}\nDT: {}\nST: {}\nSP: {}\nLast Stack: {}\n\n---------------------------------------------\n\n".format(hex(self.getCurrentOpcode()), hex(self.PC), hex(self.I), hex(self.delay_timer), hex(self.sound_timer), hex(self.SP), hex(self.stack[self.SP-1]))

		for idx, value in enumerate(self.V):
			result += "V[{}] = {} = {}\n".format(idx, hex(value), value)

		result += "\n\n---------------------------------------------\n\n"

		result += str(self.memory)

		with open("memdump.txt", "w") as f:
			f.write(result)

	########################################################################################################

	def dumpPixels(self): 	# Dumps the status of all pixels in a file "screen.txt" in the script folder

		result = str(self.screen)

		with open("screen.txt", "w") as f:
			f.write(result)

	########################################################################################################

	def loadFonts(self): 	# Loads the Chip 8 fonts at the beginning of the memory

		# Each character is defined by a sprite of 5 lines of 4 pixels.
		# In Chip 8, those characters are stored as 5 bytes in the memory, and each byte has its 4 MSB representing the 4 pixels. The 4 LSB are set to 0
		# In this script we wrote those bytes in a list so it'd be easier to load them (and write the code) this way, instead of setting each cell of memory one by one. We are lazy.

		fonts = [
			0xF0, 0x90, 0x90, 0x90, 0xF0, 	# 0
			0x20, 0x60, 0x20, 0x20, 0x70, 	# 1
			0xF0, 0x10, 0xF0, 0x80, 0xF0, 	# 2
			0xF0, 0x10, 0xF0, 0x10, 0xF0, 	# 3
			0x90, 0x90, 0xF0, 0x10, 0x10, 	# 4
			0xF0, 0x80, 0xF0, 0x10, 0xF0, 	# 5
			0xF0, 0x80, 0xF0, 0x90, 0xF0, 	# 6
			0xF0, 0x10, 0x20, 0x40, 0x40, 	# 7
			0xF0, 0x90, 0xF0, 0x90, 0xF0, 	# 8
			0xF0, 0x90, 0xF0, 0x10, 0xF0, 	# 9
			0xF0, 0x90, 0xF0, 0x90, 0x90, 	# A
			0xE0, 0x90, 0xE0, 0x90, 0xE0, 	# B
			0xF0, 0x80, 0x80, 0x80, 0xF0, 	# C
			0xE0, 0x90, 0x90, 0x90, 0xE0, 	# D
			0xF0, 0x80, 0xF0, 0x80, 0xF0, 	# E
			0xF0, 0x80, 0xF0, 0x80, 0x80 	# F
		]

		for idx, val in enumerate(fonts): 	# For each byte
			self.memory[idx] = val 	# We put it into the memory starting from the adress 0x0 which is easier for us, but it could be anywhere between 0x00 and 0x1FF because those memory cells are free and we only need 80 of them.

	########################################################################################################

	def getCurrentOpcode(self): 	# Retrieves the value of current opcode

		# We retrieve the value in the memory for the current PC, and shift it 8 times to the left because it represents the 8 MSB of 16 bits message
		# We then add the value for the next memory cell, without any shifting because those are the 8 LSB
		# We now have our current opcode
		return ((self.memory[self.PC] << 8) + self.memory[self.PC+1])

	########################################################################################################

	def executeOpcode(self, opcode): 	# Executes the action linked to an opcode

		# Those 3 operations retrieve the 12 LSB of our opcode, in group of 4 bits, which correspond to an hexadecimal character. Usually opcodes are treated in hexadecimal, it is easier to visualize
		# This is to get the differents potential parameters of the opcode
		# So for the opcode Dxyn where we need x, y and n, we would get all of these 3 in variables

		# To do this, we use a combination of masking and shifting.
		# I don't know how to explain, but with the masking we cancel all bits which we dont need.
		# With shifting, if your bits aren't at the LSB position, their integer value doesn't represent their 4 bits value, so we shift them to put them in the LSB position

		b0 = opcode & 0x000F 			# 4th hexadecimal character (here it would be the n)
		b1 = (opcode & 0x00F0) >> 4 	# 3rd hexadecimal character (here it would be the y)
		b2 = (opcode & 0x0F00) >> 8 	# 2nd hexadecimal character (here it would be the x)

		result = opcode & 0xF000 	# First mask to switch on opcodes with their first hexadecimal value, which differentiates a lot of them
		# We will then use masking if needed to differentiate opcodes starting with the same hexadecimal value, and again if needed for the third and fourth.

		if(result == 0x0000): 	# Opcodes with 0xxx

			result = opcode & 0x000F
			if(result == 0x0000): 	# 00E0 : clears the screen
				self.screen.clear()

			elif(result == 0x000E): 	# 00EE : returns from a subroutine
				if(self.SP > 0): 					# If our stack pointer is above 0
					self.SP -= 1 					# We decrement it to return from where we came from
					self.PC = self.stack[self.SP] 	# We set the PC to the last stack value we did (so the CALL instruction). This won't fall in an infinite loop because at the end of each opcode treatment, we increase the PC to reach next instruction

		elif(result == 0x1000): 	# 1NNN : jumps to the location NNN in the memory
			self.PC = (b2<<8) + (b1<<4) + b0 	# Sets the PC to the value of NNN. We need to shift our values in order to create the real value
			self.PC -= 2 						# Remember to decrement the PC by a step, because at the end of this instruction it'll be incremented by a step and we won't be where we wanted to, we will be 1 step ahead.

		elif(result == 0x2000): 	# 2NNN : calls subroutine NNN. This is like a jump but we save the current PC to return at the end of the routine
			self.stack[self.SP] = self.PC 		# Store the current PC in the stack
			if(self.SP < 15): 					# If the stack pointer isn't being overflowed (only 8 bits max) we increase it
				self.SP += 1
			self.PC = (b2<<8) + (b1<<4) + b0 	# As previously for the jump, we set the new PC by shifting the different values
			self.PC -= 2 						# And we remember to decrement the PC by a step

		elif(result == 0x3000): 	# 3XKK : skip next instruction if V[X] and KK are equal
			if(self.V[b2] == ((b1<<4)+b0)): 	# Comparison, remember to shift the KK values
				self.PC += 2 					# If those are equal, we increase the PC by a step.

		elif(result == 0x4000): 	# 4XKK : skip next instruction if V[X] and KK are not equal
			if(self.V[b2] != ((b1<<4)+b0)): 	# Same as before, just with a not equal
				self.PC += 2

		elif(result == 0x5000): 	# 5xxx
			if((opcode & 0x000F) == 0x0000): 	# 5XY0 : skip next instruction if V[X] = V[Y]
				if(self.V[b2] == self.V[b1]): 	# Same as before, but comparison between two registers
					self.PC += 2

		elif(result == 0x6000): 	# 6XKK : sets the value KK into V[X]
			self.V[b2] = (b1 << 4) + b0 	# Remember to shift the first K to be able to add the second K

		elif(result == 0x7000): 	# 7XKK : adds KK to V[X]
			self.V[b2] += (b1 << 4) + b0 	# This time it is an addition, but it is the same principle with the shifting

		elif(result == 0x8000): 	# 8xxx
			
			result = opcode & 0x000F
			if(result == 0x0000): 	# 8XY0 : sets V[X] = V[Y]
				self.V[b2] = self.V[b1] 	# No shifting needed

			elif(result == 0x0001): 	# 8XY1 : sets V[X] = V[X] OR V[Y]. It is a bitwise operation. If we do 0101 OR 1100 it'll do 1101. We do an OR on each bit
				self.V[b2] |= self.V[b1] 	# In Python a bitwise OR is done with the | symbol, and we can use its shortcut which is like self.V[b2] = self.V[b2] | self.V[b1]

			elif(result == 0x0002): 	# 8XY2 : sets V[X] = V[X] AND V[Y]. Bitwise operation
				self.V[b2] &= self.V[b1] 	# Python symbol for a bitwise AND is &

			elif(result == 0x0003): 	# 8XY3 : sets V[X] = V[X] XOR V[Y]. Bitwise operation
				self.V[b2] ^= self.V[b1] 	# Python symbol for a bitwise XOR is ^

			elif(result == 0x0004): 	# 8XY4 : adds V[Y] into V[X]. Sets V[0xF] (the last V register) to 1 if the addition is overflowing (if we have more than 8 bits, which the max value is 255). Else it is 0. And if we overflow, we just remove 256 from the number -> 258 becomes 2
				self.V[0xF] = 0 						# Resets the carry
				if((self.V[b2] + self.V[b1]) > 0xFF): 	# If we overflow
					self.V[0xF] = 1 					# We set the carry to 1
				self.V[b2] += self.V[b1] 				# We add V[Y] into V[X]. We don't care about the overflow because it is treated by our nice UnsignedBitsArray

			elif(result == 0x0005): 	# 8XY5 : V[X] = V[X] - V[Y] and sets V[0xF] to 0 if we "underflow", else it is 1.
				self.V[0xF] = 1 				# Resets the borrow
				if(self.V[b2] < self.V[b1]): 	# If we "underflow"
					self.V[0xF] = 0 			# We set the borrow to 0
				self.V[b2] -= self.V[b1] 		# Do the operation

			elif(result == 0x0006): 	# 8XY6 : sets V[0xF] to the LSB of V[Y], divides V[Y] by 2 and puts it into V[X]
				self.V[0xF] = getLSB(self.V[b1]) 	# Getting the LSB thanks to our great function above
				self.V[b2] = (self.V[b1] >> 1) 		# Dividing by 2 with binary values is the same as shifting 1 bit to the right. That is why we get the LSB beforehand, because we want to know what it was before we deleted it

			elif(result == 0x0007): 	# 8XY7 : V[X] = V[Y] - V[X]. Same as 8XY5, but VX and VY are reverted in the operation
				self.V[0xF] = 1
				if(self.V[b1] < self.V[b2]):
					self.V[0xF] = 0
				self.V[b2] = self.V[b1] - self.V[b2]

			elif(result == 0x000E): 	# 8XYE : sets V[0xF] to the MSB of V[Y], multiplies V[Y] by 2 and puts it into V[X]
				self.V[0xF] = getMSB(self.V[b1], 8) 	# Getting the MSB thanks to our great function above. 8 represents the max length of our binary value.
				self.V[b2] = (self.V[b1] << 1) 			# Multiplying by 2 with binary values is like shifting 1 bit to the left. Same as for the division, we want to know what was the deleted bit

		elif(result == 0x9000): 	# 9xxx
			if((opcode & 0x000F) == 0x0000): 	# 9XY0 : skip next inscrution if V[X] != V[Y]
				if(self.V[b2] != self.V[b1]): 	# It works the same as those "skip instruction if" opcodes we did before
					self.PC += 2

		elif(result == 0xA000): 	# ANNN : sets I = NNN
			self.I = (b2<<8) + (b1<<4) + b0 	# Always remember to shift our different N

		elif(result == 0xB000): 	# BNNN : jumps to location NNN + V[0]
			self.PC = (b2<<8) + (b1<<4) + b0 + self.V[0x0] 	# We set the PC to NNN + V[0]
			self.PC -= 2 									# Like our other jumps, we need to decrement the PC in order to reach the instruction we want

		elif(result == 0xC000): 	# CXKK : sets V[X] = (random byte) AND KK
			self.V[b2] = randint(0, 255) & ((b1 << 4) + b0) 	# Our random byte is just a value between 0 and 255, and we do a bitwise AND with KK. Beware of the bit shifting

		elif(result == 0xD000): 	# DXYN : displays a sprite of length N at coordinates (V[X], V[Y]) from the memory starting at I. Quite tricky
			self.DXYN(b2, b1, b0) 	# We just give X, Y and N to another function detailed later

		elif(result == 0xE000): 	# EXxx

			result = opcode & 0x000F
			if(result == 0x000E): 	# EX9E : skips next instruction if the key of value V[X] is pressed
				if self.key[self.V[b2]] == 1: 	# Same as always, we do the if and then we increase the PC
					self.PC += 2

			elif(result == 0x0001): 	# EXA1 : skips next instruction if the key of value V[X] isn't pressed
				if self.key[self.V[b2]] == 0: 	# Same as before
					self.PC += 2

		elif(result == 0xF000): 	# FXxx

			# Here opcodes aren't in numerical order because I'm a jackass. Sorry

			result = opcode & 0x000F
			if(result == 0x0003): 	# FX33 : stores BCD representation of V[X] in memory from the adress I
				# BCD representation is a way to easily get decimal digits from a binary number.
				# It consists in separating each digit of a decimal number and storing them independantly. Useful to store scores for instance.
				# Ex.: 231 will get you 2, 3 and 1.
				# Here we get those 3 digits (because V[X] is an 8 bits number which goes to 255) and store them in the memory at adress I for the first one, I+1 for the second and I+2 for the last one.
				# So : 	2 -> memory[I]
				#		3 -> memory[I+1]
				#		1 -> memory[I+2]
				self.memory[self.I] = self.V[b2] // 100 													# // It is an euclidian division, without the rest. So by doing this with 231, we get 2 which is what we want
				self.memory[self.I+1] = (self.V[b2] - (self.memory[self.I] * 100)) // 10 					# To get the second digit, we substract from the original number the hundreds we just got (2*100) so we have 231-200=31. We then do 31//10 and we get 3
				self.memory[self.I+2] = self.V[b2] - self.memory[self.I]*100 - self.memory[self.I+1]*10 	# For the units, we just substract the hundreds and tens. 231 - (2*100) - (3*10) = 1

			elif(result == 0x0005): 	# FXx5
				
				result = opcode & 0x00F0
				if(result == 0x0010): 	# FX15 : sets the delay timer to the value of V[X]
					self.delay_timer = self.V[b2]

				elif(result == 0x0050): 	# FX55 : copies the values from V[0] to V[X] (included) in the memory, starting from the adress I and I must be set after its last adress modified
					for i in range(0,b2+1): 				# For each value from 0 to X included
						self.memory[self.I+i] = self.V[i] 	# Sets V[i] into memory[I+i]
					self.I += b2 + 1 						# Sets I to I + X + 1 so we are the next cell than the last we modified

				elif(result == 0x0060): 	# FX65 : copies the values starting from the adress I into V[0] to V[X], and sets I to after the latest value retrieved
					for i in range(0, b2+1): 				# The for loop works the same as before, going from 0 to X included
						self.V[i] = self.memory[self.I+i] 	# The assignation is just reversed
					self.I += b2 + 1 						# Sets I to I + X + 1

			elif(result == 0x0007): 	# FX07 : V[X] = delay timer
				self.V[b2] = self.delay_timer

			elif(result == 0x0008): 	# FX18 : sound timer = V[X]
				self.sound_timer = self.V[b2]

			elif(result == 0x0009): 	# FX29 : sets I = location of the character sprite corresponding to the value of V[X]
				# Because we put our sprites from the adress 0, we just have to do I = V[X]*5.
				# If we want the sprite for 0, 0*5 = adress 0
				# But if we want the sprite for 8, 8*5 = adress 40
				# If we didn't put the sprites at 0x00, we would just have added to I the starting adress of the sprites. But by putting them at 0x00 we don't even have to do that
				self.I = self.V[b2]*5

			elif(result == 0x000A): 	# FX0A : waits for a key press, and stores the pressed key in V[X]. It stops everything, so we will use an infinite loop.
				# The side effect is that all the Python script is locked until we press the key.
				# I'm pretty sure we could avoid the infinite loop here and keeping the rest of the code by making the PC goes a step before at the end of the instruction if no key is pressed
				# This way if no key is pressed, the script still listens to event (to quit, etc.) but the next instruction is still this one
				# And if we press a key, we don't decrement the PC and all goes on

				isKeyPressed = False 						# Boolean to get out of the loop (redundant with the break)
				while not isKeyPressed: 					# While no key is pressed we stay inside the loop
					for idx, val in enumerate(self.key): 	# For each available key
						if(val == 1): 						# If the current one is pressed
							isKeyPressed = True 			# We set the boolean to True
							self.V[b2] = idx 				# Store the value of the key in V[X]
							break 							# Break out of the loop

			elif(result == 0x000E): 	# FX1E : sets I = I + V[X]
				self.I += self.V[b2]

		self.PC += 2 	# After we executed our instruction, we go to the next step with the PC, which is 2 memory cells later because we have 16 bits opcodes and a cell is only 8 bits

	########################################################################################################

	def DXYN(self, b2, b1, b0): 	# Function called by the instruction DXYN

		self.V[0xF] = 0 	# V[0xF] stores 0 by default, and 1 if during the instruction we erase a pixel (setting it to black, or 0)

		for i in range(b0): 	# For each line of our sprite

			line = self.memory[self.I+i] 	# We are reading the sprite starting from the I adress and increasing it for each line
			currentY = self.V[b1] + i 		# We set the initial Y axis position to the one given by V[Y] and we add to it the i counter to get the current line position

			if currentY < len(self.screen.pixels[0]): 	# If we are in available height of the screen

				for j in range(8): 	# A sprite is 8 bits in width

					currentX = self.V[b2] + j 	# Sets the current X position to the value given by V[X] and adding the j counter value

					if currentX < len(self.screen.pixels): 	# If we are in available width of the screen

						mask = 0x1 << (7-j) 										# Mask to be used to retrieve the wanted bit in the line (which is a byte). If I want the MSB bit, j is at 0, so we get a mask of 0b10000000. Applying it with a bitwise AND and shifting will get us our bit.
						newBit = (mask & line) >> (7-j) 							# Getting the bit by applying the mask, and shifting it back to the LSB position
						result = newBit ^ self.screen.pixels[currentX][currentY] 	# A new pixel is decided by doing a XOR between the current state of the pixel, and the value wanted by the sprite
						self.screen.pixels[currentX][currentY] = result 			# We set the result of the XOR to the screen

						if(self.screen.pixels[currentX][currentY] == 0 and newBit == 1): 	# If we erased it (with a XOR, it happens when the pixel is erased and we wanted to apply a value of 1)
							self.V[0xF] = 1 												# We set V[0xF] to 1 as described


############################################################################################################

changeRom = True 	# Boolean to do an infinite loop until we don't want to change a ROM anymore (we quit)

while changeRom: 	# While we are still wanting to play when quitting the loaded ROM

	root = Tk() 					# Creating a Tkinter window to use the file browser
	romPath = askopenfilename() 	# Displaying the file browser and getting the selecting file
	root.destroy() 					# Destroying Tkinter

	if romPath == '': 				# If no ROM path was supplied
		exit() 						# We stop

	C8 = CHIP8(romPath) 			# We create our Chip 8 object with the ROM path
	C8.loadGame() 					# We load the game into memory
	changeRom = C8.startGame() 		# We start the game and save the returned value when it ends
	del C8 							# We delete the Chip 8 object to restart with a new ROM if needed