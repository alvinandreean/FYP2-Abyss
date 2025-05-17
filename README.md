# Main Repository for MCS11 - Topic: Abyss AI Meets the dark side

## Quick Start Guide

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed on your system

### Running the Application

1. **Install Docker Desktop**
   - Download and install from [Docker's official website](https://www.docker.com/products/docker-desktop/)
   - Start Docker Desktop after installation

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd FYP2-Abyss
   ```

3. **Run the application**
   ```bash
   # Using the newer Docker CLI syntax
   docker compose up --build
   
   # OR if using older Docker Compose
   docker-compose up --build
   ```

4. **Access the website**
   - Open your web browser and go to: [http://localhost](http://localhost)
   - The application is now running!

5. **Stop the application**
   - Press `Ctrl+C` in the terminal where Docker is running
   - Or run `docker compose down` in a new terminal

### Troubleshooting

- Make sure Docker Desktop is running before executing commands
- If you see "docker-compose not recognized", use `docker compose` (with a space) instead
- If you have port conflicts, modify the port mappings in `docker-compose.yml`

## Detailed Docker Deployment Instructions

For more detailed instructions on Docker deployment, please see [DOCKER.md](DOCKER.md).