# terraformDev

Terraform configuration that provisions the Google Cloud Platform infrastructure for the Cloud App project. It stands up the networking, the MySQL database, the VM that runs the Spring Boot service, the Pub/Sub topic and subscription, and the Cloud Function that delivers verification emails.

## What it creates

- **Networking** — a VPC with `webapp` and `db` subnets, routes, and firewall rules
- **Compute** — a Compute Engine VM built from the Packer image, with a startup script that wires the webapp to Cloud SQL
- **Database** — a private Cloud SQL (MySQL) instance with CMEK encryption and automatic backups
- **KMS** — a key ring with separate CMEK keys for VM disks, Cloud SQL, and Cloud Storage
- **Pub/Sub** — the topic and subscription that connect the webapp to the email verification Cloud Function
- **Cloud Function** — deploys the source zip from [../serverlessDev](../serverlessDev) and wires it to the Pub/Sub trigger
- **DNS / load balancing** — DNS records pointing the public name at the VM
- **IAM** — service account and role bindings for the webapp and Cloud SQL service identity

## Tech stack

- Language: HCL
- Tool: Terraform
- Providers: `google`, `google-beta`

## Layout

- [main.tf](main.tf) — all resources
- [variables.tf](variables.tf) — input variables and defaults
- [outputs.tf](outputs.tf) — outputs
- `dev.tfvars` — environment-specific values (not checked in)

## Usage

```sh
terraform init
terraform fmt
terraform plan   -var-file=dev.tfvars
terraform apply  -var-file=dev.tfvars
terraform destroy -var-file=dev.tfvars
```

## Required variables

`dev.tfvars` (or another `*.tfvars` file) must provide at minimum:

- `project_id` — the GCP project to deploy into
- `region`, `zone` — where to create resources
- `environment` — name suffix used to disambiguate resources
- `webapp_subnet_cidr`, `db_subnet_cidr` — subnet CIDRs
- `image_name` — the Packer-built image to boot the VM from
- `vm_disk_size`, `service_account` — VM configuration

Defaults for Mailgun, Cloud SQL sizing, and database credentials live in [variables.tf](variables.tf); override them per environment.

## CI

GitHub Actions workflow: [.github/workflows/basic.yml](.github/workflows/basic.yml) (runs `terraform fmt` / `validate` on pull requests).
