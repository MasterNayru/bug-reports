from pulumi.provider.experimental import component_provider_host

import _bucket

if __name__ == "__main__":
    component_provider_host(
        name="custom-resource-provider",
        components=[
            _bucket.MyBucket,
        ],
    )
