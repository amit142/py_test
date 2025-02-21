
output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.web_server.id
}

output "lb_dns_name" {
  description = "DNS name of the load balancer"
  value       = aws_lb.application_lb.dns_name
}
