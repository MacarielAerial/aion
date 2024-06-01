terraform {
  backend "s3" {
    bucket         	   = "aion-tfstate-34567"
    key              	 = "state/tofu.tfstate"
    region         	   = "eu-west-1"
    encrypt        	   = true
    dynamodb_table     = "aion_tf_lockid"
    profile            = "malcador"
  }
}