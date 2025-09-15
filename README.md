### Reproduction steps

```
cd pulumi-project
pulumi login --local
pulumi stack select dev
pulumi package add ../pulumi-component
pulumi up
```
