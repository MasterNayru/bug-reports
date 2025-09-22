# This project is to show that registering a resource transforms on a resource instantiated by RPC through a component library breaks types for fields containing outputs.

## Setup steps
```
cd custom_component_module
uv sync
cd ../pulumi-component-package
uv add ../custom_component_module   # This should be done instead of a sync to make sure it gets any changes made
cd ../pulumi-project
uv add ../custom_component_module   # This can be done to validate that calling the functions directly does work
pulumi package add ../pulumi-component-package
pulumi login --local
pulumi select stack dev
pulumi up
```

# "Fixing" the issue

To disable the transform, remove this line from the constructor of PulumiComponentResource in _types.py:
```
from . import _bootstrap
```

## Project Layout

```
.
├── custom_component_module          <-- My recreation of a package I made that defines a bunch of my custom components 
│   ├── pyproject.toml
│   ├── README.md
│   ├── src
│   │   └── custom_component_module
│   │       ├── __init__.py
│   │       ├── _bootstrap.py        <-- Module for defining the problem resource transform
│   │       ├── _security_group.py   <-- Module defining a security group.
│   │       ├── _types.py            <-- A module to define some helper methods to deal with RPC sending me dicts instead of the types I actually use.
│   │       └── _vpc.py              <-- Module defining a VPC, basically using this to generate an unknown value
│   └── uv.lock
├── pulumi-component-package     <-- Pulumi component library package used to expose custom components to project and recreate this issue.
│   ├── __main__.py
│   ├── PulumiPlugin.yaml
│   ├── pyproject.toml           <-- Has custom_component_module as a dependency. Need to make sure we re-add custom_component_module here when it is changed.
│   └── uv.lock
├── pulumi-project
│   ├── __main__.py
│   ├── Pulumi.dev.yaml          <-- The passphrase on this is empty
│   ├── Pulumi.yaml
│   ├── pyproject.toml
│   ├── README.md
│   ├── sdks
│   └── uv.lock
└── README.md                    <-- You are here :)

```

I am trying to develop a component that can be used to abstract the fact that users are supposed to generate security group rules using pulumi_aws.vpc.*Rule objects and not the ones in pulumi_aws.ec2. I want to expose a field on my objects that allows users to define ingress rules as a map, and then I use the key to build up a resource name and the value contains config options for the rule.

In custom_component_module/src/custom_component_module/{_vpc,security_group}.py, I am defining Pulumi component resources. For the args object and other configuration, I am using Pydantic models because I like validating user input and type safety. 

In custom_component_module/src/custom_component_module/_bootstrap.py, I have code that defines a resource transform. I am using this transform to set base tags across a bunch of things in my infrastructure.

In custom_component_module/src/custom_component_module/_types.py:50, I have a class that I have inherit from pulumi.ComponentResource that I use to import _bootstrap to ensure I only import it once and it absolutely happens in a Pulumi context. I'm all ears if there is a better way of doing this that would work with RPC, but when I have this imported I start seeing errors.

# The error

```
$ pulumi up

Enter your passphrase to unlock config/secrets
    (set PULUMI_CONFIG_PASSPHRASE or PULUMI_CONFIG_PASSPHRASE_FILE to remember):
Enter your passphrase to unlock config/secrets
Previewing update (dev):
     Type                    Name                Plan       Info
 +   pulumi:pulumi:Stack     pulumi.project-dev  create     2 errors
 +   └─ custom:resource:VPC  my-vpc              create
 +      └─ aws:ec2:Vpc       my-vpc              create

Diagnostics:
  pulumi:pulumi:Stack (pulumi.project-dev):
    error: custom-resource-provider:index:EC2SecurityGroup resource 'my-security-group' has a problem: Unexpected <class 'Exception'>: 1 validation error for EC2SecurityGroup
Args
    ingress_rules
      Input should be a valid dictionary [type=dict_type, input_value=<pulumi.output.Output object at 0x10612f0e0>, input_type=Output]
        For further information visit https://errors.pydantic.dev/2.11/v/dict_type:
      File "/Users/jmo/src/playground/bug-reports/pulumi-component-package/.venv/lib/python3.13/site-packages/custom_component_module/_security_group.py", line 242, in __init
__
        args = EC2SecurityGroupArgs.from_rpc(args)
      File "/Users/jmo/src/playground/bug-reports/pulumi-component-package/.venv/lib/python3.13/site-packages/custom_component_module/_types.py", line 38, in from_rpc
        return cls(**args)
      File "/Users/jmo/src/playground/bug-reports/pulumi-component-package/.venv/lib/python3.13/site-packages/pydantic/main.py", line 253, in __init__
        validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
```

## What works
* Importing the Python components directly
* Using the component package components but NOT setting any fields in ingress rules to Output values

## What doesn't work
* Using the component package and using an output value as a configuration option in ingress_rules
