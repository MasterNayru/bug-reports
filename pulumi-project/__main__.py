"""An AWS Python Pulumi program"""

import pulumi
from pulumi_custom_resource_provider import MyBucket, MyBucketArgs

# Create an AWS resource (S3 Bucket)
bucket = MyBucket(
    'my-bucket',
    args=MyBucketArgs(
        bucket_name='my-unique-bucket-name-12345',
    )
)

child_bucket = MyBucket(
    'my-child-bucket',
    args=MyBucketArgs(
        bucket_name='my-unique-child-bucket-name-12345',
        tags={
            'Environment': 'Dev',
            'Owner': 'Alice',
        }
    ),
    opts=pulumi.ResourceOptions(parent=bucket),
)

# Export the name of the bucket
pulumi.export('bucket_name', bucket.name)
