import dataclasses

import pulumi
import pulumi_aws.s3


@dataclasses.dataclass
class MyBucketArgs:
    bucket_name: pulumi.Input[str]
    tags: pulumi.Input[dict[str, str]] | None = None


class MyBucket(pulumi.ComponentResource):
    
    name: pulumi.Output[str]

    def __init__(
        self,
        resource_id: str,
        args: MyBucketArgs,
        opts: pulumi.ResourceOptions | None = None,
    ) -> None:
        super().__init__('custom:resource:MyBucket', resource_id, {}, opts)

        # Handle the case where args is passed as a dictionary (for example, when exposing
        # this component via a component library package).
        if isinstance(args, dict):
            args = MyBucketArgs(**args)

        child_opts = pulumi.ResourceOptions.merge(opts, pulumi.ResourceOptions(parent=self))

        bucket = pulumi_aws.s3.Bucket(
            resource_id,
            bucket=args.bucket_name,
            tags=args.tags,
            opts=child_opts,
        )

        self.name = bucket.bucket
        """The name of the bucket."""

        self.register_outputs({
            'name': self.name,
        })
