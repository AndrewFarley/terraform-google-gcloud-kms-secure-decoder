# Define our inputs
variable "project" {}
variable "region" {}
variable "keyring" {}
variable "key" {}
variable "ciphertext" {}

# Perform our python based GCloud KMS Decrypt
data "external" "decode-google-cloud-kms" {
  program = ["python", "${path.module}/get-secret.py"]

  query = {
    project    = "${var.project}"
    region     = "${var.region}"
    keyring    = "${var.keyring}"
    key        = "${var.key}"
    ciphertext = "${var.ciphertext}"
  }
}

# Output our KMS plaintext value
output "plaintext" {
  value = "${data.external.decode-google-cloud-kms.result["output"]}"
}
