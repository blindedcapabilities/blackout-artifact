FROM ubuntu:focal

ENV TZ=UTC

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    locales

RUN locale-gen en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN apt update && apt install -y \
    curl \
    wget \
    git \
    vim \
    build-essential \
    unzip \
    pkg-config \
    tzdata \ 
    python3 \
    autoconf \
    automake \
    cmake \
    ninja-build \
    zlib1g-dev \
    python3-pip \
    libtcl8.6 \
    libelf-dev \
    sudo

RUN  pip3 install pyyaml
ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN adduser --uid $USER_UID --disabled-password $USERNAME

USER $USERNAME
WORKDIR /home/$USERNAME


# Install BlueSpec compiler (bsc)
ADD --chown=$USERNAME:$USERNAME https://github.com/B-Lang-org/bsc/releases/download/2024.07/bsc-2024.07-ubuntu-20.04.tar.gz ./
RUN tar xzf bsc-2024.07-ubuntu-20.04.tar.gz
RUN ls bsc-2024.07-ubuntu-20.04
ENV PATH="$PATH:/home/$USERNAME/bsc-2024.07-ubuntu-20.04/bin/"
RUN echo $PATH

# Install BlueSpec libraries
RUN git clone https://github.com/B-Lang-org/bsc-contrib.git
RUN cd bsc-contrib && git checkout 17e029843cefb3421913d630b2984a1591d2cb8c && make PREFIX=~/bsc-2024.07-ubuntu-20.04/

WORKDIR /home/$USERNAME/
COPY --chown=$USERNAME:$USERNAME ./patch ./patch
RUN git clone https://github.com/CTSRD-CHERI/cheribuild.git
RUN mkdir -p /home/$USERNAME/cheri
WORKDIR /home/$USERNAME/cheri
RUN git clone https://github.com/CTSRD-CHERI/newlib.git
RUN cd newlib && git checkout a982bc9
WORKDIR /home/$USERNAME/cheri
RUN git clone https://github.com/CTSRD-CHERI/llvm-project.git
WORKDIR /home/$USERNAME/cheri/llvm-project
RUN git checkout 578ea4f7
RUN git apply /home/$USERNAME/patch/blinded_diff.patch

WORKDIR /home/$USERNAME/cheribuild

RUN ./cheribuild.py llvm-native -d

RUN ./cheribuild.py newlib-baremetal-riscv64-purecap && ./cheribuild.py compiler-rt-builtins-baremetal-riscv64-purecap
RUN ./cheribuild.py newlib-baremetal-riscv64
RUN ./cheribuild.py compiler-rt-builtins-baremetal-riscv64


### Let's build Toooba core for baseline 
WORKDIR /home/$USERNAME/cheri
RUN git clone https://github.com/CTSRD-CHERI/Toooba.git &&  cd Toooba && git checkout 1ae93da4 && git submodule update --init --recursive
ENV TOOOBA_ROOT=/home/$USERNAME/cheri/Toooba/

WORKDIR ${TOOOBA_ROOT}/builds/RV64ACDFIMSUxCHERI_Toooba_bluesim
RUN sed -i 's/Bool verbose = False;/Bool verbose = True;/' ../../src_Core/RISCY_OOO/procs/RV64G_OOO/MemExePipeline.bsv
RUN sed -i 's/Bool verbose = False;/Bool verbose = True;/' ../../src_Core/RISCY_OOO/procs/RV64G_OOO/AluExePipeline.bsv
RUN make compile && make simulator 
RUN cp exe_HW_sim exe_HW_sim_baseline
RUN cp exe_HW_sim.so exe_HW_sim_baseline.so
ENV SIM_BASELINE=/home/$USERNAME/cheri/Toooba/builds/RV64ACDFIMSUxCHERI_Toooba_bluesim/exe_HW_sim_baseline

### Let's build Toooba core for blinded
RUN git checkout -- ../../src_Core/RISCY_OOO/procs/RV64G_OOO/MemExePipeline.bsv
RUN git checkout -- ../../src_Core/RISCY_OOO/procs/RV64G_OOO/AluExePipeline.bsv
RUN cd ${TOOOBA_ROOT} && git apply /home/$USERNAME/patch/toooba.patch && cd ${TOOOBA_ROOT}/libs/cheri-cap-lib/ &&  git apply /home/$USERNAME/patch/cheri_cap_lib.patch
RUN sed -i 's/Bool verbose = False;/Bool verbose = True;/' ../../src_Core/RISCY_OOO/procs/RV64G_OOO/MemExePipeline.bsv
RUN sed -i 's/Bool verbose = False;/Bool verbose = True;/' ../../src_Core/RISCY_OOO/procs/RV64G_OOO/AluExePipeline.bsv
RUN make compile && make simulator
RUN make -C ${TOOOBA_ROOT}/Tests/elf_to_hex
ENV SIM_BLACKOUT=/home/$USERNAME/cheri/Toooba/builds/RV64ACDFIMSUxCHERI_Toooba_bluesim/exe_HW_sim

WORKDIR /home/$USERNAME/

RUN git clone https://github.com/cirosantilli/vcdvcd.git
ENV VCDCAT=/home/$USERNAME/vcdvcd/vcdcat
COPY --chown=$USERNAME:$USERNAME ./blinded-cheri-sw ./blinded-cheri-sw
ENV BLINDED_SW_ROOT=/home/$USERNAME/blinded-cheri-sw/

USER root
RUN echo "$USERNAME ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/no-passwd && \
    chmod 0440 /etc/sudoers.d/no-passwd
USER $USERNAME

WORKDIR /home/$USERNAME/

CMD ["/bin/bash"]
