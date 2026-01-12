# Odoo Linux Deployment Guide

This guide provides step-by-step instructions to deploy and run this Odoo project on a Linux server (Ubuntu/Debian recommended) using Docker Compose.

## Prerequisites

- A Linux server (e.g., Ubuntu 22.04 or 24.04).
- SSH access to the server with sudo privileges.
- Basic knowledge of the terminal.

---

## Step 1: Update System Packages

Connect to your server via SSH and ensure your system is up to date:

```bash
sudo apt update && sudo apt upgrade -y
```

## Step 2: Install Docker and Docker Compose

Run the following commands to install Docker and the Docker Compose plugin:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose Plugin
sudo apt install -y docker-compose-v2

# Start and enable Docker
sudo systemctl enable --now docker

# Add your user to the docker group (optional, to run docker without sudo)
sudo usermod -aG docker $USER
# Note: You may need to log out and back in for this to take effect.
```

## Step 3: Prepare the Project Directory

Clone your repository or upload the project files to the server:

```bash
# Example if using Git
git clone <your-repository-url>
cd <repository-folder>
```

## Step 4: Configure Permissions

The project uses Google Chrome for web scraping, which requires specific permissions within Docker. Ensure the `addons` and `config` directories have the correct ownership:

```bash
# Ensure the addons and config folders are readable by the container
sudo chown -R 101:101 ./addons ./config
```

> [!NOTE]
> 101 is the default UID for the `odoo` user inside the official Odoo Docker image.

## Step 5: Start the Services

Use Docker Compose to build and start the Odoo and PostgreSQL containers:

```bash
# Build and start in detached mode
sudo docker compose up -d --build
```

Wait a few moments for the containers to initialize. You can check the logs to ensure everything is running correctly:

```bash
sudo docker compose logs -f
```

## Step 6: Access Odoo

Once the logs show that Odoo is running, you can access it via your browser:

- **URL:** `http://<your-server-ip>:8069`
- **Default Database:** `odoo`
- **Default Database User:** `odoo`
- **Default Database Password:** `odoo_password` (as configured in `docker-compose.yml`)

## Troubleshooting

### Port 8069 is blocked

If you cannot access Odoo, check your server's firewall (UFW) to ensure port 8069 is open:

```bash
sudo ufw allow 8069/tcp
```

### Chrome/Scraping Issues

If the scraping features fail, ensure the server has enough RAM (at least 2GB is recommended, as defined in `shm_size` in `docker-compose.yml`). You can check container resources using:

```bash
sudo docker stats
```

### Database Connection

If Odoo fails to connect to the database, verify that the `db` service is running:

```bash
sudo docker compose ps
```
