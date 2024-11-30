#!/usr/bin/env python3
import os
from aws_cdk import App
from smart_trader_stack import SmartTraderStack

app = App()
SmartTraderStack(app, "SmartTraderStack",
    env={
        'account': os.environ.get('CDK_DEFAULT_ACCOUNT'),
        'region': os.environ.get('CDK_DEFAULT_REGION', 'ap-south-1')
    }
)

app.synth()
