# Use Ubuntu 24.04 and force linux/arm64 to match M1/M2 Macs
FROM --platform=linux/arm64 ubuntu:24.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV HDF5_DIR=/usr/lib/aarch64-linux-gnu/hdf5/serial
ENV POLARS_SKIP_CPU_CHECK=1  

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    git python3 python3-pip python3-venv python3-dev \
    build-essential cmake make libopenblas-dev liblapack-dev \
    gfortran libcurl4-openssl-dev python3-numpy libhdf5-dev \
    libhdf5-serial-dev && \
    rm -rf /var/lib/apt/lists/*

# Create and activate a Python virtual environment
RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

# Install necessary Python packages
RUN pip install --upgrade pip && \
    pip install numpy polars-lts-cpu  # Use polars-lts-cpu

# Clone and install MOAB (ensure compatibility with ARM64)
RUN git clone https://bitbucket.org/fathomteam/moab.git /moab
WORKDIR /moab
RUN rm -rf build && mkdir build
WORKDIR /moab/build
RUN cmake .. -DBUILD_SHARED_LIBS=ON -DENABLE_MPI=OFF -DENABLE_HDF5=ON -DHDF5_ROOT=/usr -DENABLE_PYMOAB=ON -DPYTHON_EXECUTABLE=/venv/bin/python3
RUN make -j$(nproc)

# Clone and install uxarray-moab
RUN git clone https://github.com/rajeeja/uxarray-moab.git /uxarray-moab
WORKDIR /uxarray-moab
RUN pip install .

# Install ipython
RUN pip install ipython

# Install Jupyter Lab or Notebook
RUN pip install notebook

# Expose the Jupyter port
EXPOSE 8888

# Start Jupyter Notebook
CMD ["jupyter", "notebook", "--ip", "0.0.0.0", "--port", "8888", "--allow-root", "--NotebookApp.token=''"]