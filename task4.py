import boto3
import json

def fetch_ec2_details(instance_id):
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(InstanceIds=[instance_id])
    except Exception as e:
        raise Exception(f"Error fetching EC2 details: {str(e)}")

    reservations = response.get('Reservations', [])
    if not reservations:
        raise Exception(f"No reservations found for instance ID: {instance_id}")

    instances = reservations[0].get('Instances', [])
    if not instances:
        raise Exception(f"No instances found for instance ID: {instance_id}")

    instance = instances[0]
    state = instance['State']['Name']
    public_ip = instance.get('PublicIpAddress', None)

    if state != 'running':
        raise Exception(f"Instance {instance_id} is not running. Current state: {state}")

    return {
        'instance_id': instance_id,
        'state': state,
        'public_ip': public_ip
    }

def fetch_alb_details(alb_name):
    elbv2 = boto3.client('elbv2')
    try:
        response = elbv2.describe_load_balancers(Names=[alb_name])
    except Exception as e:
        raise Exception(f"Error fetching ALB details: {str(e)}")

    load_balancers = response.get('LoadBalancers', [])
    if not load_balancers:
        raise Exception(f"No ALB found with name: {alb_name}")

    alb = load_balancers[0]
    return {
        'name': alb_name,
        'dns_name': alb['DNSName']
    }

def main():
    instance_id = '12344'
    alb_name = 'amit_alb'

    validation_data = {
        'ec2': fetch_ec2_details(instance_id),
        'alb': fetch_alb_details(alb_name)
    }

    with open('aws_validation.json', 'w') as f:
        json.dump(validation_data, f, indent=2)
    print("Validation data in aws_validation.json")

