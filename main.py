import boto3
import requests
import getpass
import json
import string
from random import *

#Prompt User for information
#Dome9
dome9_api_key = input('Dome 9 API Key: ')
dome9_api_sedret = getpass.getpass('Dome9 Secret Key: ')

#AWS
access_key = input('AWS Access Key: ')
aws_secret_key = getpass.getpass('AWS Secret Key: ')

#Gather Policy Name
read_policy = 'test1_read'
write_policy = 'test1_write'

#Create IAM client for AWS
iam=boto3.client('iam', aws_access_key_id=access_key,
    aws_secret_access_key=aws_secret_key,)

#Create IAM Policies

#Create Dome9 read only policy
dome9_readonly_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Dome9ReadOnly",
            "Action": [
                "cloudtrail:LookupEvents",
                "dynamodb:DescribeTable",
                "elasticfilesystem:Describe*",
                "elasticache:ListTagsForResource",
                "es:ListTags",
                "firehose:Describe*",
                "firehose:List*",
                "guardduty:Get*",
                "guardduty:List*",
                "kinesis:List*",
                "kinesis:Describe*",
                "kinesisvideo:Describe*",
                "kinesisvideo:List*",
                "logs:Describe*",
                "logs:Get*",
                "logs:FilterLogEvents",
                "lambda:List*",
                "s3:List*",
                "sns:ListSubscriptions",
                "sns:ListSubscriptionsByTopic",
                "sns:ListTagsForResource",
                "waf-regional:ListResourcesForWebACL",
                "eks:ListNodegroups",
                "eks:DescribeNodegroup"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}

response = iam.create_policy(
  PolicyName=read_policy,
  PolicyDocument=json.dumps(dome9_readonly_policy)
)

print (response)

#Create Dome9 write policy

dome9_write_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Dome9Write",
            "Action": [
                "ec2:AuthorizeSecurityGroupEgress",
                "ec2:AuthorizeSecurityGroupIngress",
                "ec2:CreateSecurityGroup",
                "ec2:DeleteSecurityGroup",
                "ec2:RevokeSecurityGroupEgress",
                "ec2:RevokeSecurityGroupIngress",
                "ec2:ModifyNetworkInterfaceAttribute",
                "ec2:CreateTags",
                "ec2:DeleteTags"
            ],
            "Effect": "Allow",
            "Resource": "*"
        }
    ]
}

response = iam.create_policy(
  PolicyName='test1_write',
  PolicyDocument=json.dumps(dome9_write_policy)
)

print (response)

#Create Dome9 Role in AWS

#Generate External ID
extid = ''.join(choice(string.ascii_letters + string.digits) for _ in range(24))

#Role Information
path='/'
role_name = 'testrole1'
description='Dome9 Permissions Role'

#Trust Policy for Dome9 JSON to variables
trust_policy={
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::634729597623:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {"StringEquals": {"sts:ExternalId":extid}}
    }
  ]
}

tags=[
    {
        'Key': 'Environment',
        'Value': 'Production'
    }
]

#Create Initial Role
response = iam.create_role(
        Path=path,
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust_policy),
        Description=description,
        MaxSessionDuration=3600,
        
 )
  
print (response)
print (response[Arn])

role_arn = response[Arn]

#Get ARN for policies
arn_prefix = 'arn:aws:iam::252388646672:policy/'
policy_name_list = {read_policy, write_policy, SecurityAudit, AmazonInspectorReadOnlyAccess}


#Loop through list to Apply Access Policies to the newly created role
for x in policy_name_list:
    policy_arn = arn_prefix + policy_name_list[x] 
    iam.attach_role_policy(
        PolicyArn=policy_arn,
        RoleName=role_name
    )