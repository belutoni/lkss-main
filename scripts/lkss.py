#!/bin/python3

# Copyright 2026 NXP
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import subprocess
import shutil
import sys
import shlex

from lkss_manifest import LKSSManifest
from lkss_util import LKSSUtil, LKSSDocker, LKSSConfig
from lkss_env import LKSS_ENV

def compile_docker(command: str, kernel: str, image: str,
					dtb: str, output: str, clean_config: bool):
	if not LKSSDocker.start():
		print("Failed to start docker container")
		return

	# set the configuration if need be
	if clean_config:
		LKSSDocker.run(command + LKSS_ENV["DEFCONFIG_NAME"], oneshot=False)

	# build the kernel
	LKSSDocker.run(command, oneshot=False)

	# done with docker - shut it down
	LKSSDocker.shutdown()

	# done, create output directory and copy Image/DTB
	if not os.path.isdir(output):
		os.makedirs(output)

	shutil.copy(image, output)
	shutil.copy(dtb, output)

def compile_native(command: str, kernel: str, image: str,
					dtb: str, output: str, clean_config: bool):
	# set the configuration if need be
	if clean_config:
		proc = subprocess.run(shlex.split(command + LKSS_ENV["DEFCONFIG_NAME"]))
		if proc.returncode != 0:
			print("Failed to set configuration")
			return

	# build the kernel
	proc = subprocess.run(shlex.split(command))
	if proc.returncode != 0:
		print("Failed to build the kernel")
		return

	# done, copy resulting image and DTB to output directory
	if not os.path.isdir(output):
		os.makedirs(output)

	shutil.copy(image, output)
	shutil.copy(dtb, output)

def menuconfig_docker(command: str, clean_config: bool):
	if not LKSSDocker.start():
		print("Failed to start docker container")
		return

	if clean_config:
		LKSSDocker.run(command + LKSS_ENV["DEFCONFIG_NAME"], oneshot=False)

	# open the menuconfig interface
	LKSSDocker.run(command + "menuconfig", oneshot=False)

	# done with docker - shut it down
	LKSSDocker.shutdown()

def menuconfig_native(command: str, clean_config: bool):
	# set the configuration if need be
	if clean_config:
		proc = subprocess.run(shlex.split(command + LKSS_ENV["DEFCONFIG_NAME"]))
		if proc.returncode != 0:
			print("Failed to set configuration")
			return

	# open the menuconfig interface
	proc = subprocess.run(shlex.split(command + "menuconfig"))
	if proc.returncode != 0:
		print("Failed to open menuconfig")
		return

def do_menuconfig(clean_config: bool):
	if not LKSSConfig.exists():
		print("No configuration file found - have you run init?")
		return

	kernel = os.path.join(LKSS_ENV["REPOS_DIR"], LKSS_ENV["LINUX_DIR"])
	command = f"make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -C {kernel} "
	env = LKSSConfig.load().data["env"]

	if env == "docker":
		menuconfig_docker(command, clean_config)
	else:
		menuconfig_native(command, clean_config)


def do_compile(jobs: int, install_modules: bool, clean_config: bool):
	if not LKSSConfig.exists():
		print("No configuration file found - have you run init?")
		return

	kernel = os.path.join(LKSS_ENV["REPOS_DIR"], LKSS_ENV["LINUX_DIR"])
	image = os.path.join(kernel, "arch/arm64/boot/Image")
	dtb = os.path.join(kernel, "arch/arm64/boot/dts/freescale", LKSS_ENV["DTB_NAME"])
	env = LKSSConfig.load().data["env"]

	command = f"make ARCH=arm64 CROSS_COMPILE=aarch64-linux-gnu- -C {kernel} "

	if jobs:
		command += f"-j{jobs} "

	if env == "docker":
		compile_docker(command, kernel, image, dtb, LKSS_ENV["OUTPUT_DIR"], clean_config)
	else:
		compile_native(command, kernel, image, dtb, LKSS_ENV["OUTPUT_DIR"], clean_config)

	if install_modules:
		do_modules_install()

def do_boot():
	bin_path = os.path.join(os.getcwd(), LKSS_ENV["BINARIES_DIR"])
	output_path = os.path.join(os.getcwd(), LKSS_ENV["OUTPUT_DIR"])

	# assemble paths for all required binaries
	rootfs = os.path.join(bin_path, LKSS_ENV["ROOTFS_NAME"])
	image = os.path.join(output_path, "Image")
	dtb = os.path.join(output_path, LKSS_ENV["DTB_NAME"])
	container = os.path.join(bin_path, LKSS_ENV["BOOT_CONTAINER_NAME"])
	script = LKSS_ENV["BOOT_SCRIPT_PATH"]

	if LKSSUtil.platform_name() == "WSL":
		uuu = os.path.join(bin_path, LKSS_ENV["WINDOWS_UUU_NAME"])
	else:
		uuu = os.path.join(bin_path, LKSS_ENV["UNIX_UUU_NAME"])

	binaries = [rootfs, image, dtb, container, script, uuu]

	for binary in binaries:
		if not os.path.isfile(binary):
			print(f"{binary} not present - have you ran init?")
			return

	# uuu binary might not have X bit set, do it now
	LKSSUtil.set_executable(uuu)

	print(f"Booting the board using {script}")

	command = [uuu, "-b", script, container, rootfs, image, dtb]

	proc = subprocess.run(command)
	if proc.returncode != 0:
		print("Failed to boot the board")
		return

def do_copy(src_fpath: str, dst_fpath: str):
	rootfs = os.path.join(os.getcwd(), LKSS_ENV["BINARIES_DIR"], LKSS_ENV["ROOTFS_NAME"])
	LKSSUtil.copy_to_rootfs(rootfs, src_fpath, dst_fpath)

def do_modules_install():
	kernel = os.path.join(os.getcwd(), LKSS_ENV["REPOS_DIR"], LKSS_ENV["LINUX_DIR"])
	rootfs = os.path.join(os.getcwd(), LKSS_ENV["BINARIES_DIR"], LKSS_ENV["ROOTFS_NAME"])
	mount = os.path.join(os.getcwd(), LKSS_ENV["ROOTFS_MOUNT_DIR"])

	if not LKSSUtil.mount_rootfs(rootfs, mount):
		print("Failed to mount rootfs")
		return

	command = ["sudo", f"INSTALL_MOD_PATH={mount}", "make", "modules_install"]

	proc = subprocess.run(command, cwd=kernel)
	if proc.returncode != 0:
		print("Failed to install modules")

	LKSSUtil.unmount_rootfs(mount)

def do_init(env: str, force: bool):
	if LKSSConfig.exists() and not force:
		print("Environment already initialized!")
		return

	LKSSManifest().init()

	if env == "docker":
		LKSSDocker.build()

	config = LKSSConfig()
	config.data["env"] = env
	config.store()

if LKSSUtil.platform_name() == "WINDOWS":
	print("Native Windows not supported - please run in WSL")
	sys.exit(1)

parser = argparse.ArgumentParser(description="LKSS utility tool")
subparser = parser.add_subparsers(dest="command",
								title="commands",
								help="command to execute")

init_parser = subparser.add_parser("init", help="initialize the development environment")
init_parser.add_argument("-e", "--environment", type=str, choices=["native", "docker"],
						default="native", help="environment to use for development")
init_parser.add_argument("-f", "--force", action="store_true", help="force the initialization")

subparser.add_parser("update", help="update the repositories/binaries")
subparser.add_parser("boot", help="boot the board")

compile_parser = subparser.add_parser("compile", help="compile the Linux kernel")
compile_parser.add_argument("-j", "--jobs", default=0,
							type=int,
							help="number of threads to use (see make -j argument)")
compile_parser.add_argument("--install-modules", action="store_true",
							help="copy the kernel modules to rootfs")
compile_parser.add_argument("--clean-config", action="store_true",
							help="set the configuration options to the defconfig values")

copy_parser = subparser.add_parser("copy", help="copy file or directory (recursively) to rootfs")
copy_parser.add_argument("src", type=str, help="source file or directory")
copy_parser.add_argument("dst", type=str,
						help="destination file or directory (relative to rootfs)")

menucfg_parser = subparser.add_parser("menuconfig", help="open the menuconfig interface")
menucfg_parser.add_argument("--clean-config", action="store_true",
							help="set the configuration options to the defconfig values")

args = parser.parse_args()

match args.command:
	case "init":
		do_init(args.environment, args.force)
	case "update":
		LKSSManifest().update()
	case "compile":
		do_compile(args.jobs, args.install_modules, args.clean_config)
	case "boot":
		do_boot()
	case "copy":
		do_copy(args.src, args.dst)
	case "menuconfig":
		do_menuconfig(args.clean_config)
