import dataclasses

import pydantic
import pulumi
import pulumi_aws.ec2
# I MUST define Input, Output and, weirdly, T here to avoid Pulumi serialization issues.
# This is only required when the component resource is used over RPC (for example, when
# exposed via a component library package).
from ._types import (
    Input,
    Output,
    PulumiComponentResource,
    PulumiResourceArgs,
    T as T,
)
from collections.abc import Mapping
from typing import Self


class VPCArgs(PulumiResourceArgs):
    """The set of arguments for constructing a MyVPC resource."""
    name: Input[str]
    ipv4_cidr_block: Input[str]
    enable_ipv6: Input[bool] | None = None
    tags: Input[Mapping[str, Input[str]]] | None = None

    @pydantic.model_validator(mode="after")
    def _set_defaults(self) -> Self:
        """Set default values for optional fields."""
        if self.enable_ipv6 is None:
            self.enable_ipv6 = False
        if self.tags is None:
            self.tags = {}
        return self


class VPC(PulumiComponentResource):
    
    name: pulumi.Output[str]
    """The name of the VPC."""
    # I don't understand why but if I try to set this field as `id` then it will
    # not serialize properly when the component is used over RPC (for example, when
    # exposed via a component library package). I believe this is due to Pulumi's internal
    # handling of `id` fields. I have seen a GitHub issue where someone else ran into
    # this problem without RPC and required a fix on the Pulumi side. Would be nice to
    # know if something similar is happening here or if I have made some mistake.
    vpc_id: pulumi.Output[str]
    """The ID of the VPC."""
    ipv4_cidr_block: pulumi.Output[str]
    """The IPv4 CIDR block of the VPC."""
    # I don't know how to make this output handle '| None' values that isn't a
    # nightmare to use downstream. It seems that Pulumi will get an `Output[str] | None`
    # and convert it into a `Output[str | None]`. If there is some helper or way to detect
    # when the value is None and handle that properly, that would be great. Otherwise, I
    # have to mimic Go null values and set empty outputs to "" or something like that.
    ipv6_cidr_block: pulumi.Output[str]
    """The IPv6 CIDR block of the VPC."""

    def __init__(
        self,
        resource_id: str,
        args: VPCArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__('custom:resource:VPC', resource_id, {}, opts)

        # Handle the case where args is passed as a dictionary (for example, when exposing
        # this component via a component library package).
        args = VPCArgs.from_rpc(args)
        child_opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(parent=self))

        vpc = pulumi_aws.ec2.Vpc(
            resource_id,
            args=pulumi_aws.ec2.VpcArgs(
                cidr_block=args.ipv4_cidr_block,
                assign_generated_ipv6_cidr_block=args.enable_ipv6,
                tags={
                    "Name": args.name,
                }
            ),
            opts=child_opts,
        )

        self.name = vpc.tags.apply(lambda tags: tags["Name"] if tags and "Name" in tags else "")
        """The name of the VPC."""
        self.vpc_id = vpc.id
        """The ID of the VPC."""
        self.ipv4_cidr_block = vpc.cidr_block
        """The IPv4 CIDR block of the VPC."""
        self.ipv6_cidr_block = vpc.ipv6_cidr_block
        """The IPv6 CIDR block of the VPC."""

        self.register_outputs({
            'name': self.name,
            'ipv4_cidr_block': self.ipv4_cidr_block,
            'ipv6_cidr_block': self.ipv6_cidr_block,
        })
