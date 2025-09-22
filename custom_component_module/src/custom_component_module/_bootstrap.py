"""Module for performing setup for Pulumi stacks.

NOTE: This module requires that it is imported INSIDE a Pulumi context,
and thus it is vital that it is only imported in places where we know that
can only be accessed during the execution of a Pulumi program."""

import pulumi
from collections.abc import Mapping


def _auto_tag(
    args: pulumi.ResourceTransformArgs,
) -> pulumi.ResourceTransformResult:
    """Automatically tag resources with default tags.

    :param args: Pulumi stack transformation arguments.
    :return: Transformed resource arguments.
    """
    base_tags = {
        "SomeTag": "SomeValue"
    }

    # Only apply tags to AWS resources
    if args.type_.startswith("aws:") or args.type_.startswith("aws-native:"):
        # Since this is used in a Pulumi component library,
        # resources are instantiated through RPC calls to the Pulumi engine,
        # meaning we can't rely on a maintained list of tags in this library
        # to accurately apply tags on both sides of the communication.
        if "tags" in args.props and isinstance(args.props["tags"], dict):
            args.props = {
                "tags": {**args.props["tags"], **base_tags},
                **args.props,
            }

    return pulumi.ResourceTransformResult(props=args.props, opts=args.opts)


# This registers a stack transformation that will be applied to all resources
# in the stack. The transformation will add the tags to the resource if it
# supports tags.
pulumi.runtime.register_stack_transform(_auto_tag)
