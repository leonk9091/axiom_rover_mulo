FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-lc"]

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    locales \
    curl \
    gnupg2 \
    lsb-release \
    software-properties-common \
    git \
    python3-pip \
    && locale-gen en_US en_US.UTF-8 \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    -o /usr/share/keyrings/ros-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
    http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
    | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-ros-base \
    ros-jazzy-nav2-bringup \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-rviz2 \
    ros-jazzy-ros-gz \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages \
    colcon-common-extensions \
    rosdep \
    vcstool

WORKDIR /workspaces/axiom_rover_ws

COPY . /workspaces/axiom_rover_ws

RUN rosdep init || true && rosdep update || true

CMD source /opt/ros/jazzy/setup.bash && \
    colcon build --symlink-install && \
    bash
