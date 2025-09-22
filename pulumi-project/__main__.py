"""An AWS Python Pulumi program"""

import pulumi

# Use these to test using the resource by component package (i.e. over RPC)
from pulumi_custom_resource_provider import (
    VPC,
    VPCArgs,
    EC2SecurityGroup,
    EC2SecurityGroupArgs,
    EC2SecurityGroupIngressRuleArgs,
    EC2SecurityGroupRuleProtocol,
)

# This works totally fine, however
# from custom_component_module import (
#     VPC,
#     VPCArgs,
#     EC2SecurityGroup,
#     EC2SecurityGroupArgs,
#     EC2SecurityGroupIngressRule as EC2SecurityGroupIngressRuleArgs,
#     EC2SecurityGroupRuleProtocol,
# )

config = pulumi.Config()
ipv4_cidr_block = config.require("ipv4_cidr_block")

# Create an AWS resource (S3 Bucket)
vpc = VPC(
    'my-vpc',
    args=VPCArgs(
        name='my-vpc',
        ipv4_cidr_block=ipv4_cidr_block,
        enable_ipv6=True,
        tags={
            'Environment': 'Dev',
            'Owner': 'Alice',
        }
    )
)

security_group = EC2SecurityGroup(
    'my-security-group',
    args=EC2SecurityGroupArgs(
        name='my-security-group',
        description='My security group',
        vpc_id=vpc.vpc_id,
        ingress_rules={
            'ssh': EC2SecurityGroupIngressRuleArgs(
                name="ssh",
                from_port=22,
                to_port=22,
                protocol=EC2SecurityGroupRuleProtocol.TCP,
                ipv4_cidr_block=vpc.ipv4_cidr_block,
                description='Allow SSH access from within the VPC',
            ),
            'ssh-ipv6': EC2SecurityGroupIngressRuleArgs(
                name="ssh",
                from_port=22,
                to_port=22,
                protocol=EC2SecurityGroupRuleProtocol.TCP,
                ipv6_cidr_block=vpc.ipv6_cidr_block,
                description='Allow SSH access from within the VPC',
            ),
        },
    ),
)
