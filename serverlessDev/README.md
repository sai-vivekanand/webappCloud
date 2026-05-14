# serverlessDev

A Google Cloud Function (Python) that sends email verification messages to newly created users. It is triggered by a Pub/Sub topic that the Spring Boot app in the parent repo publishes to when a user signs up.

## How it works

1. The webapp publishes a Pub/Sub message containing the new user's `uuid`, `username`, and `firstName`.
2. `hello_pubsub` in [main.py](main.py) decodes the message.
3. It builds a verification link of the form `https://saivivekanand.me/v1/user/verify_email?token=<uuid>` and sends an email through the Mailgun API.
4. On success, it records the send time in the `verification_info` table of the Cloud SQL MySQL database so the webapp can enforce the verification link's TTL.

## Entry point

- Function: `hello_pubsub`
- Trigger: Pub/Sub
- Runtime: Python (functions-framework 3.x)

## Configuration

The function reads its configuration from environment variables, set on the Cloud Function at deploy time:

| Variable | Purpose |
| --- | --- |
| `DB_USERNAME` | Cloud SQL user |
| `DB_PASSWORD` | Cloud SQL password |
| `DB_HOST_NAME` | Cloud SQL host/IP |
| `INSTANCE_CONNECTION_NAME` | Cloud SQL connection name |
| `MAILGUN_DOMAIN` | Sending domain configured in Mailgun |
| `MAILGUN_API_KEY` | Mailgun API key |
| `MAILGUN_SENDER_EMAIL` | From address for verification mail |

## Dependencies

See [requirements.txt](requirements.txt): `functions-framework`, `requests`, `PyMySQL`.

## Local development

```sh
pip install -r requirements.txt
functions-framework --target=hello_pubsub --signature-type=event
```

## Deployment

The function is packaged as a zip and deployed by the Terraform configuration in the sibling [terraformDev](../terraformDev) directory (see the `cloud_zip_source` variable). CI is defined in [.github/workflows/main.yml](.github/workflows/main.yml).
