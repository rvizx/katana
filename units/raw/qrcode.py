from unit import BaseUnit
from collections import Counter
import sys
from io import StringIO
import argparse
from pwn import *
import subprocess
import units.raw
import utilities
import os
import magic
from units import NotApplicable

dependancy_command = 'zbarimg'

class Unit(units.raw.RawUnit):

	def __init__(self, katana, parent, target):
		super(Unit, self).__init__(katana, parent, target)
		# We can only handle this if it is a file!
		if not os.path.isfile(target) or 'image' not in magic.from_file(target):
			raise NotApplicable


	def evaluate(self, katana, case):

		p = subprocess.Popen([dependancy_command, self.target ], stdout = subprocess.PIPE, stderr = subprocess.PIPE)

		# Look for flags, if we found them...
		response = utilities.process_output(p)
		if 'stdout' in response:
			
			# If we see anything interesting in here... scan it again!
			for line in response['stdout']:
				katana.recurse(self, line)

			self.locate_flags(katana,str(response['stdout']))

		if 'stderr' in response:
			self.locate_flags(katana, str(response['stderr']))

		katana.add_results(self, response)

# Ensure the system has the required binaries installed. This will prevent the module from running on _all_ targets
try:
	subprocess.check_output(['which',dependancy_command])
except (FileNotFoundError, subprocess.CalledProcessError) as e:
	raise units.DependancyError(dependancy_command)