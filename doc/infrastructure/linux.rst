:orphan:

.. _linux-infrastructure:

Preparing the environment (Linux)
=================================

.. contents::
   :depth: 2
   :local:

About
-----

This page describes the steps required for setting up the development infrastructure
on a Linux-based machine.

.. warning::

   It is assumed that you're using the `apt`_ package manager, which is shipped
   with Debian-based distributions.

Prerequisites
-------------

Before getting started, make sure that you have a machine running Ubuntu [#]_ [#]_
natively. Regardless of the chosen environment (native or docker), we're going to
have to install some packages before proceeding. To do so, run:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y git minicom python3-venv python3 python3-pip

Cloning the repository
----------------------

To clone the project repository:

.. code-block:: bash

   git clone https://github.com/NXP-Research/lkss-main && cd lkss-main

Preparing the python environment
--------------------------------

Since the utility scripts are based on python, we're going to have to
prepare the python environment before proceeding. First, we'll have to
create a virtual environment. If you already have one, then make sure
to activate it before proceeding. Otherwise:

.. code-block:: bash

   # create the virtual environment
   python3 -m venv ./.venv

   # activate the virtual environment
   source ./.venv/bin/activate

.. warning::

   Make sure you always activate the virtual environment after opening a
   new terminal session.

After activating the environment, your bash prompt should look like this:

.. code-block:: text

   (.venv) lmc@playground:~/work/repos/lkss-main$

With this out of the way, we can now install the required python packages:

.. code-block:: bash

   pip install -r requirements.txt

Native development
------------------

Prerequisites
~~~~~~~~~~~~~

For native development, we're going to require a few more packages, which
can be installed by running:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y build-essential libncurses-dev bc \
                           flex bison libssl-dev \
                           libelf-dev gcc-aarch64-linux-gnu

Native environment initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With all of the necessary packages installed, we can now move on to the
next step, which is to initialize the environment for native development.
To do so, run:

.. code-block:: bash

   ./scripts/lkss.py init --runner native -f

If all commands issued so far have returned successfully, your environment
should now be prepared for native development.

Summary
~~~~~~~

1. Install the system packages:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y build-essential libncurses-dev bc \
                           flex bison libssl-dev \
                           libelf-dev gcc-aarch64-linux-gnu \
		           git minicom python3-venv python3 python3-pip


2. Clone the repository:

.. code-block:: bash

   git clone https://github.com/NXP-Research/lkss-main && cd lkss-main

3. Create and activate the python virtual environment (recommended):

.. code-block:: bash

   python3 -m venv ./.venv && source ./.venv/bin/activate

4. Install the python packages:

.. code-block:: bash

   pip install -r requirements.txt

5. Initialize the environment:

.. code-block:: bash

   ./scripts/lkss.py init --runner native -f

Docker development
------------------

Prerequisites
~~~~~~~~~~~~~

To get started, we're going to have to install `Docker`_. To do so, follow
`these instructions <https://docs.docker.com/engine/install/ubuntu/>`__.

.. warning::

   Make sure you also install **docker-compose-plugin**. This package should
   already be covered by the instructions linked above.

To make sure everything went smoothly with the installation, you can try to
run the **hello-world** Docker image as indicated by the documentation:

.. code-block:: bash

   sudo docker run hello-world

Docker environment initialization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

With Docker installed, we can now proceed with the environment initialization:

.. code-block:: bash

   ./scripts/lkss.py init --runner docker -f

.. warning::

   If you get an error similar to:

   .. code-block:: text

      docker permission denied while trying to connect to the docker API at unix:///var/run/docker.sock

   during the initialization, please make sure you follow the steps described
   `here <https://docs.docker.com/engine/install/linux-postinstall/>`__ to
   add your user to the **docker** group.

   To test if the changes were successful, you can run:

   .. code-block:: bash

      id -nG

   You should see the **docker** group being listed there.

   You may need to restart your computer if the changes don't take effect
   after logging out and logging back in.

If all commands issued so far have returned successfully, your environment
should now be prepared for Docker development.

Summary
~~~~~~~

1. Install the system packages:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install -y git minicom python3-venv python3 python3-pip


2. Clone the repository:

.. code-block:: bash

   git clone https://github.com/NXP-Research/lkss-main && cd lkss-main

3. Create and activate the python virtual environment (recommended):

.. code-block:: bash

   python3 -m venv ./.venv && source ./.venv/bin/activate

4. Install the python packages:

.. code-block:: bash

   pip install -r requirements.txt

5. Install Docker by following the steps from `here <https://docs.docker.com/engine/install/ubuntu/>`__.

6. Initialize the environment:

.. code-block:: bash

   ./scripts/lkss.py init --runner docker -f


Testing the environment
-----------------------

To make sure that your environment was properly initialized, you can try
compiling the kernel. To do so, run:

.. code-block:: bash

   ./scripts/lkss.py compile -j$(nproc) --clean-config

.. rubric:: Footnotes

.. [#] Or any other Debian-based distribution **should** work.

.. [#] The version shouldn't matter but, ideally, it should be a newer one.

.. _apt: https://en.wikipedia.org/wiki/APT_(software)
.. _Docker: https://www.docker.com/
