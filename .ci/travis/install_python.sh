#! /bin/bash

if [[ "$TRAVIS_OS_NAME" == "osx" ]]; then
    OS="MacOSX-x86_64";
else
    OS="Linux-x86_64";
fi
if [[ "$PYTHON_VERSION" == 2.* ]]; then
      wget http://repo.continuum.io/miniconda/Miniconda-latest-$OS.sh -O miniconda.sh;
else
      wget http://repo.continuum.io/miniconda/Miniconda3-latest-$OS.sh -O miniconda.sh;
fi
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
# conda update conda
conda install python=$PYTHON_VERSION
conda info -a
# cat requirements.txt | grep -v numpydoc | xargs conda create -n test-env python=$PYTHON_VERSION
# conda create -n test-env python=$PYTHON_VERSION
conda install conda-build
# source activate test-env
conda install anaconda-client
conda install coverage
conda install sphinx
