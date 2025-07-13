# GitHub Actions Workflow for E-Store Microservices

This workflow automatically builds, pushes Docker images to Amazon ECR, and deploys to Amazon ECS when code changes are detected in the microservices.

## Setting up Secrets

For the workflow to function properly, you need to set up the following secrets in your GitHub repository:

1. Go to your repository on GitHub
2. Select "Settings" > "Secrets and variables" > "Actions"
3. Add the following secrets:
- `AWS_REGION` : Region in AWS
- `AWS_ACCESS_KEY_ID`: Access key ID of an IAM user with permissions to access ECR and ECS
- `AWS_SECRET_ACCESS_KEY`: Corresponding secret access key

## Required IAM Permissions

The IAM user needs the following permissions:
- `AmazonECR-FullAccess`
- `AmazonECS-FullAccess`

Or create a custom policy with minimal permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecs:UpdateService",
                "ecs:DescribeServices"
            ],
            "Resource": "*"
        }
    ]
}
```

## ECS Structure

This workflow assumes you already have:
- An ECS Cluster named `e-store-cluster`
- ECS Services:
  - `e-store-product-service`
  - `e-store-payment-service`
  - `e-store-coupon-service`
  - `e-store-order-service`
- ECR Repositories:
  - `e-store-product`
  - `e-store-payment`
  - `e-store-coupon`
  - `e-store-order`

If your resource names are different, please update them in the workflow file.
