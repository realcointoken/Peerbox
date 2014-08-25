#!/usr/bin/python2
# -*- coding: utf-8 -*-
#
# Copyright 2014 Peerchemist
#
# This file is part of Peerbox project.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
 
__author__ = "Peerchemist"
__license__ = "GPL"
__version__ = "0.1"

import os, sys
import sh
import argparse
import json
import platform
from datetime import timedelta

## Class that pulls and parses data
class pbinfo:

	def system(self):

		def uptime():

			with open('/proc/uptime', 'r') as f:
				uptime_seconds = float(f.readline().split()[0])
				uptime_str = str(timedelta(seconds = uptime_seconds))

			return(uptime_str)

		def distr():

			with open('/etc/os-release', 'r') as lsb:
				for line in lsb:
					if line.startswith('VERSION_ID'):
						return(line.split('=')[1].replace('"','').strip())

		mm = {
			'peerbox': distr(),
			'kernel release': platform.release(),	
			'uptime': uptime(),
			'average load': os.getloadavg()
			}

		return(mm)


	def hardware(self):

		mm = {}

		with open('/proc/cpuinfo') as cpuinfo:
			for line in cpuinfo:
				if line.startswith('Hardware'):
					hardware = line.split(':')[1].strip()
					if hardware == "BCM2708":
						mm['hardware'] = "Raspberry Pi"

				if line.startswith('Serial'):
					ser = line.split(':')[1].strip()
					mm['serial'] = ser


		with open('/proc/cmdline', 'r') as cmdline:
			for i in cmdline.readline().split():
				if i.startswith('smsc95xx.macaddr'):
					mm['maccaddr'] = str(i.split('=')[1])

				if i.startswith('bcm2708.boardrev'):
					mm['board_rev'] = str(i.split('=')[1])

		return(mm)


	def ppcoind(self, argv):

		get = sh.ppcoind("getinfo", _ok_code=[0,3,5,87]).stdout

		try:
			getinfo = json.loads(get)
		except:
			return("ppcoind inactive")

		## When posting in public, hide IP and balance.
		if argv == "private":
			del getinfo['balance']
			del getinfo['ip']
			return(getinfo)

		else:
			return(getinfo)

## Class that will do all the pretty printing
class box:

	def default(self): ## printed when no arguments

		box = {}

		box['Peerbox:'] = "v" + pbinfo.system()['peerbox']
		box['uptime'] = pbinfo.system()['uptime']
		box['ppcoind'] = pbinfo.ppcoind(self)
		box['serial'] = pbinfo.hardware()['serial']
		box['raspi_board_rev'] = pbinfo.hardware()['board_rev']
		return(json.dumps(box, sort_keys=True, indent=4))

	def public(self): ## When privacy is needed

		box = {}

		box['Peerbox:'] = "v" + pbinfo.system()['peerbox']
		box['serial'] = pbinfo.hardware()['serial']
		box['uptime'] = pbinfo.system()['uptime']
		box['ppcoind'] = pbinfo.ppcoind("private")
		return(json.dumps(box, sort_keys=True, indent=4))		

	def all(self): ## Switch to show all

		box = {}

		box['system'] = pbinfo.system()
		box['system'].update(pbinfo.hardware())
		box['ppcoind'] = pbinfo.ppcoind(self)
		return(json.dumps(box, sort_keys=True, indent=4))


pbinfo = pbinfo()
box = box()

######################### args

parser = argparse.ArgumentParser(description='Show information on Peerbox')
parser.add_argument('-a', '--all', help='Show everything', action='store_true')
parser.add_argument('-s','--system', help='Show system information', action='store_true')
parser.add_argument('-p', '--ppcoin', help='Equal to "ppcoid getinfo"', action='store_true')
parser.add_argument('--public', help='Hide private data [ip, balance, serial]', action='store_true')
parser.add_argument('-o', '--output', help='Dump data to stdout, use to pipe to some other program', 
																		action='store_true')
args = parser.parse_args()

## Default, if no arguments
if not any(vars(args).values()):
	print(box.default())

if args.all:
	print(box.all())

if args.system:
	print(pbinfo.system())

if args.ppcoin:
	print(json.dumps(pbinfo.ppcoind("self"), indent=4))

if args.public:
	print(box.public())

if args.output:
	sys.stdout.write(box.all())
