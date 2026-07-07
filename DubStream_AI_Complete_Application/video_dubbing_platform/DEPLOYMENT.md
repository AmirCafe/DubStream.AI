# DubStream AI - Deployment Guide

## Option 1: Railway.app (Easiest - 5 minutes)

```bash
# 1. Sign up at https://railway.app
# 2. Connect your GitHub repository
# 3. Create new project from repo
# 4. Set environment variables from .env.example
# 5. Deploy button → Live in 5 minutes
```

**Cost:** $5-15/month for small setup

## Option 2: Self-Hosted VPS (DigitalOcean/Linode - 30 minutes)

```bash
# 1. Create Ubuntu 22.04 LTS server ($20/month)
# 2. SSH in and run:

curl -fsSL https://get.docker.com | sh
git clone <your-repo>
cd dubstream_ai
cp .env.example .env

# 3. Edit .env with production values
nano .env

# 4. Start services
docker-compose -f docker-compose.prod.yml up -d

# 5. Set up Nginx reverse proxy
sudo apt install -y nginx certbot python3-certbot-nginx

# 6. Configure Nginx (see nginx.conf.example)
sudo cp nginx.conf.example /etc/nginx/sites-available/dubstream
sudo ln -s /etc/nginx/sites-available/dubstream /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx

# 7. Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

**Cost:** $20-40/month

## Option 3: Kubernetes (AWS EKS/GKE)

```bash
# Using Helm chart in /deploy/helm/
helm install dubstream ./deploy/helm/dubstream \
  -f values-prod.yaml \
  --set stripe.key=$STRIPE_KEY
```

## Option 4: AWS (Terraform)

```bash
# Using Terraform in /deploy/terraform/
terraform init
terraform plan
terraform apply
```

## Verifying Deployment

```bash
# Check services
curl https://yourdomain.com/health
# Should return: {"status":"ok",...}

# Check API docs
https://yourdomain.com/api/docs

# Check database
psql postgresql://user:pass@host/dubstream -c "SELECT COUNT(*) FROM users;"

# Check Stripe webhook
curl -X POST https://yourdomain.com/api/payments/webhook \
  -H "stripe-signature: test"
```

## Production Checklist

- [ ] Database backed up daily
- [ ] SSL certificate installed
- [ ] Stripe keys configured
- [ ] AWS/R2 credentials set
- [ ] Sentry DSN added
- [ ] CORS origins updated
- [ ] Rate limits configured
- [ ] Email alerts enabled
- [ ] Monitoring dashboard set up
- [ ] Backup strategy documented

