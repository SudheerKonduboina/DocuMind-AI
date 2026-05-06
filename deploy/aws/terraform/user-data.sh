#!/bin/bash

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Login to Docker Hub
echo "${docker_password}" | docker login -u "${docker_username}" --password-stdin

# Create app directory
mkdir -p /opt/ai-doc-qa
cd /opt/ai-doc-qa

# Clone repository (or use docker-compose.yml from S3)
# git clone https://github.com/your-org/ai-doc-qa-app.git .

# Start services
docker-compose pull
docker-compose up -d

# Setup SSL with Let's Encrypt
apt-get install -y certbot python3-certbot-nginx
certbot --nginx -d your-domain.com --email your-email@example.com --agree-tos --non-interactive
