# Deployment Guide for EC2

This guide explains how to deploy the PWP Journal API project on an AWS EC2 instance using Docker and Docker Compose.

## Prerequisites

- AWS account with permissions to create EC2 instances and security groups.
- Basic knowledge of SSH and AWS EC2.

## Steps

### 1. Launch an EC2 Instance

- Go to the AWS EC2 console.
- Launch a new instance with the following settings:
  - AMI: Amazon Linux 2 or Ubuntu 20.04 LTS
  - Instance type: t2.micro (or larger as needed)
  - Configure security group to allow inbound traffic on:
    - TCP port 22 (SSH)
    - TCP port 8000 (for the Flask app)
    - TCP port 5432 (for Postgres, optional if you want remote DB access)
- Launch the instance and download the key pair (.pem file).

### 2. Connect to the EC2 Instance

```bash
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

### 3. Install Docker and Docker Compose

For Amazon Linux 2:

```bash
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
exit
# Reconnect to apply docker group changes
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

Install Docker Compose:

```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
docker-compose --version
```

### 4. Clone the Repository

```bash
git clone https://github.com/darisdzakwanhoesien2/PWP_JournalAPI.git
cd PWP_JournalAPI
```

Alternatively, transfer your project files via SCP or other methods.

### 5. Configure Environment Variables

Edit the `docker-compose.yml` file if needed to update:

- `SECRET_KEY` to a secure value.
- Database credentials if different.

### 6. Build and Run the Containers

```bash
docker-compose build
docker-compose up -d
```

### 7. Verify the Deployment

- Access the API at `http://your-ec2-public-ip:8000/`
- You should see the JSON message: `{"message": "✅ Journal API is running!"}`

### 8. Optional: Configure Auto-start on Boot

Create a systemd service file to start Docker Compose on boot.

Example `/etc/systemd/system/journalapi.service`:

```ini
[Unit]
Description=Journal API Docker Compose Service
Requires=docker.service
After=docker.service

[Service]
WorkingDirectory=/home/ec2-user/PWP_JournalAPI
ExecStart=/usr/local/bin/docker-compose up
ExecStop=/usr/local/bin/docker-compose down
Restart=always
User=ec2-user

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
sudo systemctl enable journalapi
sudo systemctl start journalapi
```

## Security Considerations

- Restrict security group access to trusted IPs.
- Use strong secrets for `SECRET_KEY` and database passwords.
- Consider using AWS RDS for managed Postgres instead of containerized DB.

---

This completes the deployment setup for EC2.
