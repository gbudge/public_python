# 
# A python script that scans cloudformation yaml files for duplicate security group rules.
# The requirements are:
#   - Python 3.6 or later
#   - PyYAML library
#   - The script must accept the command line argument "--path" and the "--output" arguments.
#   - The --path argument must handle a directory only, with a single file or wildcard files.
#   - The --output argument must handle either json, text or none (set exit code only).
#   - The script output must only output the duplicates with the following fields:
#       - Resource names, security group id (if available) and descriptions (if available).
#       - Ingress/egress, protocol, cidr, fromport, toport
#   - The script must locate duplicates in any file matching the --path argument.
#   
#   Usage: python cfn_sg.py --path <yaml_file_path_pattern> --output <json|text>
#       Example: python cfn_sg.py --path /path/to/yaml/files --output json
#       Example: python cfn_sg.py --path /path/to/yaml/files/*.yaml --output text
#       Example: python cfn_sg.py --path /path/to/yaml/my_file.yml --output text
#   
# Example of a CloudFormation YAML template:
# 
# Parameters:
#   MyCidrIp:
#     Type: String
#     Description: The IP address range that can be used to access the EC2 instances
#     AllowedPattern: "(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})/(\d{1,2})"
#     Default: ""
#
# Resources:
#   MySecurityGroupRule1:
#     Type: AWS::EC2::SecurityGroupIngress
#     Properties:
#       GroupId:
#         Ref: MySecurityGroup
#       IpProtocol: tcp
#       FromPort: '80'
#       ToPort: '80'
#       CidrIp:
#         Ref: MyCidrIp
# 
#   MySecurityGroupRule2:
#     Type: AWS::EC2::SecurityGroupIngress
#     Properties:
#       GroupId:
#         Ref: MySecurityGroup
#       IpProtocol: tcp
#       FromPort: '22'
#       ToPort: '22'
#       CidrIp:
#         Ref: 10.0.0.0/8
#
#   MySecurityGroup:
#     Type: AWS::EC2::SecurityGroup
#     Properties:
#       GroupDescription: My security group
#       SecurityGroupIngress:
#         - IpProtocol: tcp
#           FromPort: '80'
#           ToPort: '80'
#           CidrIp: 10.0.0.0/8
#         - IpProtocol: tcp
#           FromPort: '22'
#           ToPort: '22'
#           CidrIp:
#             Ref: MyCidrIp
#       SecurityGroupEgress:
#         - IpProtocol: tcp
#           FromPort: '80'
#           ToPort: '80'
#           CidrIp:
#             Ref: MyCidrIp
#         - IpProtocol: tcp
#           FromPort: '22'
#           ToPort: '22'
#           CidrIp:
#             Ref: MyCidrIp
#

#!/usr/bin/env python3

import argparse
import os
import yaml
import json
from collections import defaultdict

# Yaml files dictionary file path and contents.
yaml_files = {}

# Read all files into the yaml_files dictionary.
def read_files(path):
    for file in os.listdir(path):
        if file.endswith(".yaml") or file.endswith(".yml"):
            with open(os.path.join(path, file), 'r') as stream:
                try:
                    yaml_files[file] = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

# Start of the script.
if __name__ == "__main__":
    # Parse command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="Path to the yaml files")
    parser.add_argument("--output", help="Output format: json|text", default="json")
    args = parser.parse_args()

    # Check if the path argument is provided.
    if not args.path:
        print("Error: The --path argument is required.")
        exit(1)
    
    # Read all files into the yaml_files dictionary.
    read_files(args.path)
