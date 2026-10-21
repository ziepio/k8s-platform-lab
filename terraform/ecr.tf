resource "aws_ecrpublic_repository" "pacer" {
  provider        = aws.us_east_1
  repository_name = var.repository_name

  catalog_data {
    about_text        = "Running pace calculator from the k8s-platform-lab project."
    architectures     = ["x86-64"]
    operating_systems = ["Linux"]
    usage_text        = "docker pull public.ecr.aws/<alias>/pacer:<tag>"
  }
}
