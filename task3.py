from jinja2 import Template
from python_terraform import *
import sys
import json

ami_options = {
    "1": "ami-0abcdef1234567890",  # Ubuntu example AMI
    "2": "ami-0123456789abcdef0"   # Amazon Linux example AMI
}

instance_types = {
    "1": "t3.small",
    "2": "t3.medium"
}

ami_choice = "1"
instance_type_choice = "2"
region = "us-east-1"
availability_zone = "us-east-1a"
load_balancer_name = "my-application-lb"

ami = ami_options.get(ami_choice, "ami-0abcdef1234567890")
instance_type = instance_types.get(instance_type_choice, "t3.small")


main_template = """
provider "aws" {
  region = "{{ region }}"
}

resource "aws_instance" "web_server" {
  ami               = "{{ ami }}"
  instance_type     = "{{ instance_type }}"
  availability_zone = "{{ availability_zone }}"
  tags = {
    Name = "WebServer"
  }
}

resource "aws_lb" "application_lb" {
  name               = "{{ load_balancer_name }}"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb_sg.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_security_group" "lb_sg" {
  name        = "lb_security_group"
  description = "Allow HTTP inbound traffic"
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_lb_listener" "http_listener" {
  load_balancer_arn = aws_lb.application_lb.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.web_target_group.arn
  }
}

resource "aws_lb_target_group" "web_target_group" {
  name     = "web-target-group"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id
}

resource "aws_lb_target_group_attachment" "web_instance_attachment" {
  target_group_arn = aws_lb_target_group.web_target_group.arn
  target_id        = aws_instance.web_server.id
}

resource "aws_subnet" "public" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index}.0/24"
  availability_zone = element(["{{ availability_zone }}", "us-east-1b"], count.index)
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}
"""

outputs_template = """
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web_server.id
}

output "lb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.application_lb.dns_name
}
"""

def create_terraform_files():
    template = Template(main_template)
    main_rendered = template.render(
        region=region,
        ami=ami,
        instance_type=instance_type,
        availability_zone=availability_zone,
        load_balancer_name=load_balancer_name
    )

    with open("main.tf", "w") as file:
        file.write(main_rendered)
        print("\n main.tf has been created.")

    # Save outputs configuration
    with open("outputs.tf", "w") as file:
        file.write(outputs_template)
        print(" outputs.tf has been created.")

def execute_terraform():
    try:
        tf = Terraform()
        print("\n Initializing Terraform...")

        ret_code, stdout, stderr = tf.init()
        if ret_code != 0:
            raise Exception(f"Terraform init failed:\n{stderr}")
        print(" Terraform initialization successful")

        print("\nRunning Terraform plan...")
        ret_code, stdout, stderr = tf.plan()
        if ret_code != 0:
            raise Exception(f"Terraform plan failed:\n{stderr}")
        print(" Terraform plan successful")
        print(stdout)

        print("\n Applying Terraform configuration...")
        ret_code, stdout, stderr = tf.apply(skip_plan=True, auto_approve=True)
        if ret_code != 0:
            raise Exception(f"Terraform apply failed:\n{stderr}")
        print(" Terraform apply successful")

        print("\n Retrieving Terraform outputs...")
        ret_code, stdout, stderr = tf.output(json=True)
        if ret_code != 0:
            raise Exception(f"Failed to get Terraform outputs:\n{stderr}")

        outputs = json.loads(stdout)

        print("\n Infrastructure Details:")
        print(f"Instance ID: {outputs.get('instance_id', {}).get('value', 'N/A')}")
        print(f"Load Balancer DNS: {outputs.get('lb_dns_name', {}).get('value', 'N/A')}")

        return True, outputs

    except Exception as e:
        return False, str(e)

def main():
    create_terraform_files()

    success, result = execute_terraform()

    if not success:
        print(f"\n Terraform execution failed:")
        print(result)
        sys.exit(1)

    print("\n Infrastructure deployment completed successfully!")

main()
