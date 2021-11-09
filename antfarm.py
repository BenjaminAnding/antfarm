import random
import time
import os

class Cell:
	"""
	Cell class
	- requres x and y position param
	- individual parts of farm (x,y location, contents)
	"""
	xLoc = None
	yLoc = None
	def __init__(self, xLoc, yLoc):
		self.xLoc = xLoc
		self.yLoc =	yLoc
		self.contents = []
		self.posChem = 0
		self.negChem = 0
	def clearContents(self):
		self.contents = []
	def addToTile(self, thing):
		self.contents.append(thing)
	def getContents(self):
		return self.contents
	def setXLoc(self, xLoc):
		self.xLoc = xLoc
	def getXLoc(self):
		return self.xLoc
	def setYLoc(self, yLoc):
		self.yLoc = yLoc
	def getYLoc(self):
		return self.yLoc
	def depop(self, thing):
		self.contents.remove(thing)
	def incPosChem(self, x):
		self.posChem += x
	def incNegChem(self, x):
		self.negChem += x
	def getPosChem(self):
		return self.posChem
	def getNegChem(self):
		return self.negChem

class Farm:
	"""
	Farm Class
	- Requires 2 integer parameters to construct.
	- Holds the world in which the ants will live.
	"""
	farm = []
	xDim = None
	yDim = None
	ant = '@'
	food = '*'
	floor = '.'
	wall = '#'
	rowString = ''
	def __init__(self, xDim, yDim):
		self.xDim = int(xDim)
		self.yDim = int(yDim)
		for i in range(yDim):
			farmRow = []
			for j in range(xDim):
				newCell = Cell(j, i)
				newCell.addToTile('floor')
				farmRow.append(newCell)
			self.farm.append(farmRow)
			
	def getCell(self, x, y):
		return self.farm[y][x]

	def equalize(self, x, y):
		self.getCell(x, y).incPosChem(-1*self.getCell(x,y).getNegChem())
		self.getCell(x, y).incNegChem(-1*self.getCell(x,y).getNegChem())

	def drawFarm(self):
		for i in range(self.yDim):
			for j in range(self.xDim):
				self.equalize(j,i)
				self.rowString+=getattr(self, self.getCell(j,i).getContents()[-1])
			print(self.rowString)
			self.rowString = ''	


class Ant:
	"""
	Ant Class
	- Requires a farm and 3 integer values to construct (id, x, y). 
	- These are the little buggers we're going to observe.
	"""
	directions = ['wait', 'up', 'down', 'left', 'right']
	dirmap = {'wait':(0, 0), 'up':(0, -1), 'down':(0, 1), 'left':(-1, 0), 'right':(1, 0)}
	home = None
	antId = None
	xPos = None
	yPos = None
	tendencies = ['courageous', 'cautious', 'caring']
	def __init__(self, farm, antId, xPos, yPos):
		self.tendency = self.tendencies[random.randint(0,2)]
		self.home = farm
		self.antId = antId
		self.isHappy = None
		self.isOnFood = None
		self.xPos = int(xPos)
		self.yPos = int(yPos)

	def getAntId(self):
		return self.antId
	def setAntId(self, antId):
		self.antId = antId
	def getXPos(self):
		return self.xPos
	def setXPos(self, xPos):
		self.xPos = xPos
	def getYPos(self):
		return self.yPos
	def setYPos(self, yPos):
		self.yPos = yPos

	def senseDir(self):
		posChemTrails = {}
		negChemTrails = {}
		#directions = {'wait':(0,0), 'up':(0, -1), 'down':(0, 1), 'left':(-1, 0), 'right':(1, 0)}
		for direction in self.dirmap:
			posChemTrails[direction] = self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getPosChem()
			negChemTrails[direction] = self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getNegChem()
		return max(posChemTrails, key = (lambda key: posChemTrails[key])), min(posChemTrails, key = (lambda key: posChemTrails[key]))

	def moveSensible(self):
		self.move(self.senseDir()[0])

	def move(self, direction):
		if (direction == 'left'):
			self.setXPos((self.getXPos() - 1) % self.home.xDim)
		if (direction == 'right'):
			self.setXPos((self.getXPos() + 1) % self.home.xDim)
		if (direction == 'up'):
			self.setYPos((self.getYPos() - 1) % self.home.yDim)
		if (direction == 'down'):
			self.setYPos((self.getYPos() + 1) % self.home.yDim)

	def mover(self):		
		randdir = self.directions[random.randint(0,99) % len(self.directions)]
		self.move(randdir)
	
	def mood(self):
		challenger = random.randint(1,3) % 2
		if (self.tendencies.index(self.tendency) + 1) % 2 >= challenger:
			self.tendency = self.tendencies[challenger+1]
		else:
			self.tendency = self.tendencies[challenger]

	def move_cautious(self):
		self.move(self.senseDir()[0])

	def move_curious(self):
		self.move(self.senseDir()[1])

	def move_caring(self):
		self.move('wait')
			
	def cautious_sanity(self):
		neighbors = 0
		for direction in self.dirmap:
			if 'ant' in self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getContents():
				neighbors += 1
		return neighbors < 2

	def curious_sanity(self):
		neighbors = 0
		for direction in self.dirmap:
			if 'ant' in self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getContents():
				neighbors += 1
		return neighbors < 3
	
	def caring_sanity(self):
		neighbors = 0
		for direction in self.dirmap:
			if 'ant' in self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getContents():
				neighbors += 1
		return neighbors < 3


	def live(self):
		self.mood()
		getattr(self, self.tendency+'_sanity')()	
		self.home.getCell(self.getXPos(), self.getYPos()).incPosChem(.1)
		if ((random.randint(0,99) % 3) == 0):
			getattr(self, 'move_'+self.tendency)()
		else:
			self.mover()

	def toString(self):
		return self.tendency+' Ant:'+str(self.antId)+' at '+str(self.xPos)+','+str(self.yPos)

class Shell:
	"""
	Shell Class
	- Requires no parameters to construct.
	- This object houses the methods through which we will interact with our ant farms.
	"""
	ants = {}
	ants[0] = 'dummy'
	commands = ['help', 'spawn', 'kill', 'list', 'sim']
	commandHelp = {'help':'Displays help messages',
					'spawn':'<n> spawn <x y> \n Spawn (n number of) ant(s) at (x y)|0 0',
					'kill':'kill n <x> \n Kill ant with id n, if x is given kill all ants within id range [n,x]',
					'list':'list \n Lists current living ants',
					'sim':'<n> sim <x> \n Perform x steps of life simulation (n times)'}
	farm = None
	def draw(self):
		self.farm.drawFarm()

	def populate(self):
		for ant in self.ants:
			if ant != 0:
				self.farm.getCell(self.ants[ant].getXPos(), self.ants[ant].getYPos()).addToTile('ant')

	def depopulate(self):
		for ant in self.ants:
			if ant != 0:
				self.farm.getCell(self.ants[ant].getXPos(), self.ants[ant].getYPos()).depop('ant')

	def simLife(self):
		self.depopulate()
		for ant in self.ants:
			if ant != 0:
				#self.ants[ant].mover()
				self.ants[ant].live()
		self.populate()
		os.system('clear')
		self.draw()
		time.sleep(0.2)

	def help(self, args):
		if len(args) == 1:
			if args[0] in self.commands:
				print(self.commandHelp[args[0]])
		else:
			print("Commands: "+str(self.commands))
			print("help <command> for more info on <command>")
			print("** to quit.")

	def spawn(self, args):
		self.depopulate()
		if (len(args) == 2):
			if not all(x.isdigit() for x in ''.join(args)):
				print("'spawn' parameters must be two valid integers.")
				return 'oof'
			else:
				self.ants[max(self.ants.keys())+1] = Ant(self.farm, max(self.ants.keys())+1, int(args[0]) % int(self.farm.xDim), int(args[1]) % int(self.farm.yDim))
		else:
			self.ants[max(self.ants.keys())+1] = Ant(self.farm, max(self.ants.keys())+1, 0, 0)
		self.populate()

	def sim(self, args):
		if (len(args) == 1):
			if not all(x.isdigit() for x in ''.join(args)):
				print("'step' parameter must be a valid integer.")
				return 'oof'
			if (int(args[0]) > 0):
				for i in range(int(args[0])):
					self.simLife()
		else:
			self.simLife()

	def kill(self, args):
		self.depopulate()
		if (len(args) == 1):
			if all(x.isdigit() for x in ''.join(args)):
				if int(args[0]) in self.ants.keys():
					if int(args[0]) is not 0:
						self.ants.pop(int(args[0]))
		if (len(args) == 2):
			if all(x.isdigit() for x in ''.join(args)):
				for i in range(int(args[0]), int(args[1])+1):
					if 	i in self.ants.keys():
						if i is not 0:
							self.ants.pop(i)
		self.populate()

	def list(self, args):
		for ant in self.ants:
			if ant != 0:
				print(ant, self.ants[ant].toString())

	def handleCommand(self, command):
		numTimes = 1
		idx = 0
		command = command.strip()
		if command.split(' ')[0].isdigit():
			numTimes = int(command.split(' ')[0])
			idx = 1
		if (command.split(' ')[idx] in self.commands):
			for i in range(numTimes):
				getattr(self, command.split(' ')[idx])(command.split(' ')[idx+1:])

	def __init__(self, boo):
		if not boo:
			print("Input x dim: ")
			print(">", end='')
			xDim = input()
			while (not all(x.isdigit() for x in xDim)) or xDim is '':
				print("Please enter valid integer: ")
				print(">", end='')
				xDim = input()
			print("Input y dim: ")
			print(">", end='')
			yDim = input()
			while (not all(x.isdigit() for x in yDim)) or yDim is '':
				print("Please enter valid integer: ")
				print(">", end='')
				yDim = input()
		else:
			xDim = 118
			yDim = 22
		print("Building farm...")
		self.farm = Farm(int(xDim), int(yDim))
		self.farm.drawFarm()

if __name__ == '__main__':
	print('Welcome to antfarm! Performing shell setup...')
	print("First things first, let's make your farm!")
	print('Default settings? 118 x 22 [Y/n]', end='')
	command = input()
	while command.strip().lower() not in ['', 'n', 'y']:
		command = input()
	if command.strip().lower() in ['', 'y']:
		shell = Shell(True)
	else:
		shell = Shell(False)
	command = ''
	print('Type "help" for help.')
	while (command != '**'):
		print('>', end='')
		command = input()
		shell.handleCommand(command)
