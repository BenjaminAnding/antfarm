import os
import time
from antfarm import *

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
