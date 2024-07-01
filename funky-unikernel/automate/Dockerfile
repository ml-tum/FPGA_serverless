FROM xilinx/xilinx_runtime_base:alveo-2021.1-ubuntu-20.04

ARG USER
ARG TOKEN

SHELL ["/bin/bash", "-c"]

#Set locales
RUN apt-get update && apt-get install -y locales && locale-gen en_US.UTF-8

ENV TZ=Europe/Berlin

RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8    

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone; 

#Get all necessary packages
RUN apt-get update && apt-get install -y git clang-7 \
	clang++-7 cmake build-essential nasm opencl-headers && \
	apt-get clean

##RUN git config --global url.”https://${USER}:${TOKEN}@github.com/".insteadOf “https://github.com/"
RUN git config --global url."https://${USER}:${TOKEN}@github.com".insteadOf "https://github.com"
## build IncludeOS
##ENV INCLUDEOS_PREFIX=/root/includeos
##ENV CC=clang-7
##ENV CXX=clang++-7

RUN source /opt/xilinx/xrt/setup.sh && mkdir root/includeos && cd /root && \
	git clone https://github.com/AtsushiKoshiba/funky-unikernel.git && \
	cd funky-unikernel && mkdir build && cd build && \
	export INCLUDEOS_PREFIX=/root/includeos && \
	export CC=clang-7 && \
	export CXX=clang++-7 && \
	cmake .. -DCMAKE_INSTALL_PREFIX=${INCLUDEOS_PREFIX} && \
	sed -i "s/GIT_REPOSITORY git.*/GIT_REPOSITORY https\:\/\/github\.com\/AtsushiKoshiba\/funky\-solo5\.git/g" /root/funky-unikernel/cmake/cross_compiled_libraries.cmake && \
	make PrecompiledLibraries && make -j 16 && make install
