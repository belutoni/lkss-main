# Copyright 2026 NXP
#
# SPDX-License-Identifier: Apache-2.0

"""Contains classes defining various utility functions"""

import platform
import os
import stat
import subprocess
import shutil
import pickle
import shlex

class LKSSUtil:
	@staticmethod
	def platform_name() -> str:
		"""Get the normalized name of the platform."""
		if "WSL" in platform.uname().release.upper():
			return "WSL"

		return platform.system().upper()

	@staticmethod
	def set_executable(fpath: str):
		"""Set the executable bit for a given file"""
		if not os.access(fpath, os.X_OK):
			os.chmod(fpath, os.stat(fpath).st_mode | stat.S_IEXEC)

	@staticmethod
	def mount_rootfs(rootfs_fpath: str, mount_fpath: str) -> bool:
		# make sure mount point's created
		if not os.path.isdir(mount_fpath):
			os.makedirs(mount_fpath)

		command = ["sudo", "mount", rootfs_fpath, mount_fpath]

		proc = subprocess.run(command)
		if proc.returncode != 0:
			LKSSUtil.__remove_file(mount_fpath)
			return False

		return True

	@staticmethod
	def unmount_rootfs(mount_fpath: str) -> bool:
		command = ["sudo", "umount", mount_fpath]

		proc = subprocess.run(command)
		if proc.returncode != 0:
			return False

		LKSSUtil.__remove_file(mount_fpath)

		return True

	@staticmethod
	def __remove_file(fpath: str):
		command = ["sudo", "rm", "-r", fpath]

		proc = subprocess.run(command)
		if proc.returncode != 0:
			print(f"Failed to remove {fpath}")
			return

	@staticmethod
	def __copy_file(src: str, dst: str):
		command = ["sudo", "cp", "-r", src, dst]

		proc = subprocess.run(command)
		if proc.returncode != 0:
			print(f"Failed to copy {src} to {dst}")
			return

	@staticmethod
	def copy_to_rootfs(mount: str, rootfs_fpath: str, src_fpath: str, dst_fpath: str):
		dst = os.path.join(mount, dst_fpath.lstrip("/"))

		print(f"Attempting to recursively copy {src_fpath} to {dst}")

		if not LKSSUtil.mount_rootfs(rootfs_fpath, mount):
			print("Failed to mount rootfs")
			return

		LKSSUtil.__copy_file(src_fpath, dst)

		if not LKSSUtil.unmount_rootfs(mount):
			print("Failed to unmount rootfs")
			return
