import pulumi

from typing import Any, TypeVar, Self
# I don't know why but when I use my components over RPC, Pulumi complains that
# Input, Output and T are not explicitly defined. Doing pulumi.Input and pulumi.Output
# does not work here, they need to be imported like this.
import pydantic
from pulumi import Input, Output
from collections.abc import Mapping
T = TypeVar("T")


class PulumiConfig(pydantic.BaseModel):
    """Class representing Pulumi resource configuration. I basically use this
    as a way to predefine the model config for all my Pulumi configuration
    classes."""

    model_config = pydantic.config.ConfigDict(
        arbitrary_types_allowed=True,
        extra="forbid",
    )


class PulumiResourceArgs(PulumiConfig):
    """Class that holds the configuration for a component resource. A child class of this
    type is required for each component resource.

    Since Pulumi uses RPC to create component resources, this class basically exists to
    define a method to catch the arguments passed over RPC and convert them from a dict
    to an instance of the class with its values populated."""

    @classmethod
    def from_rpc(cls, args: Self | dict[str, Any]) -> Self:
        """Create an instance of the class from RPC arguments."""
        if isinstance(args, cls):
            return args
        elif isinstance(args, Mapping):
            return cls(**args)
        else:
            raise ValueError(f"Invalid type for args: {type(args)}")


class PulumiResourceConfigArgs(PulumiConfig):
    """Class that holds part of a resource's configuration. This is used to define some
    aspect of a resource's configuration but is not necessarily representing a full
    resource."""
    pass


class PulumiComponentResource(pulumi.ComponentResource):
    """Class representing a Pulumi component resource. Defining this because I use this
    in my own setup and just want to make sure I reproduce my setup as closely as possible."""
    def __init__(
        self,
        resource_type: str,
        resource_id: str,
        props: dict[str, Any] | None = None,
        opts: pulumi.ResourceOptions | None = None,
    ):
        """Constructor."""
        self.pulumi_resource_id = resource_id
        # Comment out the line below to "fix" the issue
        from . import _bootstrap

        super().__init__(resource_type, name=self.pulumi_resource_id, props=props, opts=opts)

    def _outputs(
        self,
        resource_type: str,
        outputs: dict[str, Any],
    ) -> None:
        """Return the outputs for this component resource."""
        outputs = format_pulumi_output_names(
            name=self.pulumi_resource_id,
            resource_type=resource_type,
            outputs=outputs,
        )

        self.register_outputs(outputs=outputs)


def format_pulumi_output_names(
    name: str,
    resource_type: str,
    outputs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Returns outputs in a consistent format."""
    if not outputs:
        outputs = {}

    return {f"{name}/{resource_type}/{k}": v for k, v in outputs.items()}
