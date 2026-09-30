#!/usr/bin/env bash
# Delete everything the demo created (bucket contents, secrets, stack).
set -euo pipefail
PREFIX="${PREFIX:-kestrel-demo}"
BUCKET=$(aws cloudformation describe-stacks --stack-name "$PREFIX" --query "Stacks[0].Outputs[?OutputKey=='DataBucket'].OutputValue" --output text)
aws s3 rm "s3://$BUCKET" --recursive
# Force-delete secrets so a redeploy can reuse their names immediately.
for s in redshift-admin golden-readonly; do
  aws secretsmanager delete-secret --secret-id "$PREFIX/$s" --force-delete-without-recovery >/dev/null || true
done
aws cloudformation delete-stack --stack-name "$PREFIX"
aws cloudformation wait stack-delete-complete --stack-name "$PREFIX"
echo "Deleted stack $PREFIX"
