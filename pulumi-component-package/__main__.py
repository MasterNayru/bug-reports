from pulumi.provider.experimental import component_provider_host

from custom_component_module import VPC
from custom_component_module import EC2SecurityGroup

if __name__ == "__main__":
    component_provider_host(
        name="custom-resource-provider",
        components=[
            VPC,
            EC2SecurityGroup,
        ],
    )
