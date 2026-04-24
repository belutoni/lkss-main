:orphan:

.. _linux-infrastructure:

Preparing the environment (Linux)
=================================

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

After cloning the repository and installing the system packages, we need
to install some additional python packages.

.. note::

   It is recommended that you install the python packages in a virtual
   environment. If you already have one then please make sure to source
   it before proceeding. Otherwise:

   .. code-block:: bash

      # create the virtual environment
      python3 -m venv ./.venv

      # activate the virtual environment
      source ./.venv/bin/activate

To install the python packages:

.. code-block:: bash

   pip install -r requirements.txt

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

3. Create and source the python virtual environment (recommended):

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
