#!/bin/bash
docker_file_path='Dockerfile'
tag='dev'
if [ "$1" = "cython" ]; then
  docker_file_path='Dockerfile_cython'
  tag='cython'
elif [ "$1" = 'nuitka' ]; then
  docker_file_path='Dockerfile_nuitka'
  tag='nuitka'
fi

repos="local/iva-web-service:$tag"
if [ "$2" = "aws" ]; then
  repos="860291577631.dkr.ecr.ap-southeast-1.amazonaws.com/iva/iva-web-service:$tag"
fi
echo docker build -f $docker_file_path -t $repos .
docker build -f $docker_file_path -t $repos .
