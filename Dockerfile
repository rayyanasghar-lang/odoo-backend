FROM odoo:19

USER root

# Install Chrome dependencies and Chrome (Ubuntu Noble compatible)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    fonts-liberation \
    libasound2t64 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    libu2f-udev \
    libvulkan1 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome Stable
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for scraping
# webdriver-manager will download the correct ChromeDriver at runtime
RUN pip3 install --no-cache-dir --break-system-packages --ignore-installed \
    selenium \
    selenium-stealth \
    webdriver-manager

# Verify Chrome installation
RUN google-chrome-stable --version

# Create cache directory for webdriver-manager with proper permissions
RUN mkdir -p /home/odoo/.wdm && chown -R odoo:odoo /home/odoo/.wdm

USER odoo

# Set environment variable for webdriver-manager cache location
ENV WDM_LOCAL=1
ENV WDM_LOG_LEVEL=0
