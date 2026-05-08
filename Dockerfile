FROM nvidia/cudagl:11.3.1-devel-ubuntu20.04

# Prevent interactive prompts
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/conda/bin:${PATH}"

ENV DISPLAY=:0
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics,display

# 1. Install system dependencies
RUN apt-get update && apt-get install -y \
    unzip \
    wget \
    git \
    python3-pip \
    libomp5 \
    libjpeg-turbo8 \
    libtiff5 \
    libvulkan1 \
    xdg-user-dirs \
    && rm -rf /var/lib/apt/lists/*

# 2. Install Miniconda
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && rm miniconda.sh
ENV PATH="/opt/conda/bin:${PATH}"

# 3. Set up workspace
WORKDIR /workspace/DT-DRIVE
COPY ./data_generation/carla/scripts ./data_generation/carla/scripts

# 4. Run your existing setup scripts
# Move to the CARLA data generation directory and run setup scripts
WORKDIR /workspace/DT-DRIVE/data_generation/carla
RUN chmod +x ./scripts/*.sh
RUN ./scripts/setup_carla.sh

SHELL ["/bin/bash", "-c"]

# 5. Setup Transfuser++
RUN ./scripts/setup_transfuser_plus_plus.sh

RUN source /opt/conda/etc/profile.d/conda.sh && \
    conda config --set always_yes yes && \
    conda config --add envs_dirs /opt/conda/envs && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r && \
    cd /workspace/DT-DRIVE/data_generation/carla/ads/transfuser_plus_plus && \
    conda env create -f environment.yml -n garage

RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /root/.bashrc

# Copy the rest of the project files
WORKDIR /workspace/DT-DRIVE
COPY . .

# Setup user
RUN useradd -m -s /bin/bash carlauser && \
    echo "carlauser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Change ownership of the necessary folders (this is the only part that might take a moment)
RUN chown -R carlauser:carlauser /workspace/DT-DRIVE /opt/conda

# Setup bashrc for the new user
RUN echo "source /opt/conda/etc/profile.d/conda.sh" >> /home/carlauser/.bashrc && \
    echo "conda activate garage" >> /home/carlauser/.bashrc

USER carlauser
WORKDIR /workspace/DT-DRIVE/data_generation/carla

CMD ["/bin/bash"]