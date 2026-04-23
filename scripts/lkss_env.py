# Copyright 2026 NXP
#
# SPDX-License-Identifier: Apache-2.0

import os
import dotenv
import pickle

from dotenv import dotenv_values

class LKSSEnvironment:
	DEFCONFIG = "./configs/defconfig"
	CACHE = ".lkss"

	def __init__(self):
		# was the environment cached?
		if not os.path.isfile(LKSSEnvironment.CACHE):
			self.data = dict()
			return

		# yes, load it
		with open(LKSSEnvironment.CACHE, "rb") as fd:
			self.data = pickle.load(fd)

	def load_from_config(self, config: str):
		if not config:
			config = LKSSEnvironment.DEFCONFIG

		if not os.path.isfile(config):
			raise FileNotFoundError(f"File {config} not found")

		print(f"Using {config} to initialize environment...")

		self.data = dotenv_values(config)

	def store(self):
		with open(LKSSEnvironment.CACHE, "wb") as fd:
			pickle.dump(self.data, fd)

	def getvar(self, key: str):
		return self.data[key]

	@staticmethod
	def is_cached():
		return os.path.isfile(LKSSEnvironment.CACHE)

env = LKSSEnvironment()
