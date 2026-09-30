#!/usr/bin/env bash
# Create/update the Redshift Serverless demo stack.
#   GOLDEN_CIDR=x.x.x.x/32 ./aws/deploy.sh
# Env: PREFIX (kestrel-demo), AWS_REGION (from aws config), GOLDEN_CIDR (required), MY_CIDR (auto-detected)
set -euo pipefail
cd "$(dirname "$0")"
PREFIX="${PREFIX:-kestrel-demo}"
STACK="${PREFIX}"
: "${GOLDEN_CIDR:?Set GOLDEN_CIDR to the CIDR Golden connects from (use 0.0.0.0/0 only for a throwaway demo)}"
MY_CIDR="${MY_CIDR:-$(curl -s https://checkip.amazonaws.com | tr -d '\n')/32}"

# Redshift Serverless needs 3 AZs, and some (e.g. use1-az3) are unsupported - skip those.
AZS=$(aws ec2 describe-availability-zones --filters Name=state,Values=available \
  --query "AvailabilityZones[?ZoneId!='use1-az3'].ZoneName" --output text | tr '\t' '\n' | head -3 | paste -sd, -)
echo "Stack=$STACK  AZs=$AZS  GoldenCidr=$GOLDEN_CIDR  MyCidr=$MY_CIDR"

aws cloudformation deploy \
  --stack-name "$STACK" \
  --template-file redshift-serverless.yaml \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides Prefix="$PREFIX" AvailabilityZones="$AZS" GoldenCidr="$GOLDEN_CIDR" MyCidr="$MY_CIDR"

aws cloudformation describe-stacks --stack-name "$STACK" \
  --query "Stacks[0].Outputs[].[OutputKey,OutputValue]" --output table
