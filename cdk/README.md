# Smart Trader Infrastructure

This directory contains the AWS CDK infrastructure code for deploying the Smart Trader application.

## Prerequisites

1. AWS CLI installed and configured
2. AWS CDK CLI installed
3. Python 3.8 or higher
4. Docker installed (for local testing)

## Environment Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

3. Configure AWS credentials:
```bash
aws configure
```

4. Bootstrap CDK (first time only):
```bash
cdk bootstrap
```

## Configuration

Before deploying, update the following in `smart_trader_stack.py`:

1. Replace `certificate_arn` with your ACM certificate ARN
2. Replace `hosted_zone_id` and `zone_name` with your Route53 hosted zone details
3. Update the domain name in `domain_name`

## Deployment

1. Synthesize the CloudFormation template:
```bash
cdk synth
```

2. Deploy the stack:
```bash
cdk deploy
```

## Infrastructure Components

- VPC with public and private subnets
- ECS Fargate cluster
- Application Load Balancer
- RDS PostgreSQL database
- Redis ElastiCache cluster
- Secrets Manager for credentials
- CloudWatch Logs
- Auto Scaling
- Route53 DNS records
- ACM Certificate

## Security

All sensitive information (API keys, database credentials) are stored in AWS Secrets Manager.
The application runs in private subnets with controlled access through security groups.

## Monitoring

- CloudWatch Container Insights enabled
- Application logs available in CloudWatch Logs
- ALB access logs
- RDS performance insights

## Cleanup

To destroy the infrastructure:
```bash
cdk destroy
```

Note: This will not delete the RDS snapshots or ECR images.
