#!/bin/sh

export PYQTDESIGNERPATH=$(pwd)/designerplugins
export PYTHONPATH=$PYTHONPATH:$(pwd)/ui

designer-qt4
