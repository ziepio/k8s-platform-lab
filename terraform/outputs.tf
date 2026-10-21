output "role_arn" {
  description = "Paste it into the `AWS_ROLE_ARN` secret in the repository settings."
  value       = aws_iam_role.github_actions.arn
}

output "repository_uri" {
  description = "Full image URI. Set it as image.repository in values.yaml."
  value       = aws_ecrpublic_repository.pacer.repository_uri
}
