# Roman Attribute Dictionary

[![CI](https://github.com/spacetelescope/rad/actions/workflows/ci.yml/badge.svg)](https://github.com/spacetelescope/rad/actions/workflows/ci.yml) [![Documentation Status](https://readthedocs.org/projects/rad/badge/?version=latest)](https://rad.readthedocs.io/en/latest/?badge=latest)
[![Powered by STScI Badge](https://img.shields.io/badge/powered%20by-STScI-blue.svg?colorA=707170&colorB=3e8ddd&style=flat)](http://www.stsci.edu)


This is a repository for the Roman Attribute Dictionary


## Installation

The easiest way to install the latest `rad` release into a fresh virtualenv or conda environment is

    pip install rad

### Detailed Installation

The `rad` package can be installed into a virtualenv or conda environment via `pip`. We recommend that for each
installation you start by creating a fresh environment that only has Python installed and then install the `rad`
package and its dependencies into that bare environment. If using conda environments, first make sure you have a recent
version of Anaconda or Miniconda installed. If desired, you can create multiple environments to allow for switching
between different versions of the `rad` package (e.g. a released version versus the current development version).

In all cases, the installation is generally a 3-step process:

* Create a conda environment
* Activate that environment
* Install the desired version of the `rad` package into that environment

Details are given below on how to do this for different types of installations, including tagged releases, DMS builds
used in operations, and development versions. Remember that all conda operations must be done from within a bash shell.

### Installing latest releases

You can install the latest released version via `pip`. From a bash shell:

    conda create -n <env_name> python
    conda activate <env_name>
    pip install rad

> **Note**\
> Alternatively, you can also use `virtualenv` to create an environment;
> however, this installation method is not supported by STScI if you encounter issues.

You can also install a specific version (from `rad 0.1.0` onward):

    conda create -n <env_name> python
    conda activate <env_name>
    pip install rad==0.5.0

### Installing the development version from Github

You can install the latest development version (not as well tested) from the Github main branch:

    conda create -n <env_name> python
    conda activate <env_name>
    pip install git+https://github.com/spacetelescope/rad

### Installing for Developers

If you want to be able to work on and test the source code with the `rad` package, the high-level procedure to do
this is to first create a conda environment using the same procedures outlined above, but then install your personal
copy of the code overtop of the original code in that environment. Again, this should be done in a separate conda
environment from any existing environments that you may have already installed with released versions of the `rad`
package.

As usual, the first two steps are to create and activate an environment:

    conda create -n <env_name> python
    conda activate <env_name>

To install your own copy of the code into that environment, you first need to fork and clone the `rad` repo:

    cd <where you want to put the repo>
    git clone https://github.com/spacetelescope/rad
    cd rad

> **Note**\
> Installing via `setup.py` (`python setup.py install`, `python setup.py develop`, etc.) is deprecated and does not work.

Install from your local checked-out copy as an "editable" install:

    pip install -e .

If you want to run the unit or regression tests and/or build the docs, you can make sure those dependencies are
installed too:

    pip install -e ".[test]"
    pip install -e ".[docs]"
    pip install -e ".[test,docs]"

Need other useful packages in your development environment?

    pip install ipython pytest-xdist
