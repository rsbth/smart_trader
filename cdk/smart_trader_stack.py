from constructs import Construct
from aws_cdk import (
    Stack,
    Duration,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_elasticache as elasticache,
    aws_rds as rds,
    aws_secretsmanager as secretsmanager,
    aws_logs as logs,
    aws_certificatemanager as acm,
    aws_route53 as route53,
    aws_route53_targets as targets
)

class SmartTraderStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # VPC
        vpc = ec2.Vpc(self, "SmartTraderVPC",
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                )
            ]
        )

        # ECS Cluster
        cluster = ecs.Cluster(self, "SmartTraderCluster",
            vpc=vpc,
            container_insights=True
        )

        # Redis for Session Management
        redis_subnet_group = elasticache.CfnSubnetGroup(self, "RedisSubnetGroup",
            subnet_ids=vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS).subnet_ids,
            description="Subnet group for Redis"
        )

        redis_security_group = ec2.SecurityGroup(self, "RedisSecurityGroup",
            vpc=vpc,
            description="Security group for Redis cluster",
            allow_all_outbound=True
        )

        redis_cluster = elasticache.CfnCacheCluster(self, "SmartTraderRedis",
            cache_node_type="cache.t3.micro",
            engine="redis",
            num_cache_nodes=1,
            cluster_name="smart-trader-redis",
            vpc_security_group_ids=[redis_security_group.security_group_id],
            cache_subnet_group_name=redis_subnet_group.ref
        )

        # RDS for Database
        db_credentials = secretsmanager.Secret(self, "DBCredentials",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template='{"username": "admin"}',
                generate_string_key="password",
                exclude_characters="\"@/\\"
            )
        )

        db_security_group = ec2.SecurityGroup(self, "DatabaseSecurityGroup",
            vpc=vpc,
            description="Security group for RDS instance",
            allow_all_outbound=True
        )

        database = rds.DatabaseInstance(self, "SmartTraderDatabase",
            engine=rds.DatabaseInstanceEngine.postgres(version=rds.PostgresEngineVersion.VER_13),
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS),
            security_groups=[db_security_group],
            credentials=rds.Credentials.from_secret(db_credentials),
            database_name="smarttrader",
            backup_retention=Duration.days(7),
            deletion_protection=True,
            removal_policy=RemovalPolicy.SNAPSHOT
        )

        # Fargate Service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "SmartTraderService",
            cluster=cluster,
            memory_limit_mib=1024,
            cpu=512,
            desired_count=2,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=ecs.ContainerImage.from_asset("../"),
                container_port=5000,
                environment={
                    "REDIS_HOST": redis_cluster.attr_redis_endpoint_address,
                    "DB_HOST": database.instance_endpoint.hostname,
                    "DB_NAME": "smarttrader",
                    "DB_USER": db_credentials.secret_value_from_json("username").to_string(),
                    "FLASK_ENV": "production"
                },
                secrets={
                    "DB_PASSWORD": ecs.Secret.from_secrets_manager(db_credentials, "password"),
                    "ANGEL_API_KEY": ecs.Secret.from_secrets_manager(
                        secretsmanager.Secret.from_secret_name_v2(self, "AngelAPIKey", "angel-api-key")
                    ),
                    "ANGEL_CLIENT_ID": ecs.Secret.from_secrets_manager(
                        secretsmanager.Secret.from_secret_name_v2(self, "AngelClientID", "angel-client-id")
                    ),
                    "ANGEL_PIN": ecs.Secret.from_secrets_manager(
                        secretsmanager.Secret.from_secret_name_v2(self, "AngelPIN", "angel-pin")
                    ),
                    "ANGEL_TOTP_KEY": ecs.Secret.from_secrets_manager(
                        secretsmanager.Secret.from_secret_name_v2(self, "AngelTOTPKey", "angel-totp-key")
                    )
                },
                log_driver=ecs.LogDrivers.aws_logs(
                    stream_prefix="SmartTrader",
                    log_retention=logs.RetentionDays.ONE_MONTH
                )
            ),
            public_load_balancer=True,
            certificate=acm.Certificate.from_certificate_arn(
                self, "Certificate",
                certificate_arn="arn:aws:acm:region:account:certificate/certificate-id"
            ),
            domain_name="smarttrader.yourdomain.com",
            domain_zone=route53.HostedZone.from_hosted_zone_attributes(
                self, "HostedZone",
                hosted_zone_id="your-hosted-zone-id",
                zone_name="yourdomain.com"
            )
        )

        # Security group rules
        redis_security_group.add_ingress_rule(
            fargate_service.service.connections.security_groups[0],
            ec2.Port.tcp(6379),
            "Allow access from Fargate service"
        )

        db_security_group.add_ingress_rule(
            fargate_service.service.connections.security_groups[0],
            ec2.Port.tcp(5432),
            "Allow access from Fargate service"
        )

        # Auto Scaling
        scaling = fargate_service.service.auto_scale_task_count(
            max_capacity=4,
            min_capacity=2
        )

        scaling.scale_on_cpu_utilization("CpuScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )

        scaling.scale_on_memory_utilization("MemoryScaling",
            target_utilization_percent=70,
            scale_in_cooldown=Duration.seconds(60),
            scale_out_cooldown=Duration.seconds(60)
        )
