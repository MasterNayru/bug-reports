"""AWS My Security Group Pulumi module."""

from enum import Enum

import pulumi
import pulumi_aws.ec2
import pulumi_aws.vpc
import pydantic

from ._types import (
    Input,
    Output,
    PulumiComponentResource,
    PulumiResourceArgs,
    PulumiResourceConfigArgs,
)
from ._types import (
    T as T,
)
from ._typing import Mapping, Self


class EC2SecurityGroupRuleProtocol(str, Enum):
    """Enum for supported protocols in security group rules."""

    TCP = "tcp"
    UDP = "udp"
    ICMP = "icmp"
    ALL = "all"
    ANY = "-1"


class EC2SecurityGroupEgressRule(PulumiResourceConfigArgs):
    """Config for an AWS My Security Group ingress rule."""

    name: str
    """The name of the rule. Must be in kebab-case format."""
    description: str
    """The description of the rule."""
    protocol: EC2SecurityGroupRuleProtocol
    """The protocol for the rule. Can be 'tcp', 'udp', 'icmp', 'all', or '-1'."""
    from_port: int | None = None
    """The start port of the range for the rule."""
    to_port: int | None = None
    """The end port of the range for the rule."""
    destination_security_group_id: Input[str] | None = None
    """The destination security group ID this rule applies to."""
    ipv4_cidr_block: Input[str] | None = None
    """The IPv4 CIDR block this rule applies to."""
    ipv6_cidr_block: Input[str] | None = None
    """The IPv6 CIDR block this rule applies to."""
    prefix_list_id: Input[str] | None = None
    """The prefix list ID this rule applies to."""
    tags: Mapping[str, Input[str]] | None = None
    """The tags for the rule."""

    @pydantic.model_validator(mode="after")
    def validate_rule_attributes(self) -> Self:
        """Validate the rule attributes."""
        # Ensure that only one of the following is set
        set_attributes = [
            self.destination_security_group_id,
            self.ipv4_cidr_block,
            self.ipv6_cidr_block,
            self.prefix_list_id,
        ]
        if sum(attr is not None for attr in set_attributes) != 1:
            raise ValueError(
                "One and only one of destination_security_group_id, "
                "ipv4_cidr_block, ipv6_cidr_block, or prefix_list_id must be set."
            )

        if self.protocol in ["-1", "all"]:
            if self.from_port == -1:
                self.from_port = 0
            if self.to_port == -1:
                self.to_port = 0
        elif self.protocol in ["icmp"]:
            if self.to_port != -1:
                self.to_port = -1
        else:
            if self.from_port == -1:
                self.from_port = 0
            if self.to_port == -1:
                self.to_port = 65535

        return self


class EC2SecurityGroupIngressRule(PulumiResourceConfigArgs):
    """Config for an AWS My Security Group ingress rule."""

    name: str
    """The name of the rule. Must be in kebab-case format."""
    description: str
    """The description of the rule."""
    protocol: EC2SecurityGroupRuleProtocol
    """The protocol for the rule. Can be 'tcp', 'udp', 'icmp', 'all', or '-1'."""
    from_port: int | None = None
    """The start port of the range for the rule."""
    to_port: int | None = None
    """The end port of the range for the rule."""
    source_security_group_id: Input[str] | None = None
    """The source security group ID this rule applies to."""
    ipv4_cidr_block: Input[str] | None = None
    """The IPv4 CIDR block this rule applies to."""
    ipv6_cidr_block: Input[str] | None = None
    """The IPv6 CIDR block this rule applies to."""
    prefix_list_id: Input[str] | None = None
    """The prefix list ID this rule applies to."""
    tags: Mapping[str, Input[str]] | None = None
    """The tags for the rule."""

    @pydantic.model_validator(mode="after")
    def validate_rule_attributes(self) -> Self:
        """Validate the rule attributes."""
        # Ensure that one and only one of the following is set
        set_attributes = [
            self.source_security_group_id,
            self.ipv4_cidr_block,
            self.ipv6_cidr_block,
            self.prefix_list_id,
        ]
        if sum(attr is not None for attr in set_attributes) != 1:
            raise ValueError(
                "One and only one of source_security_group_id, "
                "ipv4_cidr_block, ipv6_cidr_block, or prefix_list_id must be set."
            )

        if self.protocol in ["-1", "all"]:
            if self.from_port == -1:
                self.from_port = 0
            if self.to_port == -1:
                self.to_port = 0
        elif self.protocol in ["icmp"]:
            if self.to_port != -1:
                self.to_port = -1
        else:
            if self.from_port == -1:
                self.from_port = 0
            if self.to_port == -1:
                self.to_port = 65535

        return self



def _default_egress_rules() -> Mapping[str, EC2SecurityGroupEgressRule]:
    """Return default egress rules.

    :returns: The default egress rules.
    """
    return {
        "all-all": EC2SecurityGroupEgressRule(
            name="all-all",
            description="Allow all outbound traffic",
            ipv4_cidr_block="0.0.0.0/0",
            protocol=EC2SecurityGroupRuleProtocol.ALL,
        ),
        "all-all-ipv6": EC2SecurityGroupEgressRule(
            name="all-all-ipv6",
            description="Allow all outbound IPv6 traffic",
            ipv6_cidr_block="::/0",
            protocol=EC2SecurityGroupRuleProtocol.ALL,
        ),
    }


class EC2SecurityGroupArgs(PulumiResourceArgs):
    """Config for an AWS My Security Group."""

    name: str
    """The name of the security group. Must be in kebab-case format."""
    vpc_id: Input[str] | None = None
    """The VPC ID to create the security group in."""
    description: str
    """The description of the security group."""
    ingress_rules: Mapping[str, EC2SecurityGroupIngressRule] | None = None
    """The ingress rules for the security group. The keys will be used in the Pulumi resource IDs and
    must be in kebab-case format."""
    egress_rules: Mapping[str, EC2SecurityGroupEgressRule] | None = None
    """The egress rules for the security group. The keys will be used in the Pulumi resource IDs and must be
    in kebab-case format."""
    tags: Mapping[str, Input[str]] | None = None
    """The tags to apply to the security group resource."""

    @pydantic.model_validator(mode="after")
    def set_default_values(self) -> Self:
        """Set default values for the security group arguments."""
        if not self.vpc_id:
            self.vpc_id = pulumi_aws.ec2.get_vpc(
                filters=[
                    pulumi_aws.ec2.GetVpcFilterArgs(
                        name="tag:VPCQualifier",
                        values=["default"],
                    )
                ]
            ).id

        if not self.ingress_rules:
            self.ingress_rules = {}

        if not self.egress_rules:
            self.egress_rules = _default_egress_rules()

        if not self.tags:
            self.tags = {}

        return self

    @pydantic.field_validator("tags")
    @classmethod
    def validate_name_tag_absent(cls, tags: Mapping[str, Input[str]] | None) -> Mapping[str, Input[str]]:
        """Validate that no name tag was provided explicitly."""
        if not tags:
            tags = {}

        if "Name" in tags:
            raise ValueError("The 'Name' tag should not be set explicitly. It is set automatically.")

        return tags


class EC2SecurityGroup(PulumiComponentResource):
    """AWS My Security Group."""

    security_group_id: Output[str]
    """The ID of the security group."""
    vpc_id: Output[str]
    """The VPC ID the security group is in."""

    def __init__(
        self,
        resource_id: str,
        args: EC2SecurityGroupArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        """AWS My Security Group."""
        super().__init__("custom:resource:SecurityGroup", resource_id, None, opts=opts)

        # When Pulumi instantiates our class by RPC, the data is actually received as a dict
        args = EC2SecurityGroupArgs.from_rpc(args)
        opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(parent=self))

        assert args.vpc_id is not None, f"{args.__class__}.vpc_id must not be None at this point"

        security_group = _security_group(
            resource_id,
            group_name=args.name,
            description=args.description,
            tags=args.tags,
            vpc_id=args.vpc_id,
            opts=opts,
        )

        pulumi_aws.ec2.Tag(
            f"{resource_id}-name",
            args=pulumi_aws.ec2.TagArgs(
                resource_id=security_group.id,
                key="Name",
                value=security_group.name,
            ),
            opts=opts,
        )

        ingress_rules = {}
        egress_rules = {}

        if args.ingress_rules is None:
            raise ValueError(f"{args.__class__}.ingress_rules must not be None at this point.")

        for ingress_rule_id, ingress_rule in args.ingress_rules.items():
            ingress_rules[ingress_rule_id] = _security_group_ingress_rule(
                f"{resource_id}-ingress-{ingress_rule_id}",
                security_group_id=security_group.id,
                name=ingress_rule.name,
                description=ingress_rule.description,
                ip_protocol=ingress_rule.protocol,
                to_port=ingress_rule.to_port,
                from_port=ingress_rule.from_port,
                prefix_list_id=ingress_rule.prefix_list_id,
                ipv4_cidr_block=ingress_rule.ipv4_cidr_block,
                ipv6_cidr_block=ingress_rule.ipv6_cidr_block,
                source_security_group_id=ingress_rule.source_security_group_id,
                tags=ingress_rule.tags,
                opts=pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(parent=security_group)),
            )

        if args.egress_rules is None:
            raise ValueError(f"{args.__class__}.egress_rules must not be None at this point.")

        for egress_rule_id, egress_rule in args.egress_rules.items():
            egress_rules[egress_rule_id] = _security_group_egress_rule(
                f"{resource_id}-egress-{egress_rule_id}",
                security_group_id=security_group.id,
                name=egress_rule.name,
                description=egress_rule.description,
                ip_protocol=egress_rule.protocol,
                to_port=egress_rule.to_port,
                from_port=egress_rule.from_port,
                prefix_list_id=egress_rule.prefix_list_id,
                ipv4_cidr_block=egress_rule.ipv4_cidr_block,
                ipv6_cidr_block=egress_rule.ipv6_cidr_block,
                destination_security_group_id=egress_rule.destination_security_group_id,
                tags=egress_rule.tags,
                opts=pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(parent=security_group)),
            )

        self.security_group_id = security_group.id
        """The ID of the security group."""
        self.vpc_id = security_group.vpc_id
        """The VPC ID the security group is in."""

        self.register_outputs(
            {
                "security-group-id": self.security_group_id,
                "vpc-id": self.vpc_id,
            },
        )


def _security_group(
    resource_id: str,
    vpc_id: Input[str],
    group_name: str,
    description: str | None = None,
    tags: Mapping[str, Input[str]] | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> pulumi_aws.ec2.SecurityGroup:
    """Returns an AWS My security group resource.

    This function does not allow setting rules directly on it as Pulumi
    advise against doing so. The security group created by this function
    should have ingress/egress rules added to it in separate resources.
    (Most people should not be using this function and instead should be
    using the EC2SecurityGroup Pulumi component resource that creates
    the right resources for you.)

    :param resource_id: The Pulumi identifier for the resource.
    :param vpc_id: The VPC ID.
    :param description: The description of the security group.
    :param group_name: The name of the security group.
    :param tags: The tags to apply to the resource.
    :param opts: A bag of options that control this resource's behavior.
    :returns: The Security Group resource.
    """
    if not tags:
        tags = {}

    args = pulumi_aws.ec2.SecurityGroupArgs(
        name=group_name,
        description=description,
        vpc_id=vpc_id,
    )

    args.tags = {
        "Name": group_name,
        **tags,
    }

    return pulumi_aws.ec2.SecurityGroup(
        resource_id,
        args=args,
        opts=opts,
    )


def _security_group_ingress_rule(
    resource_id: str,
    security_group_id: Input[str],
    name: str,
    description: str,
    ip_protocol: str,
    to_port: int | None = 0,
    from_port: int | None = 0,
    prefix_list_id: Input[str] | None = None,
    ipv4_cidr_block: Input[str] | None = None,
    ipv6_cidr_block: Input[str] | None = None,
    source_security_group_id: Input[str] | None = None,
    tags: Mapping[str, Input[str]] | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> pulumi_aws.vpc.SecurityGroupIngressRule:
    """Return an AWS VPC Security Group Ingress Rule.

    :param resource_id: The Pulumi resource ID.
    :param security_group_id: The security group ID.
    :param name: The name of the rule.
    :param description: The description of the rule.
    :param ip_protocol: The IP protocol.
    :param to_port: The end port of the range for the rule.
    :param from_port: The start port of the range for the rule.
    :param prefix_list_id: The prefix list ID.
    :param ipv4_cidr_block: The IPv4 CIDR block this rule applies to.
    :param ipv6_cidr_block: The IPv6 CIDR block this rule applies to.
    :param source_security_group_id: The source security group ID this
        rule applies to.
    :param tags: The tags for the rule.
    :param opts: The resource options.
    :returns: The Security Group Ingress Rule resource.
    """
    if not tags:
        tags = {}

    if source_security_group_id in ["self"]:
        source_security_group_id = security_group_id

    if ip_protocol in ["all", "-1"]:
        ip_protocol = "-1"

    default_tags = {
        "Name": name,
    }

    args = pulumi_aws.vpc.SecurityGroupIngressRuleArgs(
        ip_protocol=ip_protocol,
        security_group_id=security_group_id,
        description=description,
        cidr_ipv4=ipv4_cidr_block,
        cidr_ipv6=ipv6_cidr_block,
        prefix_list_id=prefix_list_id,
        referenced_security_group_id=source_security_group_id,
        tags={
                **default_tags,
                **tags,
        }
    )

    if ip_protocol not in ["all", "-1"]:
        args.from_port = from_port
        args.to_port = to_port

    return pulumi_aws.vpc.SecurityGroupIngressRule(
        resource_id,
        args=args,
        opts=opts,
    )


def _security_group_egress_rule(
    resource_id: str,
    security_group_id: Input[str],
    name: str,
    description: str,
    ip_protocol: str,
    to_port: int | None = 0,
    from_port: int | None = 0,
    prefix_list_id: Input[str] | None = None,
    ipv4_cidr_block: Input[str] | None = None,
    ipv6_cidr_block: Input[str] | None = None,
    destination_security_group_id: Input[str] | None = None,
    tags: Mapping[str, Input[str]] | None = None,
    opts: pulumi.ResourceOptions | None = None,
) -> pulumi_aws.vpc.SecurityGroupEgressRule:
    """Return an AWS VPC Security Group Egress Rule.

    :param resource_id: The Pulumi resource ID.
    :param security_group_id: The security group ID.
    :param name: The name of the rule.
    :param description: The description of the rule.
    :param ip_protocol: The IP protocol.
    :param to_port: The end port of the range for the rule.
    :param from_port: The start port of the range for the rule.
    :param prefix_list_id: The prefix list ID.
    :param ipv4_cidr_block: The IPv4 CIDR block this rule applies to.
    :param ipv6_cidr_block: The IPv6 CIDR block this rule applies to.
    :param destination_security_group_id: The destination security group
        ID this rule applies to.
    :param tags: The tags for the rule.
    :param opts: The resource options.
    :returns: The Security Group Egress Rule resource.
    """
    if not tags:
        tags = {}

    if destination_security_group_id in ["self"]:
        destination_security_group_id = security_group_id

    if ip_protocol in ["all", "-1"]:
        ip_protocol = "-1"

    default_tags = {
        "Name": name,
    }

    args = pulumi_aws.vpc.SecurityGroupEgressRuleArgs(
        ip_protocol=ip_protocol,
        security_group_id=security_group_id,
        description=description,
        cidr_ipv4=ipv4_cidr_block,
        cidr_ipv6=ipv6_cidr_block,
        prefix_list_id=prefix_list_id,
        referenced_security_group_id=destination_security_group_id,
        tags={
            **default_tags,
            **tags,
        }
    )

    if ip_protocol not in ["all", "-1"]:
        args.from_port = from_port
        args.to_port = to_port

    return pulumi_aws.vpc.SecurityGroupEgressRule(
        resource_id,
        args=args,
        opts=opts,
    )


__all__ = [
    "EC2SecurityGroupEgressRule",
    "EC2SecurityGroupIngressRule",
    "EC2SecurityGroupArgs",
    "EC2SecurityGroup",
    "EC2SecurityGroupRuleProtocol",
]

