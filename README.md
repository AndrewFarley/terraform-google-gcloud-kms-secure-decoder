Terraform Module - Google Cloud KMS Decoder
========================

Purpose
------

Google Cloud KMS Secrets if you decode them in Terraform will have their plaintext value show
up in the [state file as seen here](https://www.terraform.io/docs/state/sensitive-data.html), which on most strict compliance and regulatory entities is
a huge .  Secrets plaintext should NEVER live anywhere on any
static location, and should only ever be requested when they need to be used.

Requirements
------
* Must have a Python interpreter installed
* Must be using a Unix-ey machine (linux/osx) (sorry Windows)
* Must have GCLoud CLI installed

Usage
------

First, create the KMS Key Ring and Crypto Key
```hcl

variable "project" { value = "my-project-name" }
variable "region" { value = "europe-west1" }

resource "google_kms_key_ring" "secrets" {
  name     = "my-secrets"
  location = "${var.region}"
}
resource "google_kms_crypto_key" "secrets" {
  name     = "my-secrets"
  key_ring = "${google_kms_key_ring.secrets.id}"
}
```

Next, create a secret (easier to do via shell...)

```bash
echo -n "SECRET GOES HERE" | gcloud kms encrypt \
--project my-project-name     \
--location europe-west1       \
--keyring my-secrets          \
--key my-secrets              \
--plaintext-file -            \
--ciphertext-file -           \
| base64 --wrap=0 && echo ""
# The output will look something like this...
CiQAHZpVct7KFNwG7IP3zp/asl1n912bih1281h2n1h8aW3iMGAOOJv1SIyEI=
```

Then expand your original TF script above to have...
```hcl
variable "project" { value = "my-project-name" }
variable "region" { value = "europe-west1" }
variable "ciphertext" { value = "CiQAHZpVct7KFNwG7IP3zp/asl1n912bih1281h2n1h8aW3iMGAOOJv1SIyEI="}

resource "google_kms_key_ring" "secrets" {
  name     = "my-secrets"
  location = "${var.region}"
}
resource "google_kms_crypto_key" "secrets" {
  name     = "my-secrets"
  key_ring = "${google_kms_key_ring.secrets.id}"
}
module "secret" {
  source = "github.com/andrewfarley/terraform-google-cloud-kms-decoder.git"
  project    = "${var.project}"
  region     = "${var.region}"
  keyring    = "my-secrets"
  key        = "my-secrets"
  ciphertext = "${var.ciphertext}"
}
output "plaintext" {
  value = "${module.secret.plaintext}"
}
```

Now you can safely store that KMS ciphertext inside your tfvars files, and not worry that their plaintext equivalent will ever be inside your project or your state file.

Author, Support, Feedback, Questions
------

<br/>Module created and managed by [Farley](https://github.com/andrewfarley) - farley _at_ neonsurge <dot> com

Please feel free to file Github bugs if you find any or suggestions for features!  If you're technically minded, please feel free to fork and make your own modifications.  If you make any fixed/changes that are awesome, please send me pull requests or patches.

If you have any questions/problems beyond that, feel free to email me.


License
-------

Apache 2 Licensed. See LICENSE for full details.
