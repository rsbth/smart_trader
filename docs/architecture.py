from diagrams import Diagram, Cluster
from diagrams.aws.compute import ECS, ElasticContainerServiceContainer
from diagrams.aws.database import RDS, ElastiCache
from diagrams.aws.network import ELB, Route53, VPC
from diagrams.aws.security import SecretsManager, ACM
from diagrams.aws.integration import ApplicationIntegration
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import S3
from diagrams.programming.framework import Flask
from diagrams.generic.network import Firewall

with Diagram("Smart Trader Architecture", show=False, direction="TB"):
    # DNS and Certificate
    dns = Route53("Route 53")
    cert = ACM("SSL Certificate")

    # Load Balancer
    alb = ELB("Application Load Balancer")

    # Connect DNS and Cert to ALB
    dns >> cert >> alb

    with Cluster("VPC"):
        # Security and Monitoring
        secrets = SecretsManager("Secrets Manager")
        cloudwatch = Cloudwatch("CloudWatch")
        
        with Cluster("ECS Cluster"):
            # ECS Service
            service = ECS("ECS Service")
            
            # Task containers
            with Cluster("Task Definition"):
                containers = ElasticContainerServiceContainer("Smart Trader App")
            
            service >> containers
        
        # Database and Cache
        with Cluster("Data Layer"):
            db = RDS("PostgreSQL")
            cache = ElastiCache("Redis")
        
        # Application components
        with Cluster("Application Components"):
            with Cluster("Analysis Modules"):
                sentiment = Flask("Sentiment Analysis")
                technical = Flask("Technical Analysis")
                fundamental = Flask("Fundamental Analysis")
            
            with Cluster("Trading Module"):
                broker = Flask("Broker Integration")
                trading = Flask("Trading Engine")
        
        # Event Processing
        events = ApplicationIntegration("Event Bridge")
        
        # Connect components
        alb >> service
        containers >> sentiment >> db
        containers >> technical >> db
        containers >> fundamental >> db
        containers >> trading >> broker
        broker >> events
        containers >> cache
        
        # Security and monitoring connections
        containers >> secrets
        containers >> cloudwatch
