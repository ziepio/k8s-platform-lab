variable "aws_region" {
  description = "Region for resources other than ECR Public."
  type        = string
  default     = "eu-central-1"
}

variable "github_repository" {
  description = "Repository in the format `owner/name`. Only this repository will be granted the role."
  type        = string
  default     = "ziepio/k8s-platform-lab"
}

variable "repository_name" {
  description = "Container image repository name."
  type        = string
  default     = "pacer"
}
