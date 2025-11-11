# Odoo 18 Enterprise Application

Enterprise-grade Odoo 18 deployment with modern DevOps practices, monitoring, and CI/CD automation.

## Architecture

- **Application**: Odoo 18.0
- **Database**: PostgreSQL 15
- **Containerization**: Docker & Docker Compose
- **Monitoring**: Prometheus + Grafana
- **CI/CD**: GitHub Actions
- **Reverse Proxy**: Nginx with SSL

## Quick Start

```bash
# Clone the repository
git clone <your-repo-url>
cd <project-directory>

# Copy environment file
cp .env.example .env

# Edit .env with your configuration
nano .env

# Start the application
docker-compose up -d

# View logs
docker-compose logs -f odoo
```

Access Odoo at: `http://your-server-ip:8069`

## Project Structure

```
.
├── addons/                    # Custom Odoo modules
│   ├── default_apps_page/
│   ├── ica_web_responsive/
│   └── ica_website_theme/
├── .github/
│   └── workflows/
│       └── ci-cd.yml         # CI/CD pipeline
├── monitoring/               # Prometheus & Grafana configs
├── nginx/                    # Nginx reverse proxy configs
├── docker-compose.yml        # Main docker configuration
├── .env.example             # Environment variables template
└── README.md

```

## Custom Modules

### 1. default_apps_page
Default apps page configuration for Odoo users.

### 2. ica_web_responsive
Responsive web interface with dark mode support.

### 3. ica_website_theme
Custom website theme with portfolio and services pages.

## Development Workflow

### Local Development
```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f

# Restart Odoo after code changes
docker-compose restart odoo

# Access Odoo shell
docker-compose exec odoo odoo shell
```

### Code Quality
```bash
# Run linting
flake8 addons/

# Format code
black addons/

# Sort imports
isort addons/
```

## CI/CD Pipeline

The project uses GitHub Actions for automated testing and deployment:

1. **Lint & Test**: Code quality checks and validation
2. **Build**: Docker image building and pushing to registry
3. **Security Scan**: Vulnerability scanning with Trivy
4. **Deploy**: Automated deployment to staging/production

## Monitoring Stack

### Prometheus
- Metrics collection from Odoo and PostgreSQL
- Access: `http://your-server:9090`

### Grafana
- Visualization dashboards
- Pre-configured dashboards for Odoo metrics
- Access: `http://your-server:3000`
- Default credentials: admin/admin

## Production Deployment

### Prerequisites
- Docker and Docker Compose installed
- Domain name configured
- SSL certificate (Let's Encrypt recommended)

### Steps
```bash
# 1. Clone repository
git clone <your-repo-url>
cd <project-directory>

# 2. Configure environment
cp .env.example .env
nano .env

# 3. Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 4. Configure SSL
./scripts/setup-ssl.sh

# 5. Verify deployment
docker-compose ps
```

## Backup & Recovery

### Database Backup
```bash
# Manual backup
docker-compose exec db pg_dump -U odoo postgres > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T db psql -U odoo postgres < backup_20240101.sql
```

### Automated Backups
Configured in `docker-compose.yml` to run daily backups.

## Scaling

### Horizontal Scaling
```bash
# Scale Odoo workers
docker-compose up -d --scale odoo=3
```

### Resource Limits
Adjust in `docker-compose.yml`:
- Memory limits
- CPU limits
- Worker configuration

## Troubleshooting

### Common Issues

**Odoo won't start**
```bash
# Check logs
docker-compose logs odoo

# Verify database connection
docker-compose exec odoo ping db
```

**Database connection errors**
```bash
# Check PostgreSQL status
docker-compose ps db
docker-compose logs db
```

**Port conflicts**
```bash
# Check ports in use
sudo netstat -tlnp | grep -E '8069|5432'
```

## Security Best Practices

1. Change default passwords in `.env`
2. Use strong database passwords
3. Enable firewall rules
4. Keep Docker images updated
5. Regular security audits with Trivy
6. SSL/TLS encryption for production

## Performance Tuning

### Odoo Configuration
- Workers: Adjust based on CPU cores
- Memory limits: Set according to available RAM
- Database connections: Tune PostgreSQL max_connections

### PostgreSQL Optimization
```sql
-- In postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is proprietary. All rights reserved.

## Support

For issues and questions:
- Open an issue on GitHub
- Email: support@yourdomain.com

## Changelog

### Version 1.0.0 (2024-11-11)
- Initial release
- Docker containerization
- CI/CD pipeline setup
- Monitoring stack integration
- Custom modules implementation
