#!/bin/bash

FOLDER=$1

for file in $FOLDER/*; do clustalw $file; done
