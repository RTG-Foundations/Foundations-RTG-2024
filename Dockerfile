FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tint2 \
    xfce4 \
    x11vnc \
    xvfb \
    python3-pip \
    git \
    curl \
    wget \
    ca-certificates \
    libx11-xcb1 \
    libxcb1 \
    libxcb-util1 \
    libxcb-render0 \
    libxcb-shm0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxrender1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libxfixes3 \
    libxcursor1 \
    libxinerama1 \
    libxss1 \
    libglib2.0-0 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libxext6 \
    libsm6 \
    libxcomposite1 \
    libxdamage1 \
    libxkbcommon-x11-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*


# Create work directory
WORKDIR /app

# Copy project files
COPY . /app

RUN apt-get update && apt-get install -y openbox

# Make start script executable
RUN chmod +x /app/start.sh

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Clone noVNC and websockify
RUN git clone --branch v1.2.0 https://github.com/novnc/noVNC.git /opt/novnc \
 && git clone https://github.com/novnc/websockify /opt/novnc/utils/websockify

# Close zombie processes
RUN apt-get update && apt-get install -y tini

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/bin/bash", "/app/start.sh"]


EXPOSE 8080

CMD ["/bin/bash", "/app/start.sh"]
