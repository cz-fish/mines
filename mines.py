#!/usr/bin/env python
#
# Minefield
#   text-mode mine-sweeping logical puzzle in Python with curses library
# Author:
#   Filip Simek, 2009, <filip.simek@gmail.com>
#
# This program is free software, which can be used and distributed under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the license, or (at your
# option) any later version. For the full text of the license, see
# <http://www.gnu.org/licenses/>.

import sys
import random
import re
import curses
import getopt

# these are default values, that can be overridden by the program's arguments
WIDTH = 20
HEIGHT = 20
MINES = 90

def printUsage(name):
	global WIDTH, HEIGHT, MINES
	print """Usage: %s [options]
where [options] may be one or more of the following
 -h,   --help      this help
 -x X, --width=X   set width of the mine field (%d)
 -y Y, --height=Y  set height of the mine field (%d)
 -m M, --mines=M   set number of mines (%d)""" % (name, WIDTH, HEIGHT, MINES)

def numberToAlpha(number):
	"""Converts the given integer to its corresponding letter or string of letters.
	   Indices are zero based (0=A, 25=Z, 26=AA, 27=AB, ...)"""
	r = ''
	a = 0
	while 1:
		x = number % 26
		if a == 0:
			a = 1
		else:
			x -= 1
		r = chr(ord('A')+x) + r
		number /= 26
		if number == 0:
			break
	return r

def alphaToNumber(alpha):
	"""Converts a string of letters to its corresponding integer."""
	r = 0
	l = len(alpha)
	while l > 0:
		c = alpha[0]
		if ord(c) >= ord('a') and ord(c) <= ('z'):
			n = ord(c) - ord('a')
		elif ord(c) >= ord('A') and ord(c) <= ('Z'):
			n = ord(c) - ord('A')
		else:
			raise ValueError
		if l > 1:
			n += 1
		r = 26 * r + n
		alpha = alpha[1:]
		l -= 1
	return r

def parseCommand(com):
	"""Parses a command, i.e. extracts user action and coordinates
	   
	   returns a triplet: (action, column, row)
	   where action can be:
	   	0 - discover the field
		1 - mark a mine (!)
		2 - mark the field with a question mark (?)
		3 - quit the game
		4 - request help
		5 - redraw (or print) the field
	
	   raises:
	   	ValueError if the command has an invalid syntax
	"""
	c = com.strip()
	# extract action
	action = 0
	if c == 'quit':
		return (3, 0, 0)
	elif c == 'help':
		return (4, 0, 0)
	elif c == 'print':
		return (5, 0, 0)
	elif c[0] == '!':
		action = 1
		c = c[1:]
	elif c[0] == '?':
		action = 2
		c = c[1:]
	
	# extract X coordinate
	m = re.match('^([a-zA-Z]+)',c)
	if m == None:
		raise ValueError
	# convert X coordinate to number
	x = alphaToNumber(m.group(1))
	# strip X coordinate from the command
	c = c[len(m.group(1)):]

	# extract Y coordinate
	m = re.match('^([0-9]+)', c)
	if m == None:
		raise ValueError
	# X is zero-based, let Y be as well
	y = int(m.group(1)) - 1

	return (action, x, y)


class MineField():
	def __init__(self, width, height, mines):
		self.width = width
		self.height = height
		self.mines = mines
		# arrays numbers and visible are indexed with [row][column]
		self.numbers = [[0 for i in xrange(width)] for j in xrange(height)]
		self.visible = [[0 for i in xrange(width)] for j in xrange(height)]
		self.placeMines()
		# number of exclamation marks placed
		self.exclam = 0
		# number of question marks placed
		self.question = 0
		self.solved = 0
		self.xoff = 0


	def placeMines(self):
		if self.width * self.height < self.mines:
			raise OverflowError()
		i = 0
		while i < self.mines:
			# place a mine to an empty position
			x = random.randint(0, self.width - 1)
			y = random.randint(0, self.height - 1)
			if self.numbers[y][x] == 0:
				self.numbers[y][x] = -1
				i += 1
		# fill the rest of the numbers array
		for x in xrange(self.width):
			for y in xrange(self.height):
				if self.numbers[y][x] == -1:
					continue
				# count neighbouring mines
				self.numbers[y][x] = self.neighbours(x,y)


	def neighbours(self, x, y):
		m = 0
		hlimit = self.height - 1
		wlimit = self.width - 1
		if x > 0:
			if self.numbers[y][x-1] == -1: m += 1
			if y > 0:
				if self.numbers[y-1][x-1] == -1: m += 1
			if y < hlimit:
				if self.numbers[y+1][x-1] == -1: m += 1
		if y > 0:
			if self.numbers[y-1][x] == -1: m += 1
		if y < hlimit:
			if self.numbers[y+1][x] == -1: m += 1
		if x < wlimit:
			if self.numbers[y][x+1] == -1: m += 1
			if y > 0:
				if self.numbers[y-1][x+1] == -1: m += 1
			if y < hlimit:
				if self.numbers[y+1][x+1] == -1: m += 1
		return m

	def printPosition(self, scr, x, y, hilite):
		"""Print one given position of the mine field (consider
		the curses cursor position already set.

		scr - curses' window
		x - column
		y - row
		hilite - if true, hilite this position
		"""
		i = self.numbers[y][x]
		j = self.visible[y][x]
		atr = curses.color_pair(0)
		if j == 0:
			atr |= curses.A_DIM
			s = 'X'
		elif j == 1:
			if i == -1:
				atr = curses.color_pair(2) | curses.A_BLINK
				s = 'M'
			elif i == 0:
				s = ' '
			else:
				if i == 1:
					atr = curses.color_pair(5) #green
				elif i <= 4:
					atr = curses.color_pair(3) #blue
				else:
					atr = curses.color_pair(1) #yellow
				s = str(i)
		elif j == 2:
			s = '!'
			atr = curses.color_pair(4) | curses.A_BOLD
		elif j == 3:
			s = '?'
			atr = curses.color_pair(6) | curses.A_BOLD
		elif j == 4:
			# the field is marked with !, but there
			# is no mine on that position and the
			# player has been blown up
			s = 'W'
			atr = curses.color_pair(2)
		if hilite:
			atr = curses.color_pair(7)
			#atr = atr & ~curses.A_DIM | curses.A_UNDERLINE
		scr.addstr(" %s " % s, atr)

	def printHorCaption(self, scr, x, hilite):
		if hilite:
			atr = curses.color_pair(1)
		else:
			atr = curses.color_pair(0)
		scr.addstr("%2s " % numberToAlpha(x), atr)

	def printVertCaption(self, scr, y, hilite):
		if hilite:
			atr = curses.color_pair(1)
		else:
			atr = curses.color_pair(0)
		scr.addstr("%2s " % str(y+1), atr)

	def printField(self, scr, posx, posy):
		"""Print the whole mine field using curses' functions.

		scr - curses' window
		posx, posy - current cursor position (will be hilighted)
		"""
		# compute horizontal offset to have the field centered
		size = scr.getmaxyx()
		self.xoff = (size[1] - 3 * self.width - 3) / 2
		if self.xoff < 0:
			self.xoff = 0
		scr.move(1, self.xoff + 3)
		# print top captions (column indices)
		for x in xrange(self.width):
			self.printHorCaption(scr, x, x == posx)
		# print left captions (row indices) and the field
		for y in xrange(self.height):
			scr.move(y + 2, self.xoff)
			self.printVertCaption(scr, y, y == posy)
			for x in xrange(self.width):
				self.printPosition(scr, x, y, x == posx and y == posy)

		# print current score
		scr.move(0,2)
		scr.addstr("Mines: %d / %d  " % (self.exclam, self.mines))

	def takeAction(self, action, x, y):
		if x < 0 or y < 0 or x >= self.width or y >= self.height:
			raise IndexError
		if action < 0 or action > 2:
			raise ValueError
		v = self.visible[y][x]
		if v == 1:
			# this position is already discovered
			return
		if action == 0:
			# discover
			if v == 2:
				# don't allow the user to discover a position that is
				# marked with an '!'
				return
			if self.numbers[y][x] == -1:
				self.boom()
			elif self.numbers[y][x] == 0:
				self.floodDiscover(x, y)
			else:
				self.visible[y][x] = 1
		elif action == 1:
			# !
			# toggle a ! mark or override a ? mark
			if v == 2:
				self.exclam -= 1
				self.visible[y][x] = 0
			elif v == 3:
				self.question -= 1
				self.exclam += 1
				self.visible[y][x] = 2
			else:
				self.exclam += 1
				self.visible[y][x] = 2
		elif action == 2:
			# ?
			# toggle a ? mark or override a ! mark
			if v == 2:
				self.exclam -= 1
				self.question += 1
				self.visible[y][x] = 3
			elif v == 3:
				self.question -= 1
				self.visible[y][x] = 0
			else:
				self.question += 1
				self.visible[y][x] = 3

	def isSolved(self):
		if self.solved > 0:
			return self.solved
		# all positions without mines must have been discovered to
		# claim the game solved
		for x in xrange(self.width):
			for y in xrange(self.height):
				if self.numbers[y][x] != -1 and self.visible[y][x] != 1:
					return 0
		self.solved = 1
		return 1

	def boom(self):
		self.solved = 2
		# uncover all mines
		for x in xrange(self.width):
			for y in xrange(self.height):
				if self.numbers[y][x] != -1 and self.visible[y][x] == 2:
					# this position is incorrectly marked as a mine
					self.visible[y][x] = 4
				elif self.numbers[y][x] == -1:
					# uncover the mine
					self.visible[y][x] = 1

	def floodDiscover(self, x, y):
		if self.visible[y][x] != 0:
			return
		self.visible[y][x] = 1
		if self.numbers[y][x] != 0:
			return
		hlimit = self.height - 1
		wlimit = self.width - 1
		if x > 0:
			self.floodDiscover(x-1, y)
			if y > 0:
				self.floodDiscover(x-1, y-1)
			if y < hlimit:
				self.floodDiscover(x-1, y+1)
		if y > 0:
			self.floodDiscover(x, y-1)
		if y < hlimit:
			self.floodDiscover(x, y+1)
		if x < wlimit:
			self.floodDiscover(x+1, y)
			if y > 0:
				self.floodDiscover(x+1, y-1)
			if y < hlimit:
				self.floodDiscover(x+1, y+1)

class Control():
	def __init__(self, stdscr, minefield):
		# curses window
		self.stdscr = stdscr
		# mine field
		self.field = minefield
		# cursor position
		self.posx = 0
		self.posy = 0
		# vertical position of the prompt line
		self.prompty = minefield.height + 3
		# vertical position of the message line
		self.msgy = minefield.height + 5
		self.initColors()
	
	def initColors(self):
		curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
		curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLUE)

	def checkWindowSize(self):
		size = self.stdscr.getmaxyx()
		if 3 * (self.field.width + 1) >= size[1] or self.field.height + 5 >= size[0]:
			return 0
		return 1

	def message(self, msg):
		scr = self.stdscr
		size = scr.getmaxyx()
		y = self.msgy
		x = 2
		l = len(msg)
		# amount of free space for the message
		amount = (size[0] - y) * size[1] - 3
		if amount < l:
			# there's too little space, remove indentation
			y -= 1
			x = 0
			amount = (size[0] - y) * size[1] - 1
			if amount > l:
				# the whole message can now be printed
				amount = l
			# else print only 'amount' first characters of the msg
		else:
			amount = l
		scr.move(y, x)
		scr.addstr(msg[:amount])
		scr.getch()
		scr.move(y, x)
		scr.addstr(amount * ' ')

	def decorate(self):
		self.stdscr.move(self.prompty, 2)
		self.stdscr.addstr("> ")
	
	def reprintStr(self):
		self.stdscr.move(self.prompty, 4)
		self.stdscr.addstr(20*' ')
		self.stdscr.move(self.prompty, 4)
		self.stdscr.addstr(self.str)

	def loop(self):
		# main loop
		field = self.field
		while 1:
			self.str = ''
			self.reprintStr()
			a, b = self.input()
			if a == 0:
				# input is a string that needs to be parsed
				try:
					action, x, y = parseCommand(b)
				except ValueError:
					self.message("Invalid syntax. Read the game's manual for help.")
					continue
			else:
				# the action is already known
				action = b
				x = self.posx
				y = self.posy

			if action == 3:
				return
			elif action == 4:
				#NOTE: there's no in-game help now. Do nothing
				pass
			elif action == 5:
				# refresh screen
				# this action is also performed when the window was resized
				self.stdscr.clear()
				while not self.checkWindowSize():
					# window is too small
					size = self.stdscr.getmaxyx()
					s = size[0] * size[1]
					if s >= 64:
						self.stdscr.addstr("Window is too small. Please resize it or quit with the Esc key.")
					# else there is not even enough space to print the message
					while 1:
						c = self.stdscr.getch()
						if c == 27:
							return
						elif c == curses.KEY_RESIZE:
							self.stdscr.clear()
							break
				# window size is ok
				self.decorate()
				self.reprintStr()
				field.printField(self.stdscr, self.posx, self.posy)
			else:
				try:
					field.takeAction(action, x, y)
				except IndexError:
					self.message("Position is out of range")
					continue
				field.printField(self.stdscr, self.posx, self.posy)
				sol = field.isSolved()
				if sol == 1:
					self.message("Mine field clear, good job!")
					return
				elif sol == 2:
					self.message("You've been blown up, better luck next time")
					return
	
	def input(self):
		while 1:
			c = self.stdscr.getch()
			if c == curses.KEY_LEFT:
				self.moveCursor(-1,0)
			elif c == curses.KEY_RIGHT:
				self.moveCursor(1,0)
			elif c == curses.KEY_UP:
				self.moveCursor(0,-1)
			elif c == curses.KEY_DOWN:
				self.moveCursor(0,1)
			elif c == 12 or c == curses.KEY_RESIZE:
				# ^L
				# return action 5 = refresh screen
				return (1, 5)
			elif c == 10:
				# enter
				if self.str != '':
					# return the string entered
					return (0, self.str)
				else:
					# return action 0 = discover
					return (1, 0)
			elif c == 27:
				# return action 3 = quit
				return (1, 3)
			elif c == ord(' '):
				# return action 1 = mark !
				return (1, 1)
			elif c == 9:
				# tab
				# return action 2 = mark ?
				return (1, 2)
			elif c == curses.KEY_BACKSPACE or c == curses.KEY_DC:
				self.str = self.str[:-1]
				self.reprintStr()
			elif c >= 32 and c <= 127:
				if len(self.str) < 20:
					self.str += chr(c)
				self.reprintStr()


	def moveCursor(self, xdiff, ydiff):
		scr = self.stdscr
		x = self.posx
		y = self.posy
		field = self.field
		scr.move(y + 2, field.xoff + 3 * x + 3)
		field.printPosition(scr, x, y, 0)
		if xdiff != 0:
			scr.move(1, field.xoff + 3 * x + 3)
			field.printHorCaption(scr, x, 0)
			maxx = self.field.width
			x += xdiff
			if x < 0:
				x += maxx
			elif x >= maxx:
				x -= maxx
			scr.move(1, field.xoff + 3 * x + 3)
			field.printHorCaption(scr, x, 1)
		if ydiff != 0:
			scr.move(y + 2, field.xoff)
			field.printVertCaption(scr, y, 0)
			maxy = self.field.height
			y += ydiff
			if y < 0:
				y += maxy
			elif y >= maxy:
				y -= maxy
			scr.move(y + 2, field.xoff)
			field.printVertCaption(scr, y, 1)
		# hilite the new field
		scr.move(y + 2, field.xoff + 3 * x + 3)
		field.printPosition(scr, x, y, 1)
		self.posx = x
		self.posy = y
		scr.move(self.prompty, 4)


endmsg = ''

def main(stdscr):
	global endmsg
	global WIDTH, HEIGHT, MINES
	try:
		field = MineField(WIDTH, HEIGHT, MINES)
		ctrl = Control(stdscr, field)
	except OverflowError:
		endmsg = "There are more mines than the mine field can take."
		return

	if not ctrl.checkWindowSize():
		endmsg = "Window is too small for the given mine field."
		return

	stdscr.clear()
	field.printField(stdscr, 0, 0)
	ctrl.decorate()
	ctrl.loop()



# program entry point
if __name__ == '__main__':
	# parse arguments
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hx:y:m:",\
				["help", "width=", "height=", "mines="])
	except getopt.GetoptError:
		printUsage(sys.argv[0])
		sys.exit(1)
	for o, a in opts:
		if o in ('-h', '--help'):
			printUsage(sys.argv[0])
			sys.exit(0)
		elif o in ('-x', '--width'):
			WIDTH = int(a)
		elif o in ('-y', '--height'):
			HEIGHT = int(a)
		elif o in ('-m', '--mines'):
			MINES = int(a)

	# fail-safe wrapper for the main function
	curses.wrapper(main)
	print >>sys.stderr, endmsg


