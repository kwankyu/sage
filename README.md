<div>
<a href="https://sagemath.org">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="src/doc/common/static/logo_sagemath_white.svg">
    <img src="src/doc/common/static/logo_sagemath_black.svg" height="60" align="left">
  </picture>
</a>
   <em>"Creating a Viable Open Source Alternative to
   Magma, Maple, Mathematica, and MATLAB"</em>
</div>

#

Sage is open-source mathematical software released under
[the GNU General Public Licence GPLv3](https://www.gnu.org/licenses/gpl-3.0.html),
and includes a distribution of software packages that have
[compatible software licenses](./COPYING.txt).
[Many people around the globe](https://www.sagemath.org/development-map.html)
have contributed to the development of Sage. The full
[documentation](https://doc.sagemath.org/html/en/index.html) is available online.

Getting Started
---------------

Those who are impatient may use the prebuilt Sage available online

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/sagemath/sage-binder-env/master)

It takes some time to launch &mdash; be patient. Alternatively, if you are
comfortable with [docker](https://www.docker.com/), you may run the
prebuilt Sage just by executing
``` bash
docker run -it sagemath/sagemath
```
which pulls the docker image on dockerhub

[![Docker Status](http://dockeri.co/image/sagemath/sagemath)](https://hub.docker.com/r/sagemath/sagemath)

If you want to install Sage on your platform, there are several alternative
ways. The [Sage Installation Guide](https://doc.sagemath.org/html/en/installation/index.html)
provides a decision tree that guides you to the type of installation that will work best
for you. This includes building from source, obtaining Sage from a package
manager of your platform, [installing in conda environment]((https://doc.sagemath.org/html/en/installation/conda.html)),
using a container image with your docker, or using Sage in the cloud.

This **README** contains general instructions for building Sage from the source
code in the [GitHub git repository](https://github.com/sagemath/sage). If you
encounter any difficulties or need further explanations while following the
instructions below, please refer to the detailed guide in the section
[_Installation from Source_](https://doc.sagemath.org/html/en/installation/source.html)
of the Sage Installation Guide.

Instructions to Build from Source
---------------------------------

### Supported Platforms

Sage supports all major Linux distributions, recent versions of macOS, and
Windows through Windows Subsystem for Linux (WSL).  Detailed information on the
supported platforms for a specific version of Sage can be found in the section
[_Availability and installation help_](https://github.com/sagemath/sage/releases)
of the Release Tour for that version.

Instead of your local platform, you may use online free platforms

[![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/sagemath/sage/tree/master
) &nbsp; [![Open in GitHub Codespaces](https://img.shields.io/badge/Open_in_GitHub_Codespaces-black?logo=github)](https://codespaces.new/sagemath/sage/tree/master)

that automatically clones the git repository for you. There you may build Sage from
the source following the same instructions presented below.

For examples in this guide, we assume Ubuntu Linux distribution for convenience.

### Preparing the Windows Platform

You may install Sage on Windows using Windows Subsystem for
Linux (WSL). Follow the [official WSL guide](https://learn.microsoft.com/windows/wsl/)
to install Ubuntu or other Linux distribution into WSL. Then open the Linux terminal.
From this point on, all instructions for installation in Linux apply.

### Preparing the Linux Platform

Install the build prerequisites:

    sudo apt-get update
    sudo apt-get install autoconf automake libtool pkg-config

For your platform, there is a similar list of
[build prerequisites](https://doc.sagemath.org/html/en/reference/spkg/_bootstrap.html#equivalent-system-packages).
Install them using the package manager of your platform.

Sage depends on many system packages. Install them by executing

    sudo apt-get install bc binutils bzip2 ca-certificates cliquer cmake curl \
        ecl eclib-tools fflas-ffpack g++ gap gcc gengetopt gfan gfortran \
        glpk-utils gmp-ecm lcalc libatomic-ops-dev libboost-dev \
        libbraiding-dev libbrial-dev libbrial-groebner-dev libbz2-dev \
        libcdd-dev libcdd-tools libcliquer-dev libcurl4-openssl-dev libec-dev \
        libecm-dev libffi-dev libflint-dev libfplll-dev libfreetype-dev \
        libgap-dev libgc-dev libgd-dev libgf2x-dev libgiac-dev libgivaro-dev \
        libglpk-dev libgmp-dev libgsl-dev libhomfly-dev libiml-dev \
        liblfunction-dev liblinbox-dev liblrcalc-dev liblzma-dev libm4ri-dev \
        libm4rie-dev libmpc-dev libmpfi-dev libmpfr-dev libncurses5-dev \
        libntl-dev libopenblas-dev libpari-dev libplanarity-dev libppl-dev \
        libprimesieve-dev libpython3-dev libqhull-dev \
        libreadline-dev librw-dev libsingular4-dev libsqlite3-dev libssl-dev \
        libsuitesparse-dev libsymmetrica2-dev zlib1g-dev libzmq3-dev m4 make \
        maxima maxima-sage meson nauty ninja-build openssl palp pari-doc \
        pari-elldata pari-galdata pari-galpol pari-gp2c pari-seadata patch \
        patchelf perl pkg-config planarity ppl-dev python3 python3-setuptools \
        python3-venv qhull-bin singular singular-doc sqlite3 sympow tachyon \
        tar texinfo tox xcas xz-utils

If you encounter error messages like "Unable to locate package ...", don't be
panic. Just delete the problematic package names in the list, and rerun the
command. Sage will automatically install a package from its own mirrors if it
is not found in the system.

This will take a while. For your platform, refer to
[the lists of system packages](https://doc.sagemath.org/html/en/installation/source#linux-system-package-installation).

### Preparing the macOS Platform

To build Sage on macOS, You have to use
[Homebrew](https://brew.sh/) ("the missing package manager for macOS").
Installing Homebrew also accompanies installing [Xcode command line tools](https://developer.apple.com/xcode/),
which contain the compiler and library suites necessary to build software from source on mac.

To check if Xcode command line tools are installed, open a terminal window and
run `xcode-select --install`. If a pop-up window opens, click "Install" to
install it. If it is already installed, you will see a message that says so.

Using Homebrew, install the build prerequisites:

    brew install autoconf automake libtool pkg-config

and also install [the system packages](https://doc.sagemath.org/html/en/installation/source#macos-package-installation)
that Sage depends. There are many packages to install. It will take a while.

### Cloning Sage git repository

We will clone the source git repository with `git`. To check that `git` is
available, open a terminal and enter the following command at the shell prompt
`$`:

    $ git --version
    git version 2.45.2

The exact version does not matter, but if this command gives an error,
install `git`:

    $ sudo apt-get install git

and configure it. Read the guide [_Setting Up Git_](https://doc.sagemath.org/html/en/developer/git_setup.html)
for more information.

We are ready to clone the Sage git repository. For online platforms like gitpod
and GitHub codespaces, the git repository is already cloned to
`/workspace/sage`, and you are in this directory after login.  On your local
platform, create a subdirectory `sage` of your home directory:

    $ mkdir ~/sage
    $ cd sage
    $ pwd
    .../sage

The full path `.../sage` must contain no spaces. Now run

    $ git clone -c core.symlinks=true --filter blob:none \
            --origin upstream --branch master https://github.com/sagemath/sage.git

This will create the subdirectory `sage` in the current directory `~/sage`.
Change into the directory:

    $ cd sage

Check if you are in the right directory that contains the cloned repository with:

    $ ls README.md
    README.md

Traditionally, this directory, where we build and run Sage, is called `SAGE_ROOT`.
Define the environment variable:

    $ SAGE_ROOT=~/sage/sage

When you build Sage or later install additional packages to Sage, it is
important that environment variables, including `SAGE_ROOT`, are
properly defined. If you are on macOS and using Hombrew, paths to some
Homebrew packages should be known to Sage's build scripts via environment
variables. These are defined in the file `SAGE_ROOT/.homebrew-build-env`.
Hence you must execute

    $ source $SAGE_ROOT/.homebrew-build-env  # only for macOS

Moreover be sure to add these lines

    SAGE_ROOT=~/sage/sage
    source $SAGE_ROOT/.homebrew-build-env    # only for macOS

to your shell's rc(run commands) file such as `~/.bashrc` or `~/.zshrc` so that
these environment variables are always defined when you open a new terminal.

### Building Sage from source

In the `SAGE_ROOT` directory, bootstrap the source tree:

    $ ./bootstrap

The source tree is now ready to be configured and built. Run

    $ ./configure

At the end, you will see some messages recommending to install some extra system
packages using your package manager. You may ignore them for now. In
fact, `./configure` can take many options, to configure the subsequent build
process.  If you are curious, run `./configure --help`.

Now let's build Sage!

    $ make

Building Sage may take a couple of hours even on a fast computer. If you
watched your computer busy logging lots of messages for a couple of minutes,
just leave your computer running and take a walk to breathe some fresh air.

If `make` finished with reporting the running time at the end, then
congratulations, Sage built successfully! Otherwise go to the
**Troubleshooting** section below.

### Running Sage

In the `SAGE_ROOT` directory, type `./sage` to try it
out. For example

    $ ./sage
    ...
    sage: nth_prime(100)
    541

Type <kbd>Ctrl</kbd>+<kbd>D</kbd> or `quit` to quit Sage.

If you want to be able to start Sage by typing `sage` anywhere, create a symlink to
the `SAGE_ROOT/sage` script in some directory, typically `/usr/local/bin`, specified in your
`PATH` environment variable. This can be done by

    $ sudo ln -s $SAGE_ROOT/sage /usr/local/bin

Many Sage users prefer the Jupyter notebook interface to the terminal
interface. The single command

    $ sage -i jupyterlab

installs and another

    $ sage -n jupyterlab

launches the JupyterLab. For more information, see the section
[_Launching SageMath_](https://doc.sagemath.org/html/en/installation/launching.html) of the
Sage Installation Guide.

The HTML version of the [documentation](https://doc.sagemath.org/html/en/index.html)
is built as part of the build process of Sage and resides in the directory
`SAGE_ROOT/local/share/doc/sage/html/en/`. You may want to bookmark it in your browser.

If you have questions using Sage, you can ask them in the [SageMath forum](https://ask.sagemath.org/questions/).

Troubleshooting
---------------

If you have problems building Sage, check the [Sage Installation Guide](https://doc.sagemath.org/html/en/installation/source.html),
as well as the installation help in the [Release Tour](https://github.com/sagemath/sage/releases) corresponding to the
version that you are installing.

Please do not hesitate to ask for help in the [sage-support mailing
list](https://groups.google.com/forum/#!forum/sage-support).  The
[_Troubleshooting_](https://doc.sagemath.org/html/en/installation/troubles.html) section
in the Sage Installation Guide provides instructions on what information to provide so that we can provide
help more effectively.

Contributing to Sage
--------------------

If you want to contribute to Sage, you may start looking around the [Sage GitHub wiki](https://github.com/sagemath/sage/wiki)
and reading the [Developer Guide](https://doc.sagemath.org/html/en/developer/index.html).
If you have questions regarding Sage development, visit the [sage-devel mailing list](https://groups.google.com/group/sage-devel).

Changes to Included Software
----------------------------

All software packages included in Sage is copyrighted by the respective authors
and released under an open-source license that is __GPL version 3 or later__
compatible. See [COPYING.txt](./COPYING.txt) for more details.

The source of the packages are in unmodified (as far as possible) tarballs in
the `upstream/` directory. The description, version information,
patches, and build scripts are in the accompanying `build/pkgs/<packagename>`
directory. These directories are part of the Sage git repository.

<p align="center">
   Copyright (C) 2005-2024 The Sage Development Team
</p>
<p align="center">
   https://www.sagemath.org
</p>

