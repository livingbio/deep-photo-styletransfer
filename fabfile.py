# -*- coding: utf-8 -*-

# http://askubuntu.com/questions/886445/how-do-i-properly-install-cuda-8-on-an-azure-vm-running-ubuntu-14-04-lts
# https://docs.microsoft.com/en-us/azure/virtual-machines/linux/n-series-driver-setup
from __future__ import print_function

import os
import sys

from fabric.api import cd, run, sudo, lcd, local, put
from fabric.api import task
from fabric.api import env
from cStringIO import StringIO
from fabric.context_managers import shell_env


def setup_common_env():
    sudo('apt-get update -y')
    sudo('apt-get upgrade -y')
    sudo('apt-get install git -y')
    sudo('apt-get install python-pip python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev zlib1g-dev libjpeg-dev libpng-dev -y')
    sudo('apt-get install libmysqlclient-dev -y')
    sudo('apt-get install jpegoptim optipng -y')
    sudo('apt-get install zsh -y')

    try:
        run('sh -c "$(curl -fsSL https://raw.githubusercontent.com/robbyrussell/oh-my-zsh/master/tools/install.sh)"')
    except:
        pass

    sudo('apt-get purge -y python-pip')
    run('wget -N https://bootstrap.pypa.io/get-pip.py')
    sudo('python ./get-pip.py')
    sudo('apt-get install python-pip')
    sudo('pip install pdbpp ipython')
    sudo('pip install virtualenv')


@task
def setup_cuda_driver():
    with shell_env(CUDA_REPO_PKG="cuda-repo-ubuntu1604_8.0.61-1_amd64.deb"):
        run('wget -O /tmp/${CUDA_REPO_PKG} http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/${CUDA_REPO_PKG}')
        sudo("dpkg -i /tmp/${CUDA_REPO_PKG}")
        run("rm -f /tmp/${CUDA_REPO_PKG}")

    sudo("apt-get update -y")
    sudo("apt-get install cuda-drivers -y")
    sudo('reboot')
    run('nvidia-smi')


@task
def setup_cuda():
    sudo("apt-get install cuda -y")


@task
def setup_deep_photo_styletransfer():
    try:
        run('git clone https://github.com/livingbio/deep-photo-styletransfer.git')
    except:
        pass

    run('luarocks install torch')
    run('luarocks install cutorch')
    with cd("~/deep-photo-styletransfer"):
        # TODO: put('./makefile', 'makefile')
        run('sh models/download_models.sh')

        run('make clean && make')

@task
def setup_requirement():

    sudo('apt-get install octave -y')
    sudo('apt-get install octave-control octave-image octave-io octave-optim octave-signal octave-statistics -y')

    try:
        run('git clone https://github.com/torch/distro.git ~/torch --recursive')
    except:
        pass

    with cd('/root/torch'):
        run('bash install-deps;')
        run('./install.sh -b')

    sudo('apt-get install libmatio2 -y')
    run('luarocks install matio')
    sudo('apt-get install libprotobuf-dev protobuf-compiler -y')
    run('luarocks install loadcaffe')


@task
def setup_docker():
    try:
        sudo('apt-get remove docker docker-engine -y')
    except:
        pass

    sudo('apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual -y')
    sudo('apt-get install apt-transport-https ca-certificates curl software-properties-common -y')
    run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -')
    sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"')
    sudo('apt-get update -y')
    sudo('apt-get install docker-ce -y')


@task
def setup_nvidia_docker():
    # Install nvidia-docker and nvidia-docker-plugin
    run('wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb')
    sudo('dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb')

    # Test nvidia-smi
    sudo('nvidia-docker run --rm nvidia/cuda nvidia-smi')


@task
def install():
    setup_common_env()
    setup_cuda_driver()
    setup_cuda()
    setup_requirement()
    setup_deep_photo_styletransfer()
