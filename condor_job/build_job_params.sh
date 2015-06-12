#!/bin/bash


for path in "/study/reference/public/IAPS/IAPS/CompleteSets1-20/IAPS 1-20 Images/"*.jpg; do
  file=$(basename "$path") 

  echo Arguments=$file
  echo Queue
done

