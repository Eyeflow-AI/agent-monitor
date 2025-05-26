#!/bin/bash
# LOG file at /opt/eyeflow/install/edge-install-<date time>.log
# Install Eyeflow EDGE 
#     Options are:
#     Python on Ubuntu 22.04 server
#     Python on Docker
#     C++ on Docker
# To download instructions and script:
#     wget https://raw.githubusercontent.com/snsergio/agent/main/README-Eyeflow_Edge_Install.txt
#     wget https://raw.githubusercontent.com/snsergio/agent/main/install-edge.sh
#     chmod +x install-edge.sh
#     sudo ./install-edge.sh
clear
set -eo pipefail
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi
mkdir -p /opt/eyeflow/install
touch /opt/eyeflow/install/edge-install.log
echo "################################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "##### Initiating Eyeflow EDGE installation #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
date | sudo tee -a /opt/eyeflow/install/edge-install.log
if [ ! "$EUID" -ne 0 ]; then
    echo "Running as root" | sudo tee -a /opt/eyeflow/install/edge-install.log
fi
lspci | grep -i nvidia &> /dev/null
if [ ! $? == 0 ]; then
    echo "No NVIDIA GPU found, exiting..." | sudo tee -a /opt/eyeflow/install/edge-install.log
    exit
fi
if [ ! $(lsb_release -sr) == "22.04" ]; then
    echo "OS is not Version 22.04, please use correct distributiona and version" | sudo tee -a /opt/eyeflow/install/edge-install.log
fi
echo "#########################################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "##### Station GPU and Operating System information: #####"
echo "GPU Card: $(lspci | grep -i nvidia)" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "Operating system installed: $(lsb_release -si)" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "OS version: $(lsb_release -sr)" | sudo tee -a /opt/eyeflow/install/edge-install.log
if [ -f ./install-edge.sh ]; then
    cp ./install-edge.sh /opt/eyeflow/install/install-edge.sh
fi
function choose_from_menu() {
    local prompt="$1" outvar="$2"
    shift
    shift
    local options=("$@") cur=0 count=${#options[@]} index=0
    local esc=$(echo -en "\e")
    printf "$prompt\n"
    while true
    do
        index=0
        for o in "${options[@]}"
        do
            if [ "$index" == "$cur" ]
            then echo -e " >\e[7m$o\e[0m"
            else echo "  $o"
            fi
            index=$(( $index + 1 ))
        done
        read -s -n3 key
        if [[ $key == $esc[A ]]
        then cur=$(( $cur - 1 ))
            [ "$cur" -lt 0 ] && cur=0
        elif [[ $key == $esc[B ]]
        then cur=$(( $cur + 1 ))
            [ "$cur" -ge $count ] && cur=$(( $count - 1 ))
        elif [[ $key == "" ]]
        then break
        fi
        echo -en "\e[${count}A"
    done
    printf -v $outvar "${options[$cur]}"
}
if [ ! -f /opt/eyeflow/install/resume-status ]; then
    selections=(
    "Install EDGE Python on Ubuntu Station"
    "Install EDGE Python on Docker container"
    "Install EDGE C++ on Docker container"
    )
    echo " "
    echo " "
    choose_from_menu "Use arrow keys to select installation type and hit <ENTER> or <CTRL-C> to exit:" selected_choice "${selections[@]}"
    echo "Selected Installation: $selected_choice"
    if [[ $selected_choice = "Install EDGE Python on Ubuntu Station" ]]; then
        touch /opt/eyeflow/install/edge-option-1
    elif [[ $selected_choice = "Install EDGE Python on Docker container" ]]; then
        touch /opt/eyeflow/install/edge-option-2
    elif [[ $selected_choice = "Install EDGE C++ on Docker container" ]]; then
        touch /opt/eyeflow/install/edge-option-3
    else
        exit
    fi
    echo "resuming installation"
fi
if [ -f /opt/eyeflow/install/edge-option-1 ]; then
    echo "###############################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
    echo "#####   running EDGE installation script  #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
    echo "#####      Python on physical server      #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
    if [ ! -f /opt/eyeflow/install/resume-status ]; then
        echo "##### running script for the first time.. #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt update | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt -y upgrade | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Installing initial packages         #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y gcc make libsystemd-dev
        echo "##### Adding PPA Repository               #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        add-apt-repository -y ppa:graphics-drivers/ppa | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Installing Nvidia 525 driver        #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt update
        apt install -y nvidia-driver-525-server | sudo tee -a /opt/eyeflow/install/edge-install.log
        script="sudo bash /opt/eyeflow/install/install-edge.sh"
        touch /home/eyeflow/.bash_login
        echo 'echo "####################################################################"' > /home/eyeflow/.bash_login
        echo 'echo "#    Resuming EDGE on Ubuntu installation - Enter SUDO password    #"' >> /home/eyeflow/.bash_login
        echo 'echo "####################################################################"' >> /home/eyeflow/.bash_login
        echo "$script" >> /home/eyeflow/.bash_login
        touch /opt/eyeflow/install/resume-status
        echo "#################################################################################"
        echo "# Rebooting station - login as eyeflow user after reboot to resume installation #"
        echo "#################################################################################"
        echo "Rebooting at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        reboot
    else
        echo "######################################################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### returning from boot-resuming Edge Python on Ubuntu Install #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "Return from boot at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####     nvidia-smi output     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        nvidia-smi | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####        GCC Version        #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        gcc --version | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####      Kernel headers       #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        uname -r | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Download and install CUDA #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
        mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600 | sudo tee -a /opt/eyeflow/install/edge-install.log
        wget https://developer.download.nvidia.com/compute/cuda/12.0.1/local_installers/cuda-repo-ubuntu2204-12-0-local_12.0.1-525.85.12-1_amd64.deb
        dpkg -i cuda-repo-ubuntu2204-12-0-local_12.0.1-525.85.12-1_amd64.deb | sudo tee -a /opt/eyeflow/install/edge-install.log
        cp /var/cuda-repo-ubuntu2204-12-0-local/cuda-*-keyring.gpg /usr/share/keyrings/ | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt-get update
        apt-get -y install cuda | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "######################################################################"
        echo "#####   Install required libraries ignoring install-recommends   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y \
            gcc \
            g++ \
            gfortran \
            build-essential \
            software-properties-common \
            python3 \
            python3-pip \
            python3-dev \
            python3-setuptools \
            libhdf5-serial-dev \
            libblas3 \
            libblas-dev \
            liblapack3 \
            liblapack-dev \
            libatlas-base-dev \
            libjpeg8-dev \
            libtiff5-dev \
            zlib1g-dev \
            freetype* \
            libtiff-dev \
            libjpeg-dev \
            libpng-dev \
            libsm6 \
            libxext6 \
            libxrender-dev \
            fonts-dejavu-core
        echo "#####  Removing packages   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt-get remove x264 libx264-dev
        echo "##### Adding Universe repo #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        add-apt-repository -y universe
        apt-get upgrade -y
        echo "##### Install additional libraries ignoring install-recommends #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y \
            libgtk2.0-dev \
            libeigen3-dev \
            libtheora-dev \
            libvorbis-dev \
            libxvidcore-dev \
            libx264-dev \
            sphinx-common \
            libfaac-dev \
            libopencore-amrnb-dev \
            libopencore-amrwb-dev \
            libopenexr-dev \
            libgstreamer1.0-0 \
            libgstreamer1.0-dev \
            libgstreamer-plugins-bad1.0-dev \
            libgstreamer-plugins-good1.0-dev \
            libgstreamer-plugins-base1.0-dev \
            libavutil-dev \
            libavfilter-dev \
            libtbb2 \
            libtbb-dev \
            libavcodec-dev \
            libavformat-dev \
            libswscale-dev \
            libeigen3-dev \
            ffmpeg \
            libxine2-dev \
            libv4l-dev \
            gstreamer1.0-plugins-base \
            gstreamer1.0-plugins-good \
            gstreamer1.0-plugins-bad \
            gstreamer1.0-plugins-ugly \
            gstreamer1.0-libav \
            gstreamer1.0-tools \
            libxvidcore-dev \
            libx264-dev \
            libmp3lame-dev \
            x264 \
            v4l-utils
        echo "##### Install changed requirement qt5-default and libdc1394-22-dev #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y \
            qtbase5-dev \
            qtchooser \
            qt5-qmake \
            qtbase5-dev-tools \
            libdc1394-dev
        echo "##### Install CUDNN #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/libcudnn8_8.8.0.121-1+cuda12.0_amd64.deb
        dpkg -i libcudnn8_8.8.0.121-1+cuda12.0_amd64.deb
        wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/libcudnn8-dev_8.8.0.121-1+cuda12.0_amd64.deb
        dpkg -i libcudnn8-dev_8.8.0.121-1+cuda12.0_amd64.deb
        echo "##### Install python requirements #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y python-wheel-common
        echo "##### Install PIP packages #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        python3 -m pip install --upgrade --no-cache-dir --upgrade --trusted-host pypi.python.org \
            DateTime \
            decorator \
            tables \
            h5py \
            scipy \
            scikit-learn \
            pika \
            arrow \
            psutil \
            pynvml \
            Pillow \
            pymongo \
            opencv_python \
            tqdm \
            keras_resnet \
            arrow \
            psutil \
            pynvml \
            azure-storage-blob \
            eyeflow_sdk
        echo "##### Install Tensorflow #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        python3 -m pip install --no-cache-dir --upgrade --trusted-host pypi.python.org tensorflow==2.12.0
        pip install tensorrt
        echo "##### Exporting environment variables #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        export PATH=/usr/local/cuda/bin${PATH:+:${PATH}}
        export LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib/:/usr/local/cuda/extras/CUPTI/lib64:/usr/local/cuda/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}
        export CUDA_HOME=/usr/local/cuda
        echo "#####          NVCC Version          #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        nvcc --version | sudo tee -a /opt/eyeflow/install/edge-install.log
        function lib_installed() { /sbin/ldconfig -N -v $(sed 's/:/ /' <<< $LD_LIBRARY_PATH) 2>/dev/null | grep $1; }
        function check() { lib_installed $1 && echo "$1 is installed" || echo "ERROR: $1 is NOT installed"; }
        echo "##### Logging CUDA components version #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        check libcuda | sudo tee -a /opt/eyeflow/install/edge-install.log
        check libcudart | sudo tee -a /opt/eyeflow/install/edge-install.log
        check libcudnn | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "###########################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Preparing Eyeflow user groups and directories:" | sudo tee -a /opt/eyeflow/install/edge-install.log
        usermod -aG users eyeflow
        usermod -aG sudo eyeflow
        mkdir -p /opt/eyeflow/data
        mkdir -p /opt/eyeflow/src
        mkdir -p /opt/eyeflow/log
        mkdir -p /opt/eyeflow/conf
        mkdir -p /opt/eyeflow/run
        echo "##### Installing GIT #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y git acl
        echo "##### Cloning Edge repo and setting rights #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        cd /opt/eyeflow/install
        git clone https://github.com/Eyeflow-AI/eyeflow-edge-python.git
        chown -R eyeflow:users /opt/eyeflow
        setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
        chmod g+rwxs /opt/eyeflow
        chown -R :users /opt/eyeflow
        chmod 775 /opt/eyeflow
        rsync -zvrh /opt/eyeflow/install/eyeflow-edge-python/* /opt/eyeflow/
        cd /opt/eyeflow
        chmod +x edge_run.sh
        chown -R eyeflow:users /opt/eyeflow
        setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
        chmod g+rwxs /opt/eyeflow
        chown -R :users /opt/eyeflow
        chmod 775 /opt/eyeflow
        echo "##### Installing onnx packages #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        python3 -m pip install -U pip
        python3 -m pip install -U eyeflow-sdk
        python3 -m pip install onnx
        python3 -m pip install tf2onnx
        python3 -m pip install nvidia-pyindex
        python3 -m pip install onnx-graphsurgeon
        echo "###############################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####   end of EDGE installation script   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####      Python on physical server      #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Finished at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
    fi
elif [ -f /opt/eyeflow/install/edge-option-2 ]; then
    echo "###############################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
    echo "#####   running EDGE installation script  #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
    echo "#####           Python on docker          #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
    if [ ! -f /opt/eyeflow/install/resume-status ]; then
        echo "##### running script for the first time.. #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt update | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt -y upgrade | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Adding PPA Repository               #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        add-apt-repository -y ppa:graphics-drivers/ppa | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Installing Nvidia 525 driver        #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt update
        apt install -y nvidia-driver-525-server | sudo tee -a /opt/eyeflow/install/edge-install.log
        script="sudo bash /opt/eyeflow/install/install-edge.sh"
        touch /home/eyeflow/.bash_login
        echo 'echo "#####################################################################"' > /home/eyeflow/.bash_login
        echo 'echo "# Resuming EDGE Python on Docker installation - Enter SUDO password #"' >> /home/eyeflow/.bash_login
        echo 'echo "#####################################################################"' >> /home/eyeflow/.bash_login
        echo "$script" >> /home/eyeflow/.bash_login
        touch /opt/eyeflow/install/resume-status
        echo "#################################################################################"
        echo "# Rebooting station - login as eyeflow user after reboot to resume installation #"
        echo "#################################################################################"
        echo "Rebooting at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        reboot
    else
        echo "######################################################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### return from boot - resuming Edge Python on Docker Install  #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "Return from boot at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####          nvidia-smi output        #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        nvidia-smi | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Install docker required libraries #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            software-properties-common \
            gnupg
        echo "#####      Install docker keyring       #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        echo "#####         Install docker            #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        echo "#####     Install NVIDIA repository     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
        apt-get update
        apt-get upgrade -y
        echo "#####       Install nvidia docker       #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt-get install -y nvidia-docker2
        usermod -aG docker eyeflow
        systemctl restart docker
        echo "#####     Verifying Docker access to NVIDIA GPU     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        docker run -it --gpus all nvidia/cuda:11.4.3-base-ubuntu20.04 nvidia-smi | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Preparing Eyeflow user groups and directories #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        usermod -aG users eyeflow
        usermod -aG sudo eyeflow
        mkdir -p /opt/eyeflow/data
        mkdir -p /opt/eyeflow/src
        mkdir -p /opt/eyeflow/log
        mkdir -p /opt/eyeflow/conf
        mkdir -p /opt/eyeflow/run
        echo "##### Installing GIT #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install git acl -y
        echo "##### Cloning Edge repo and setting rights #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        cd /opt/eyeflow/install
        git clone https://github.com/Eyeflow-AI/eyeflow-edge-python.git
        chown -R eyeflow:users /opt/eyeflow
        setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
        chmod g+rwxs /opt/eyeflow
        chown -R :users /opt/eyeflow
        chmod 775 /opt/eyeflow
        rsync -zvrh /opt/eyeflow/install/eyeflow-edge-python/* /opt/eyeflow/
        cd /opt/eyeflow
        chmod +x edge_run.sh
        chown -R eyeflow:users /opt/eyeflow
        setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
        chmod g+rwxs /opt/eyeflow
        chown -R :users /opt/eyeflow
        chmod 775 /opt/eyeflow
        echo "##### Creating Docker scripts #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        touch /opt/eyeflow/docker_license.sh
        echo "docker run --rm -it --name license -v /opt/eyeflow:/opt/eyeflow --gpus all snsergio/monitor:efd1 python3 src/request_license.py \$1 \$2" > docker_license.sh
        touch /opt/eyeflow/docker_edge_run.sh
        echo "docker run --rm -d --name license -v /opt/eyeflow:/opt/eyeflow --gpus all snsergio/monitor:efd1 python3 -u src/call_flow.py" > docker_edge_run.sh
        touch /opt/eyeflow/docker_edge_interactive.sh
        echo "docker run --rm -it --name license -v /opt/eyeflow:/opt/eyeflow --gpus all snsergio/monitor:efd1 python3 -u src/call_flow.py" > docker_edge_interactive.sh
        chmod +x /opt/eyeflow/docker_license.sh
        chmod +x /opt/eyeflow/docker_edge_run.sh
        chmod +x /opt/eyeflow/docker_edge_interactive.sh
        touch /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "##### Pulling docker image     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "Start pull at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        docker pull snsergio/monitor:efd1
        echo "End pull at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        clear
        echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "! To start DEVICE Licensing on Eyeflow DEVICES, copy the reference command from Eyeflow / Devices / Copy Command !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "! and paste two last codes in the command as shown below:                                                        !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "!     ./docker_license.sh <code 1> <code 2>                                                                      !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo " " | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "! To start Eyeflow EDGE interactive, run the following command:                                                  !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "!     ./docker_edge_interactive.sh                                                                               !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo " " | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "! To start Eyeflow EDGE in the background, run the following command:                                            !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "!     ./docker_edge_run.sh                                                                                       !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        echo "###############################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####   end of EDGE installation script   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####          Python on docker           #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Finished at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "############################################################################################"
        echo "# Instructions to run Eyeflow Edge at: /opt/eyeflow/install/how-execute-eyeflow-docker.txt #"
        echo "############################################################################################"
        sleep 5
    fi
elif [ -f /opt/eyeflow/install/edge-option-3 ]; then
    echo "###############################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
    echo "#####   running EDGE installation script  #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
    echo "#####            C++ on docker            #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
    if [ ! -f /opt/eyeflow/install/resume-status ]; then
        echo "##### running script for the first time.. #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt update | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt -y upgrade | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Adding PPA Repository               #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        add-apt-repository -y ppa:graphics-drivers/ppa | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Installing Nvidia 525 driver        #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt update
        apt install -y nvidia-driver-525-server | sudo tee -a /opt/eyeflow/install/edge-install.log
        script="sudo bash /opt/eyeflow/install/install-edge.sh"
        touch /home/eyeflow/.bash_login
        echo 'echo "####################################################################"' > /home/eyeflow/.bash_login
        echo 'echo "#  Resuming EDGE C++ on Docker installation - Enter SUDO password  #"' >> /home/eyeflow/.bash_login
        echo 'echo "####################################################################"' >> /home/eyeflow/.bash_login
        echo "$script" >> /home/eyeflow/.bash_login
        touch /opt/eyeflow/install/resume-status
        echo "#################################################################################"
        echo "# Rebooting station - login as eyeflow user after reboot to resume installation #"
        echo "#################################################################################"
        echo "Rebooting at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        reboot
    else
        echo "######################################################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####   return from boot - resuming Edge C++ on Docker Install   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "Return from boot at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####          nvidia-smi output        #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        nvidia-smi | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Install docker required libraries #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            software-properties-common \
            gnupg
        echo "#####      Install docker keyring       #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        echo "#####         Install docker            #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        echo "#####     Install NVIDIA repository     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        distribution=$(. /etc/os-release;echo $ID$VERSION_ID) && curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - && curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
        apt-get update
        apt-get upgrade -y
        echo "#####       Install nvidia docker       #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt-get install -y nvidia-docker2
        usermod -aG docker eyeflow
        systemctl restart docker
        echo "#####     Verifying Docker access to NVIDIA GPU     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        docker run -it --gpus all nvidia/cuda:11.4.0-base-ubuntu20.04 nvidia-smi | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Preparing Eyeflow user groups and directories #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        usermod -aG users eyeflow
        usermod -aG sudo eyeflow
        mkdir -p /opt/eyeflow/data
        mkdir -p /opt/eyeflow/src
        mkdir -p /opt/eyeflow/log
        mkdir -p /opt/eyeflow/conf
        mkdir -p /opt/eyeflow/run
        echo "##### Installing GIT #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        apt install git acl -y
        echo "##### Cloning Edge repo and setting rights #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        cd /opt/eyeflow/install

        echo "##############################################"
        echo "# NEED TO IMPLEMENT EDGE C++ STEPS FROM HERE #"
        echo "##############################################"
        # git clone https://github.com/Eyeflow-AI/eyeflow-edge-python.git
        # chown -R eyeflow:users /opt/eyeflow
        # setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
        # chmod g+rwxs /opt/eyeflow
        # chown -R :users /opt/eyeflow
        # chmod 775 /opt/eyeflow
        # rsync -zvrh /opt/eyeflow/install/eyeflow-edge-python/* /opt/eyeflow/
        # cd /opt/eyeflow
        # chmod +x edge_run.sh
        # chown -R eyeflow:users /opt/eyeflow
        # setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow
        # chmod g+rwxs /opt/eyeflow
        # chown -R :users /opt/eyeflow
        # chmod 775 /opt/eyeflow

        # echo "##### Creating Docker scripts #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        # touch /opt/eyeflow/docker_license.sh
        # echo "docker run --rm -it --name license -v /opt/eyeflow:/opt/eyeflow --gpus all snsergio/monitor:efd1 python3 src/request_license.py \$1 \$2" > docker_license.sh
        # touch /opt/eyeflow/docker_edge_run.sh
        # echo "docker run --rm -d --name license -v /opt/eyeflow:/opt/eyeflow --gpus all snsergio/monitor:efd1 python3 -u src/call_flow.py" > docker_edge_run.sh
        # touch /opt/eyeflow/docker_edge_interactive.sh
        # echo "docker run --rm -it --name license -v /opt/eyeflow:/opt/eyeflow --gpus all snsergio/monitor:efd1 python3 -u src/call_flow.py" > docker_edge_interactive.sh
        # chmod +x /opt/eyeflow/docker_license.sh
        # chmod +x /opt/eyeflow/docker_edge_run.sh
        # chmod +x /opt/eyeflow/docker_edge_interactive.sh
        # touch /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # clear
        # echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "! To start DEVICE Licensing on Eyeflow DEVICES, copy the reference command from Eyeflow / Devices / Copy Command !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "! and paste two last codes in the command as shown below:                                                        !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "!     ./docker_license.sh <code 1> <code 2>                                                                      !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo " " | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "! To start Eyeflow EDGE interactive, run the following command:                                                  !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "!     ./docker_edge_interactive.sh                                                                               !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo " " | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "! To start Eyeflow EDGE in the background, run the following command:                                            !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "!     ./docker_edge_run.sh                                                                                       !" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "+----------------------------------------------------------------------------------------------------------------+" | sudo tee -a /opt/eyeflow/install/how-execute-eyeflow-docker.txt
        # echo "##### Pulling docker image     #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        # echo "Start pull at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        # docker pull snsergio/monitor:efd1
        # echo "End pull at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "###############################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####   end of EDGE installation script   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "#####            C++ on docker            #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "##### Finished at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
        echo "############################################################################################"
        echo "# Instructions to run Eyeflow Edge at: /opt/eyeflow/install/how-execute-eyeflow-docker.txt #"
        echo "############################################################################################"
        sleep 5
    fi
fi
echo " "
echo " "
echo "######################################################################################"
echo "#  To install Metric collector run the following command:                            #"
echo "#      wget https://raw.githubusercontent.com/snsergio/agent/main/install-monitor.sh #"
echo "#      chmod a+x install-monitor.sh                                                  #"
echo "#      sudo ./install-monitor.sh                                                     #"
echo "######################################################################################"
echo " "
echo "##### Removing temporary files #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
rm -f /opt/eyeflow/install/resume-status
rm -f /opt/eyeflow/install/edge-option-1
rm -f /opt/eyeflow/install/edge-option-2
rm -f /opt/eyeflow/install/edge-option-3
rm -f /opt/eyeflow/install/install-edge.sh
rm -rf /opt/eyeflow/install/eyeflow-edge-python
rm -f /home/eyeflow/.bash_login
rm -f /home/eyeflow/install-edge.sh
rm -f /home/eyeflow/cuda-repo*
rm -f /home/eyeflow/libcudnn*
echo "#################################################################"
echo "#          Rebooting station to complete installation           #"
echo "#################################################################"
echo " "
echo "#################################################################"
echo "# LOG file at: /opt/eyeflow/install/edge-install<date time>.log #"
echo "#################################################################"
mv /opt/eyeflow/install/edge-install.log /opt/eyeflow/install/edge-install-$(date +%F-%H:%M).log
sleep 5
reboot