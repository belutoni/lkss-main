lkss.py
=======

About
-----

**lkss.py** is a Python-based tool meant to help speed up the development process
and attempt to minimize the time spent debugging infrastructure-related issues.
That being said, this tool can be viewed as a simple wrapper over a set of commands
that would normally have to be issued manually.

To print more information regarding this tool and the commands/options it supports, run:

.. code-block:: bash

   ./scripts/lkss.py --help

You can also print more information about a specific command by running:

.. code-block:: bash

   # replace COMMAND with the command you're interested in (e.g. init, boot, etc..)
   ./scripts/lkss.py [COMMAND] --help

For example:

.. code-block:: bash

   ./scripts/lkss.py init --help

would print information about the **init** command.

The init command
----------------

This command is used to prepare the development environment. Among other things, this
command clones/downloads the repositories/binaries described in the **manifest file** [#]_
and initializes the **runner** [#]_.

.. warning::

   This command is only meant be run **once**. If you wish to run it a second time
   (e.g. to change the runner or configuration file), you'll need to use the ``-f``
   option:

   .. code-block:: bash

      ./scripts/lkss.py init -f

   Otherwise, you'll get the following error:

   .. code-block:: text

      Environment already initialized!

   You should also use the ``-f`` option if the command failed the first time.

Choosing a runner
~~~~~~~~~~~~~~~~~

To prepare the development environment, run:

.. code-block:: bash

   ./scripts/lkss.py init

This will initialize the environment for **native development**. You can choose between
the available runners using the ``--runner`` option:

.. code-block:: bash

   # replace RUNNER with your desired runner
   ./scripts/lkss.py init --runner [RUNNER]

For example:

.. code-block:: bash

   ./scripts/lkss.py init --runner docker

would initialize the environment for **docker development**.

Choosing a configuration file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If need be, you can also specify which configuration file to use. To do so, run:

.. code-block:: bash

   ./scripts/lkss.py init --config path/to/your/config

If ``--config`` is omitted, **./configs/defconfig** will be used.

The compile command
-------------------

This command is used to compile the Linux kernel. Its basic usage is:

.. code-block:: bash

   ./scripts/lkss.py compile

.. warning::

   If you're compiling the Linux kernel for the first time, you'll also have to specify
   the ``--clean-config`` flag:

   .. code-block:: bash

      ./scripts/lkss.py compile --clean-config

   Otherwise, you'll get the following error:

   .. code-block:: text

      Kernel configuration not set - please run using the --clean-config flag


To set the number of threads to use for the compilation, you can use the ``-j`` option:

.. code-block:: bash

   # replace THREADS with the number of threads to use
   ./scripts/lkss.py compile -j [THREADS]

If ``-j`` is omitted, only one thread will be used.

Most of the times, you'll also want to copy the resulting kernel modules to the rootfs.
To do so, you can use the ``--install-modules`` options:

.. code-block:: bash

   ./scripts/lkss.py compile --install-modules

The boot command
----------------

This command is used to boot the board. Its basic usage is:

.. code-blocK:: bash

   ./scripts/lkss.py boot

.. warning::

   Make sure to compile the Linux kernel before using this command. Otherwise, you'll
   get this error:

   .. code-block:: text

      /home/lmc/work/repos/lkss-main/output/Image not found

The update command
------------------

This command is used to update the repositories and binaries to the latest version,
as specified in the manifest file. Its basic usage is:

.. code-block:: bash

   ./scripts/lkss.py update

.. warning::

   This command will overwrite your binaries (e.g. rootfs) and will place your git
   repositories in a detached HEAD state!

   For repositories, if you wish to save your changes:

   .. code-block:: bash

      # add all files to staged area
      git add .

      # commit the changes
      git commit -s

      # save changes to a separate branch
      git switch -c my-amazing-branch

The copy command
----------------

This command is used to copy a file or a directory (recursively) to the rootfs. Its
basic usage is:

.. code-block:: bash

   # LOCAL_SRC - path to the file or directory you wish to copy from your local filesystem
   # ROOTFS_DTS - path relative to rootfs where you wish to copy your local file or directory
   ./scripts/lkss.py copy [LOCAL_SRC] [ROOTFS_DST]

For example:

.. code-block:: bash

   ./scripts/lkss.py copy ./lkss.yaml /lib/

will copy **lkss.yaml** to **/lib/** inside the rootfs.

.. _lkss_cheatsheet:

Cheatsheet
----------

**Initialize the environment for native development:**

.. code-block:: bash

   ./scripts/lkss.py init --runner native -f

**Initialize the environment for docker development:**

.. code-block:: bash

   ./scripts/lkss.py init --runner docker -f

**First Linux kernel compilation:**

.. code-block:: bash

   ./scripts/lkss.py compile --install-modules --clean-config -j$(nproc)

**Subsequent Linux kernel compilations:**

.. code-block:: bash

   ./scripts/lkss.py compile --install-modules -j$(nproc)

**Boot the board:**

.. code-block:: bash

   ./scripts/lkss.py boot

**Update repositories/binaries**:

.. code-block:: bash

   ./scripts/lkss.py update

**Open the menuconfig interface**:

.. code-block:: bash

   ./scripts/lkss.py menuconfig

.. rubric:: Footnotes

.. [#] This is a file containing a list of repositories/binaries, each with
       information such as where to clone/download them from, which branch/tag
       to use, etc...

.. [#] This refers to the environment you'll be using for development. For instance,
       if the docker runner is selected, you'll be compiling the Linux kernel inside
       a docker container. Otherwise, if native runner is selected, the compilation will
       happen directly on your machine.
