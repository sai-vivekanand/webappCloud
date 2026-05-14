# Cloud App

A Spring Boot REST API for user account management with email verification, designed to run on Google Cloud Platform. User creation publishes an event to Pub/Sub, which triggers the serverless email verification function in [serverlessDev/](serverlessDev/). Infrastructure is provisioned with Terraform from [terraformDev/](terraformDev/), and the VM image is built with Packer from [packer/](packer/).

## Tech stack

- Java 17, Spring Boot 3.0.2
- MySQL 8 (via Spring Data JPA)
- Spring Cloud GCP Pub/Sub
- Maven 3.8+
- JUnit 5, Mockito for tests
- Logback with logstash JSON encoder for structured logs

## Project layout

- [src/main/java/com/neu/cloud/cloudApp/](src/main/java/com/neu/cloud/cloudApp/) — application source
  - [controller/](src/main/java/com/neu/cloud/cloudApp/controller/) — REST controllers
  - [service/](src/main/java/com/neu/cloud/cloudApp/service/) — business logic and Pub/Sub config
  - [repository/](src/main/java/com/neu/cloud/cloudApp/repository/) — JPA repositories
  - [model/](src/main/java/com/neu/cloud/cloudApp/model/) — entity classes
  - [Utils/](src/main/java/com/neu/cloud/cloudApp/Utils/) — auth and helpers
- [src/test/](src/test/) — unit tests
- [packer/](packer/) — Packer template for the custom VM image
- [serverlessDev/](serverlessDev/) — Cloud Function source for email verification
- [terraformDev/](terraformDev/) — Terraform configuration for GCP infrastructure

## Build and run

Prerequisites: JDK 17, Maven 3.8+, a running MySQL 8 instance.

```sh
./mvnw clean package
./mvnw spring-boot:run
```

Database credentials and Pub/Sub settings are read from [src/main/resources/application.properties](src/main/resources/application.properties).

## API endpoints

All endpoints are versioned under `/v15`.

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/healthz` | none | Health check |
| POST | `/v15/user` | none | Create a new user; publishes a verification event to Pub/Sub |
| GET | `/v15/user/self` | Basic | Fetch the authenticated user; requires a verified email |
| PUT | `/v15/user/self` | Basic | Update the authenticated user; requires a verified email |
| GET | `/v15/user/verify_email?token=<uuid>` | none | Verify the email using the token from the verification link |

## CI/CD

GitHub Actions workflows live in [.github/workflows/](.github/workflows/):

- `basic.yml` — runs unit tests on pull requests; merges are blocked if it fails
- `packer.yml` — builds the custom GCP image on merges to main

## Related repositories

- Cloud Function source: [serverlessDev/](serverlessDev/)
- Infrastructure as code: [terraformDev/](terraformDev/)
