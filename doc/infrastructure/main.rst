.. _infrastructure:

Preparing the environment
=========================

Supported environments
----------------------

:numref:`infrastructure-supported-env-list` provides the list of supported development
environments [#]_.

.. _infrastructure-supported-env-list:

.. list-table:: List of supported environments
   :header-rows: 1
   :widths: 30 30 30 30 30 30
   :align: center

   * - Operating System
     - Architecture
     - Native
     - Docker
     - Setup steps
     - Notes

   * - Linux
     - x86
     - ✅
     - ✅
     - See :ref:`here <linux-infrastructure>`
     - N/A

   * - Windows
     - x86
     - ✅
     - ✅
     - See :ref:`here <windows-infrastructure>`
     - Through WSL only

   * - MacOS
     - x86, ARM64
     - ❌
     - ❌
     - N/A
     - N/A

Virtualized environments
------------------------

Due to many USB-related issues occuring during the board boot process,
support for virtualized environments (WSL not included) has been completely
dropped. However, if you **must** use a virtualized environment, please contact
the :ref:`team <team>` before the event starts so that we can find a solution.

.. rubric:: Footnotes

.. [#] Environments not present in this list are considered unsupported.
