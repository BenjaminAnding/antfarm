import random
import time
import os
import subprocess

redist = True
global_subprocesses = []

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

class Food:
	critter = None
	grows = None
	xPos = None
	yPos = None
	def __init__(self, x, y, mobile, grows):
		self.critter = mobile
		self.grows = grows
		self.xPos = x
		self.yPos = y

class Gene:
	symbols = ['h','j','k','l']
	antisymbols = ['l','k','j','h']
	genomelength = None
	pairs = []
	def __init__(self, seed, genomelength):
		self.genomelength = genomelength
		for i in range(0, genomelength):
			symbol = self.rand_sym(seed)
			self.pairs.append(str(self.symbols[symbol])+str(self.antisymbols[symbol]))
	def rand_sym(self, seed):
		return (random.randint(1,256)%seed)%len(self.symbols)
	def crossover(self, mate):
		new_genes = self.pairs[len(pairs)//2:]+mate.pairs[:-len(mate.pairs)//2]
		return new_genes
	def set_pairs(self, new):
		self.pairs = new
	def mutate(self):
		new_genes = []
		for gene in self.pairs:
			symbol = self.rand_sym(seed)
			if (random.randint(0,255)%256 == 0):
				new_genes.append(str(self.symbols[symbol])+str(self.antisymbols[symbol]))
			else:
				new_genes.append(gene)

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
		self.wallIn()
			
	def getCell(self, x, y):
		return self.farm[y][x]

	def equalize(self, x, y):
		self.getCell(x, y).incPosChem(-1*self.getCell(x,y).getNegChem())
		self.getCell(x, y).incNegChem(-1*self.getCell(x,y).getNegChem())

	def wallIn(self):
		x = self.xDim - 1
		y = self.yDim - 1
		for i in range(0, self.xDim):
			self.getCell(i, 0).addToTile('wall')
			self.getCell(i, y).addToTile('wall')
		for j in range(0, self.yDim):
			self.getCell(0, j).addToTile('wall')
			self.getCell(x, j).addToTile('wall')
			

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
	facing = None
	north = ['diagonul', 'up', 'diagonur']
	east = ['diagonur', 'right', 'diagondr']
	south = ['diagondr', 'down', 'diagondl']
	west = ['diagondl', 'left',' diagonul']	
	directions = ['wait', 'up', 'down', 'left', 'right', 'diagonul', 'diagonur', 'diagondl', 'diagondr']
	dirmap = {'wait':(0, 0), 'up':(0, -1), 'down':(0, 1), 'left':(-1, 0), 'right':(1, 0), 'diagonul':(-1, -1), 'diagonur':(1, -1), 'diagondl':(-1,1), 'diagondr':(1,1)}
	home = None
	antId = None
	xPos = None
	yPos = None
	age = 0
	genes = None
	tendencies = ['courageous', 'cautious', 'caring']
	def __init__(self, farm, antId, xPos, yPos):
		self.tendency = self.tendencies[random.randint(0,2)]
		self.home = farm
		self.antId = antId
		self.xPos = int(xPos)
		self.yPos = int(yPos)
		self.age = 0
		self.genes = Gene(random.randint(1,255), 8)

	def getGenes(self):
		return self.genes
	def setGenes(self, new_genes):
		self.genes = new_genes
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

	def senseDir(self, facing):
		posChemTrails = {}
		negChemTrails = {}
		for direction in [direction for direction in self.dirmap if direction in facing]:
			posChemTrails[direction] = self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getPosChem()
			negChemTrails[direction] = self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getNegChem()
		return max(posChemTrails, key = (lambda key: posChemTrails[key])), min(posChemTrails, key = (lambda key: posChemTrails[key]))

	def moveSensible(self):
		self.move(self.senseDir(self.directions)[0])

	def move(self, direction):
		if 'wall' not in self.home.getCell(self.getXPos() + self.dirmap[direction][0], self.getYPos() + self.dirmap[direction][1]).getContents():
			self.setXPos((self.getXPos() + self.dirmap[direction][0]) % self.home.xDim)
			self.setYPos((self.getYPos() + self.dirmap[direction][1]) % self.home.yDim)
		
	def mover(self):		
		randdir = self.directions[random.randint(0,99) % len(self.directions)]
		self.move(randdir)
	
	def mood(self):
		challenger = random.randint(1,3) % 2
		if (self.tendencies.index(self.tendency) + 1) % 2 > challenger:
			self.tendency = self.tendencies[challenger-1]
		elif (self.tendencies.index(self.tendency) + 1) % 2 < challenger:
			self.tendency = self.tendencies[challenger]
		else:
			self.tendency = self.tendency

	def turn(self):
		orientations = ['north', 'east', 'south', 'west']
		return getattr(self, orientations[random.randint(0,99) % len(orientations)])

	def move_courageous(self):
		self.move(self.senseDir(self.facing)[1])

	def move_cautious(self):
		self.move(self.senseDir(self.facing)[0])

	def move_caring(self):
		self.facing = self.turn()
		if random.randint(1,2)%2 == 0:
			self.move(self.senseDir(self.facing)[random.randint(0,1)])
		else:
			self.move('wait')
			
	def cautious_sanity(self):
		neighbors = 0
		for direction in self.dirmap:
			if 'ant' in self.home.getCell((self.getXPos()+self.dirmap[direction][0])%self.home.xDim, (self.getYPos()+self.dirmap[direction][1])%self.home.yDim).getContents():
				neighbors += 1
		return neighbors < 2

	def courageous_sanity(self):
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

	def eureka(self):
		if not redist:
			process = subprocess.Popen(['afplay', './mm.wav'])
			global_subprocesses.append(process)
			if len(global_subprocesses) > 0:
				for process in global_subprocesses:
					if process.poll() == 0:
						global_subprocesses.remove(process)
		return 1
	
	def oof(self):
		if not redist:
			process = subprocess.Popen(['afplay', './mm.wav'])
			global_subprocesses.append(process)
			if len(global_subprocesses) > 0:
				for process in global_subprocesses:
					if process.poll() == 0:
						global_subprocesses.remove(process)
		return -1

	def live(self):
		self.move_caring()
		self.age += 1
		if self.age in [x for x in range(2, 20) if all(x % y != 0 for y in range(2, x))]:
			self.mood()
		getattr(self, self.tendency+'_sanity')()	
		self.home.getCell(self.getXPos(), self.getYPos()).incPosChem(.1)
		if ((random.randint(0,99) % 3) == 0):
			getattr(self, 'move_'+self.tendency)()
		else:
			self.move_caring()
		if self.age + random.randint(0,1) == 30:
			return self.eureka()
		if self.age >= 30:
			if random.randint(0,99) % 13 == 0:
				return self.oof()
		return 0
		
	def toString(self):
		return self.tendency+', id: '+str(self.antId)+' at '+str(self.xPos)+','+str(self.yPos)

class Shell:
	"""
	Shell Class
	- Requires no parameters to construct.
	- This object houses the methods through which we will interact with our ant farms.
	"""
	ants = {}
	ants[0] = 'dummy'
	commands = ['help', 'spawn', 'kill', 'list', 'sim', 'cull', 'ZZ']
	commandHelp = {'help':'Displays help messages',
					'spawn':'<n> spawn <x y> \n Spawn (n number of) ant(s) at (x y)|0 0',
					'kill':'kill n <x> \n Kill ant with id n, if x is given kill all ants within id range [n,x]',
					'list':'list \n Lists current living ants',
					'sim':'<n> sim <x> \n Perform x steps of life simulation (n times)',
					'cull': 'kills all ants over the age of 30, Logan\'s Run style'}
	farm = None
	def draw(self):
		self.farm.drawFarm()
		print("Ants in farm: ", len(self.ants)-1)

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
		spawnstrings = []
		obituaries = []
		for ant in self.ants:
			if ant != 0:
				#self.ants[ant].mover()
				rbat = self.ants[ant].live()
				if rbat > 0:
					spawnstrings.append(str(self.ants[ant].getXPos())+' '+str(self.ants[ant].getYPos()))
				elif rbat < 0:
					obituaries.append(str(ant))
		self.populate()
		for baby_ant in spawnstrings:
			self.spawn(baby_ant)
		self.depopulate()
		self.populate()
		for deceased in obituaries:
			self.kill(deceased)
		self.depopulate()
		self.populate()
		os.system('clear')
		self.draw()
		time.sleep(0.18)

	def ZZ(self, args):
		while len(self.ants) not in [42, 0]:
			getattr(self, 'sim')([])
			getattr(self, 'cull')([])
		
		

	def help(self, args):
		if len(args) == 1:
			if args[0] in self.commands:
				print(self.commandHelp[args[0]])
		else:
			print("Commands: "+str(self.commands))
			print("help <command> for more info on <command>")
			print("** to quit.")

	def cull(self, args):
		logans = []
		for ant in self.ants:
			if ant != 0:
				if self.ants[ant].age > 30:
					logans.append(str(ant))	
		for run in logans:
			getattr(self, 'kill')([run])

	def spawn(self, args):
		self.depopulate()
		if (len(args) == 2):
			if not all(x.isdigit() for x in ''.join(args)):
				print("'spawn' parameters must be two valid integers.")
				return 'oof'
			else:
				self.ants[max(self.ants.keys())+1] = Ant(self.farm, max(self.ants.keys())+1, int(args[0]) % int(self.farm.xDim), int(args[1]) % int(self.farm.yDim))
		else:
			self.ants[max(self.ants.keys())+1] = Ant(self.farm, max(self.ants.keys())+1, self.farm.xDim//2, self.farm.yDim//2)
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
				print(self.ants[ant].age, self.ants[ant].toString())
		print(str(len(self.ants)-1)+" ants in farm.")
	def handleCommand(self, command):
		numTimes = 1
		idx = 0
		command = command.strip()
		if len(command.split(' ')) > 1:
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
