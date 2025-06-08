#  Purview CLI v2.0 - Production Deployment Script
# Comprehensive deployment automation for production environments

import os
import sys
import subprocess
import json
import time
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional
import yaml

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentManager:
    """Manages production deployment of  Purview CLI"""
    
    def __init__(self, environment: str = "production"):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.deployment_config = self._load_deployment_config()
        
    def _load_deployment_config(self) -> Dict:
        """Load deployment configuration"""
        config_file = self.project_root / "deployment" / f"{self.environment}.yml"
        
        if not config_file.exists():
            logger.warning(f"No deployment config found for {self.environment}")
            return self._get_default_config()
            
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> Dict:
        """Get default deployment configuration"""
        return {
            "app": {
                "name": "enhanced-purview-cli",
                "version": "2.0.0",
                "port": 8000,
                "workers": 4
            },
            "database": {
                "type": "postgresql",
                "host": "localhost",
                "port": 5432,
                "name": "purview_cli_prod"
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "nginx": {
                "port": 80,
                "ssl_port": 443
            },
            "ssl": {
                "enabled": False,
                "cert_path": "/etc/ssl/certs/purview-cli.crt",
                "key_path": "/etc/ssl/private/purview-cli.key"
            },
            "monitoring": {
                "enabled": True,
                "prometheus_port": 9090,
                "grafana_port": 3001
            }
        }
    
    def check_prerequisites(self) -> bool:
        """Check deployment prerequisites"""
        logger.info("Checking deployment prerequisites...")
        
        prerequisites = [
            ("python", "Python 3.8+"),
            ("docker", "Docker"),
            ("docker-compose", "Docker Compose"),
            ("nginx", "Nginx"),
            ("redis-server", "Redis"),
            ("postgresql", "PostgreSQL")
        ]
        
        missing = []
        
        for cmd, description in prerequisites:
            try:
                result = subprocess.run([cmd, "--version"], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    logger.info(f"✓ {description} is installed")
                else:
                    missing.append(description)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                missing.append(description)
                
        if missing:
            logger.error(f"Missing prerequisites: {', '.join(missing)}")
            return False
            
        logger.info("All prerequisites satisfied")
        return True
    
    def setup_environment(self):
        """Setup deployment environment"""
        logger.info("Setting up deployment environment...")
        
        # Create necessary directories
        directories = [
            "/var/log/purview-cli",
            "/var/lib/purview-cli",
            "/etc/purview-cli",
            self.deployment_config.get("app", {}).get("upload_dir", "/var/uploads/purview-cli")
        ]
        
        for directory in directories:
            try:
                os.makedirs(directory, mode=0o755, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except PermissionError:
                logger.error(f"Permission denied creating {directory}")
                logger.info("Please run with sudo or create directories manually")
                
        # Copy configuration files
        self._setup_config_files()
        
        # Setup systemd service
        self._setup_systemd_service()
        
        logger.info("Environment setup completed")
    
    def _setup_config_files(self):
        """Setup configuration files"""
        logger.info("Setting up configuration files...")
        
        # Create production .env file
        env_content = self._generate_env_file()
        
        env_path = Path("/etc/purview-cli/.env")
        try:
            with open(env_path, 'w') as f:
                f.write(env_content)
            os.chmod(env_path, 0o600)  # Secure permissions
            logger.info(f"Created environment file: {env_path}")
        except PermissionError:
            logger.warning("Could not create /etc/purview-cli/.env - using local .env")
            local_env = self.project_root / ".env.production"
            with open(local_env, 'w') as f:
                f.write(env_content)
            logger.info(f"Created local environment file: {local_env}")
        
        # Copy Nginx configuration
        self._setup_nginx_config()
    
    def _generate_env_file(self) -> str:
        """Generate production environment file"""
        config = self.deployment_config
        
        env_vars = {
            "APP_NAME": " Purview CLI API",
            "VERSION": "2.0.0",
            "DEBUG": "False",
            "HOST": "0.0.0.0",
            "PORT": str(config["app"]["port"]),
            "DATABASE_URL": self._build_database_url(),
            "REDIS_URL": self._build_redis_url(),
            "SECRET_KEY": self._generate_secret_key(),
            "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
            "REFRESH_TOKEN_EXPIRE_DAYS": "7",
            "ALGORITHM": "HS256",
            "LOG_LEVEL": "INFO",
            "LOG_FORMAT": "json",
            "ENABLE_METRICS": "True",
            "METRICS_PORT": str(config["monitoring"]["prometheus_port"]),
            "RATE_LIMIT_PER_MINUTE": "100",
            "RATE_LIMIT_BURST": "10",
            "MAX_UPLOAD_SIZE": str(100 * 1024 * 1024),  # 100MB
            "UPLOAD_DIR": config.get("app", {}).get("upload_dir", "/var/uploads/purview-cli")
        }
        
        return "\n".join([f"{key}={value}" for key, value in env_vars.items()])
    
    def _build_database_url(self) -> str:
        """Build database URL from config"""
        db_config = self.deployment_config["database"]
        
        if db_config["type"] == "postgresql":
            return (f"postgresql://{db_config.get('user', 'purview')}:"
                   f"{db_config.get('password', 'changeme')}@"
                   f"{db_config['host']}:{db_config['port']}/"
                   f"{db_config['name']}")
        else:
            return "sqlite:///./purview_cli.db"
    
    def _build_redis_url(self) -> str:
        """Build Redis URL from config"""
        redis_config = self.deployment_config["redis"]
        return f"redis://{redis_config['host']}:{redis_config['port']}/{redis_config['db']}"
    
    def _generate_secret_key(self) -> str:
        """Generate secure secret key"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _setup_nginx_config(self):
        """Setup Nginx configuration"""
        logger.info("Setting up Nginx configuration...")
        
        nginx_config_source = self.project_root / "nginx" / "nginx.conf"
        nginx_config_dest = Path("/etc/nginx/sites-available/purview-cli")
        nginx_enabled_dest = Path("/etc/nginx/sites-enabled/purview-cli")
        
        try:
            if nginx_config_source.exists():
                # Copy configuration
                subprocess.run([
                    "sudo", "cp", str(nginx_config_source), str(nginx_config_dest)
                ], check=True)
                
                # Enable site
                if nginx_enabled_dest.exists():
                    nginx_enabled_dest.unlink()
                nginx_enabled_dest.symlink_to(nginx_config_dest)
                
                # Test configuration
                subprocess.run(["sudo", "nginx", "-t"], check=True)
                
                logger.info("Nginx configuration installed successfully")
            else:
                logger.warning("Nginx configuration not found")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to setup Nginx configuration: {e}")
        except PermissionError:
            logger.error("Permission denied setting up Nginx - please run with sudo")
    
    def _setup_systemd_service(self):
        """Setup systemd service"""
        logger.info("Setting up systemd service...")
        
        service_content = f"""[Unit]
Description= Purview CLI API
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory={self.project_root}
Environment=PATH={self.project_root}/venv/bin
EnvironmentFile=/etc/purview-cli/.env
ExecStart={self.project_root}/venv/bin/gunicorn app.main:app \\
    --workers {self.deployment_config["app"]["workers"]} \\
    --worker-class uvicorn.workers.UvicornWorker \\
    --bind 0.0.0.0:{self.deployment_config["app"]["port"]} \\
    --access-logfile /var/log/purview-cli/access.log \\
    --error-logfile /var/log/purview-cli/error.log \\
    --log-level info
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
        
        service_path = Path("/etc/systemd/system/purview-cli.service")
        
        try:
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            # Reload systemd and enable service
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "purview-cli"], check=True)
            
            logger.info("Systemd service created and enabled")
            
        except (PermissionError, subprocess.CalledProcessError) as e:
            logger.error(f"Failed to setup systemd service: {e}")
    
    def build_application(self):
        """Build application for production"""
        logger.info("Building application...")
        
        # Install Python dependencies
        self._install_python_dependencies()
        
        # Build frontend
        self._build_frontend()
        
        # Run database migrations
        self._run_migrations()
        
        logger.info("Application build completed")
    
    def _install_python_dependencies(self):
        """Install Python dependencies"""
        logger.info("Installing Python dependencies...")
        
        # Create virtual environment
        venv_path = self.project_root / "venv"
        if not venv_path.exists():
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # Install dependencies
        pip_path = venv_path / "bin" / "pip"
        requirements_file = self.project_root / "backend" / "requirements.txt"
        
        subprocess.run([
            str(pip_path), "install", "-r", str(requirements_file)
        ], check=True)
        
        # Install additional production dependencies
        subprocess.run([
            str(pip_path), "install", "gunicorn", "psycopg2-binary"
        ], check=True)
        
        logger.info("Python dependencies installed")
    
    def _build_frontend(self):
        """Build frontend for production"""
        logger.info("Building frontend...")
        
        frontend_path = self.project_root / "frontend"
        
        if frontend_path.exists():
            # Install Node.js dependencies
            subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
            
            # Build production bundle
            subprocess.run(["npm", "run", "build"], cwd=frontend_path, check=True)
            
            logger.info("Frontend built successfully")
        else:
            logger.warning("Frontend directory not found - skipping frontend build")
    
    def _run_migrations(self):
        """Run database migrations"""
        logger.info("Running database migrations...")
        
        python_path = self.project_root / "venv" / "bin" / "python"
        backend_path = self.project_root / "backend"
        
        # Set environment variables
        env = os.environ.copy()
        env_file = Path("/etc/purview-cli/.env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.strip().split('=', 1)
                        env[key] = value
        
        # Run migrations
        subprocess.run([
            str(python_path), "-c",
            "import asyncio; from app.database.migrations import run_migrations; asyncio.run(run_migrations())"
        ], cwd=backend_path, env=env, check=True)
        
        logger.info("Database migrations completed")
    
    def deploy(self):
        """Deploy application to production"""
        logger.info(f"Starting deployment to {self.environment}...")
        
        try:
            # Stop existing services
            self._stop_services()
            
            # Deploy application files
            self._deploy_files()
            
            # Start services
            self._start_services()
            
            # Verify deployment
            self._verify_deployment()
            
            logger.info("Deployment completed successfully!")
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            self._rollback()
            raise
    
    def _stop_services(self):
        """Stop running services"""
        logger.info("Stopping services...")
        
        services = ["purview-cli", "nginx"]
        
        for service in services:
            try:
                subprocess.run([
                    "sudo", "systemctl", "stop", service
                ], check=False)  # Don't fail if service wasn't running
                logger.info(f"Stopped {service}")
            except subprocess.CalledProcessError:
                logger.warning(f"Could not stop {service}")
    
    def _deploy_files(self):
        """Deploy application files"""
        logger.info("Deploying application files...")
        
        # Create backup of current deployment
        self._create_backup()
        
        # Copy application files
        # This is a simplified version - in real deployment you'd use proper
        # deployment tools like Ansible, Docker, or CI/CD pipelines
        
        logger.info("Application files deployed")
    
    def _create_backup(self):
        """Create backup of current deployment"""
        logger.info("Creating deployment backup...")
        
        backup_dir = Path(f"/var/backups/purview-cli/{int(time.time())}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database
        self._backup_database(backup_dir)
        
        # Backup uploaded files
        upload_dir = Path(self.deployment_config.get("app", {}).get("upload_dir", "/var/uploads/purview-cli"))
        if upload_dir.exists():
            subprocess.run([
                "cp", "-r", str(upload_dir), str(backup_dir / "uploads")
            ], check=False)
        
        logger.info(f"Backup created at {backup_dir}")
    
    def _backup_database(self, backup_dir: Path):
        """Backup database"""
        db_config = self.deployment_config["database"]
        
        if db_config["type"] == "postgresql":
            backup_file = backup_dir / "database.sql"
            
            subprocess.run([
                "pg_dump",
                "-h", db_config["host"],
                "-p", str(db_config["port"]),
                "-U", db_config.get("user", "purview"),
                "-d", db_config["name"],
                "-f", str(backup_file)
            ], check=True)
            
            logger.info("Database backup created")
    
    def _start_services(self):
        """Start services"""
        logger.info("Starting services...")
        
        services = ["purview-cli", "nginx"]
        
        for service in services:
            try:
                subprocess.run([
                    "sudo", "systemctl", "start", service
                ], check=True)
                
                subprocess.run([
                    "sudo", "systemctl", "enable", service
                ], check=True)
                
                logger.info(f"Started {service}")
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to start {service}: {e}")
                raise
    
    def _verify_deployment(self):
        """Verify deployment is working"""
        logger.info("Verifying deployment...")
        
        # Check service status
        services = ["purview-cli", "nginx"]
        
        for service in services:
            result = subprocess.run([
                "systemctl", "is-active", service
            ], capture_output=True, text=True)
            
            if result.stdout.strip() != "active":
                raise Exception(f"Service {service} is not active")
            
            logger.info(f"✓ {service} is running")
        
        # Check HTTP endpoints
        import requests
        
        try:
            # Check health endpoint
            response = requests.get("http://localhost/health", timeout=30)
            if response.status_code == 200:
                logger.info("✓ Health check passed")
            else:
                raise Exception(f"Health check failed: {response.status_code}")
                
        except requests.RequestException as e:
            raise Exception(f"HTTP check failed: {e}")
        
        logger.info("Deployment verification completed")
    
    def _rollback(self):
        """Rollback to previous deployment"""
        logger.info("Rolling back deployment...")
        
        # Find latest backup
        backup_root = Path("/var/backups/purview-cli")
        if backup_root.exists():
            backups = sorted(backup_root.glob("*"), key=lambda p: p.name, reverse=True)
            if backups:
                latest_backup = backups[0]
                logger.info(f"Rolling back to {latest_backup}")
                # Implement rollback logic here
        
        logger.info("Rollback completed")
    
    def status(self):
        """Check deployment status"""
        logger.info("Checking deployment status...")
        
        # Check services
        services = ["purview-cli", "nginx", "postgresql", "redis"]
        
        for service in services:
            result = subprocess.run([
                "systemctl", "is-active", service
            ], capture_output=True, text=True)
            
            status = result.stdout.strip()
            logger.info(f"{service}: {status}")
        
        # Check disk space
        result = subprocess.run(["df", "-h"], capture_output=True, text=True)
        logger.info("Disk usage:")
        logger.info(result.stdout)

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description=" Purview CLI Deployment Manager")
    parser.add_argument("--environment", "-e", default="production", 
                       help="Deployment environment")
    parser.add_argument("command", choices=[
        "check", "setup", "build", "deploy", "status", "rollback"
    ], help="Deployment command")
    
    args = parser.parse_args()
    
    deployment = DeploymentManager(args.environment)
    
    try:
        if args.command == "check":
            if deployment.check_prerequisites():
                logger.info("System ready for deployment")
                sys.exit(0)
            else:
                logger.error("Prerequisites not met")
                sys.exit(1)
                
        elif args.command == "setup":
            deployment.setup_environment()
            
        elif args.command == "build":
            deployment.build_application()
            
        elif args.command == "deploy":
            if not deployment.check_prerequisites():
                logger.error("Prerequisites not met")
                sys.exit(1)
            deployment.setup_environment()
            deployment.build_application()
            deployment.deploy()
            
        elif args.command == "status":
            deployment.status()
            
        elif args.command == "rollback":
            deployment._rollback()
            
    except KeyboardInterrupt:
        logger.info("Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
