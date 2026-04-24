# Copyright 2026 NXP
#
# SPDX-License-Identifier: Apache-2.0

import subprocess
import requests
import os
import yaml

import lkss_util

from lkss_env import env as lkss_env

class LKSSRepository:
	@staticmethod
	def __is_repo(path: str):
		return os.path.isdir(path) and os.path.isdir(os.path.join(path, ".git"))

	@staticmethod
	def __do_clone(remote: str, path: str, depth, branch):
		command = ["git", "clone", f"{remote}", f"{path}"]

		if depth:
			command += [f"--depth={depth}", "--no-single-branch"]

		if branch:
			command += ["-b", f"{branch}"]

		proc = subprocess.run(command)
		if proc.returncode != 0:
			print("Failed to clone {}".format(remote))

	@staticmethod
	def clone(repo: dict, prefix: str):
		url = repo["remote"] + "/" + repo["name"]

		if "alias" in repo:
			repo_name = repo["alias"]
		else:
			repo_name = repo["name"]

		path = os.path.join(os.getcwd(), prefix, repo_name)

		if "depth" in repo:
			depth = repo["depth"]
		else:
			depth = 0

		if "branch" in repo:
			branch = repo["branch"]
		else:
			branch = None

		if not LKSSRepository.__is_repo(path):
			LKSSRepository.__do_clone(url, path, depth, branch)
		else:
			print("{} already cloned - skip".format(repo["name"]))

	@staticmethod
	def __head_info(path: str) -> tuple():
		# get HEAD commit title
		command = ["git", "show", "-s", "--format=%s", "HEAD"]

		proc = subprocess.run(command, cwd=path, capture_output=True)
		if proc.returncode != 0:
			print("Failed to get HEAD commit title")
			return None

		title = proc.stdout.strip().decode("utf-8")

		# get HEAD commit SHA
		command = ["git", "show", "-s", "--format=%H", "HEAD"]

		proc = subprocess.run(command, cwd=path, capture_output=True)
		if proc.returncode != 0:
			print("Failed to get HEAD commit SHA")
			return None

		sha = proc.stdout.strip().decode("utf-8")

		return (title, sha[:12])

	@staticmethod
	def __fetch_and_checkout(path: str, branch: str) -> tuple():
		command = ["git", "fetch", "origin"]

		proc = subprocess.run(command, cwd=path, stdout=subprocess.DEVNULL)
		if proc.returncode != 0:
			print("Failed to fetch")
			return False

		command = ["git", "checkout", f"origin/{branch}"]

		proc = subprocess.run(command, cwd=path, stdout=subprocess.DEVNULL)
		if proc.returncode != 0:
			print("Failed to checkout")
			return False

		return True

	@staticmethod
	def update(repo: dict, prefix: str):

		if "alias" in repo:
			path = os.path.join(os.getcwd(), prefix, repo["alias"])
		else:
			path = os.path.join(os.getcwd(), prefix, repo["name"])

		if not LKSSRepository.__is_repo(path):
			print("{} not cloned - have you ran init?".format(repo["name"]))
			return

		print("Updating {}...".format(repo["name"]))

		head_info = LKSSRepository.__head_info(path)
		if head_info is None:
			print("Failed to get HEAD info")
			return

		print("Leaving HEAD {} {}".format(head_info[1], head_info[0]))

		if not LKSSRepository.__fetch_and_checkout(path, repo["branch"]):
			print("Failed to fetch/checkout to latest {}".format(repo["branch"]))
			return

class LKSSBinary:
	# does the variant match the development environment?
	@staticmethod
	def variant_matches(variant: dict):
		return variant["platform"].upper() == lkss_util.platform_name()

	@staticmethod
	def get_url(binary: dict):
		if "tag" not in binary or binary["tag"] == "latest":
			return binary["remote"] + "/releases/latest/download/"
		else:
			return binary["remote"] + "/releases/download/" + binary["tag"] + "/"

	# returns a tuple with format (local_name, remote_name) or None if
	# unsuccessful.
	@staticmethod
	def get_variant(binary: dict) -> tuple():
		# name takes precedence over variants - these properties should be
		# mutually exclusive, really
		if "name" in binary:
			if "alias" in binary:
				return (binary["alias"], binary["name"])

			return (binary["name"], binary["name"])

		# name not specified - fall back to 'variants'
		if "variants" not in binary:
			return None

		# ok, all good - look through the variants and find the one
		# matching the development environment
		for variant in binary["variants"]:
			if LKSSBinary.variant_matches(variant):
				# aliased?
				if "alias" in variant:
					return (variant["alias"], variant["name"])
				else:
					return (variant["name"], variant["name"])

		# no match at this point
		return None

	@staticmethod
	def download(binary: dict, prefix: str, allow_overwrite=False):
		variant  = LKSSBinary.get_variant(binary)
		if variant is None:
			print("No eligible variant found - abort")
			return

		url = LKSSBinary.get_url(binary) + variant[1]
		path = os.path.join(os.getcwd(), prefix, variant[0])

		if os.path.isfile(path) and not allow_overwrite:
			print("{} already downloaded - skip".format(variant[0]))
			return

		# might have to create the directory otherwise open() will
		# fail
		if not os.path.isdir(os.path.join(os.getcwd(), prefix)):
			os.makedirs(os.path.join(os.getcwd(), prefix))

		print("Downloading {}".format(url))

		# no, clone it now
		r = requests.get(url)

		with open(path, "wb") as fd:
			fd.write(r.content)

	@staticmethod
	def update(binary: dict, prefix: str):
		return LKSSBinary.download(binary, prefix, True)

class LKSSManifest:
	def __init__(self):
		with open(lkss_env.data["MANIFEST_FILE"]) as fd:
			raw_content = fd.read()

			# before loading the YAML file, we need to perform a fixup
			# meaning we replace all the environment variables with the
			# corresponding values from the environment

			for var, val in lkss_env.data.items():
				raw_content = raw_content.replace(f"${var}", f"{val}")

			self.content = yaml.safe_load(raw_content)

	def init(self):
		if self.content is None:
			print("Empty manifest file - skip init")
			return

		if "repositories" in self.content and self.content["repositories"] is not None:
			for repo in self.content["repositories"]:
				LKSSRepository.clone(repo, lkss_env.data["REPOS_DIR"])
		else:
			print("No repositories in manifest file - skip init")

		if "binaries" in self.content and self.content["binaries"] is not None:
			for binary in self.content["binaries"]:
				LKSSBinary.download(binary, lkss_env.data["BINARIES_DIR"])
		else:
			print("No binaries in manifest file - skip init")

	def update(self):
		if self.content is None:
			print("Empty manifest file - skip update")
			return

		if "repositories" in self.content and self.content["repositories"] is not None:
			for repo in self.content["repositories"]:
				LKSSRepository.update(repo, lkss_env.data["REPOS_DIR"])
		else:
			print("No repositories in manifest file - skip update")


		if "binaries" in self.content and self.content["binaries"] is not None:
			print("Updating binaries will overwrite existing ones!")

			for binary in self.content["binaries"]:
				LKSSBinary.update(binary, lkss_env.data["BINARIES_DIR"])
		else:
			print("No binaries in manifest file - skip update")
