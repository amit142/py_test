from jinja2 import Template

ami_options = {
    "1": "ami-0c55b159cbfafe1f0",
    "2": "ami-0c94855ba95c71c99"
}
instance_options = {
    "1": "t3.small",
    "2": "t3.medium"
}

print("Please select an AMI:")
print("1. Ubuntu (ami-0c55b159cbfafe1f0)")
print("2. Amazon Linux (ami-0c94855ba95c71c99)")
ami_choice = input("Enter the number of your choice: ")
ami = ami_options.get(ami_choice, "ami-0c55b159cbfafe1f0")
if ami_choice not in ami_options:
    print("Invalid choice. Defaulting to Ubuntu.")


print("Please select an instance type:")
print("1. t3.small")
print("2. t3.medium")
instance_choice = input("Enter the number of your choice: ")
instance_type = instance_options.get(instance_choice, "t3.small")
if instance_choice not in instance_options:
    print("Invalid choice. Defaulting to t3.small.")


region = input("Enter the region (only us-east-1 is allowed): ").strip()
if region != "us-east-1":
    print("Invalid region. Defaulting to us-east-1.")
    region = "us-east-1"

alb_name = input("Enter a name for the Application Load Balancer: ").strip()


context = {
    "ami": ami,
    "instance_type": instance_type,
    "region": region,
    "alb_name": alb_name
}

template_str = """
Selected AMI: {{ ami }}
Instance Type: {{ instance_type }}
Region: {{ region }}
ALB Name: {{ alb_name }}
"""

template = Template(template_str)
rendered = template.render(context)

print(rendered)

