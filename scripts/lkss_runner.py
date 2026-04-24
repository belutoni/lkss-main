# Copyright 2026 NXP
#
# SPDX-License-Identifier: Apache-2.0

import os
import subprocess
import shlex
import shutil

from abc import ABC, abstractmethod

from lkss_env import env as lkss_env

class LKSSRunner(ABC):
	@abstractmethod
	def setup(self):
		pass

	@abstractmethod
	def start(self):
		pass

	@abstractmethod
	def shutdown(self):
		pass

	@abstractmethod
	def run(self, command: str, oneshot=True):
		pass

	@abstractmethod
	def run_batch(self, commands: list, oneshot=True):
		pass

class LKSSNativeRunner(LKSSRunner):
	def setup(self):
		# running in native environment requires no setup steps
		print("Setting up the native runner...")

	def start(self):
		# native runner is always started
		pass

	def shutdown(self):
		# can't shutdown the native runner
		pass

	def run(self, command: str, oneshot=True):
		proc = subprocess.run(shlex.split(command))
		if proc.returncode != 0:
			raise RuntimeError(f"Failed to run: {command}")

	def run_batch(self, commands: list, oneshot=True):
		for command in commands:
			self.run(command)

class LKSSDockerRunner(LKSSRunner):
	COMPOSE = "./docker/compose.yaml"
	SERVICE_NAME = "lkss"

	def setup(self):
		uid = os.getuid()
		gid = os.getgid()

		# was docker installed?
		if not shutil.which("docker"):
			raise RuntimeError("Unable to find docker - please install it")

		command = f"docker compose -f {LKSSDockerRunner.COMPOSE} " +\
			f"build --build-arg UID={uid} --build-arg GID={gid}"

		print("Setting up the docker runner...")

		proc = subprocess.run(shlex.split(command))
		if proc.returncode != 0:
			raise RuntimeError(f"Failed to build the docker image")

	def start(self):
		command = f"docker compose -f {LKSSDockerRunner.COMPOSE} up --detach"

		proc = subprocess.run(shlex.split(command))
		if proc.returncode != 0:
			raise RuntimeError(f"Failed to start the docker container")

	def shutdown(self):
		command = f"docker compose -f {LKSSDockerRunner.COMPOSE} down"

		proc = subprocess.run(shlex.split(command))
		if proc.returncode != 0:
			raise RuntimeError(f"Failed to shutdown the docker container")

	def run(self, command: str, oneshot=True):
		if oneshot:
			self.start()

		command = ["docker", "compose", "-f", LKSSDockerRunner.COMPOSE,
			"exec", LKSSDockerRunner.SERVICE_NAME, "bash", "-c", f"{command}"]

		proc = subprocess.run(command)
		if proc.returncode != 0:
			if oneshot:
				self.shutdown()

			raise RuntimeError(f"Failed to run: {command}")

		if oneshot:
			self.shutdown()

	def run_batch(self, commands: str, oneshot=True):
		if oneshot:
			self.start()

		try:
			for command in commands:
				# always force oneshot to false - we want to
				# avoid starting and shutting down the container
				# on each command
				self.run(command, False)
		finally:
			if oneshot:
				self.shutdown()

def lkss_get_runner(runner: str):
	match runner:
		case "native":
			return LKSSNativeRunner()
		case "docker":
			return LKSSDockerRunner()
		case _:
			raise RuntimeError(f"Unknown runner type: {runner}")
