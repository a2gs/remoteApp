#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota
# andre.scota@gmail.com
# MIT license

import configparser

class racCfg():
	cfgs = None
	cfgFile = ''

	def __init__(self, fileCfg : str):
		self.cfgFile = fileCfg
		self.cfgs = configparser.ConfigParser()
		self.load()

	def get(self, section : str, key : str) -> [bool, None]:
		try:
			value = self.cfgs[section][key]
		except:
			return [False, None]

		return [True, value]

	def set(self, section : str, key : str, value):

		try:
			self.cfgs.add_section(section)
		except configparser.DuplicateSectionError:
			pass

		self.cfgs.set(section, key, value)

	def save(self):
		with open(self.cfgFile, 'w') as c:
			self.cfgs.write(c)

	def load(self):
		self.cfgs.read(self.cfgFile)