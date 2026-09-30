#!/usr/bin/env bash
# Upload ./data to S3, create tables, COPY, and create the golden_ro user. Safe to re-run.
set -euo pipefail
cd "$(dirname "$0")/.."
PREFIX="${PREFIX:-kestrel-demo}"
out() { aws cloudformation describe-stacks --stack-name "$PREFIX" --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text; }
BUCKET=$(out DataBucket); WG=$(out WorkgroupName); ADMIN=$(out AdminSecretArn); GSECRET=$(out GoldenSecretArn)

[ -d data/internal ] || python3 generator/generate.py
aws s3 sync data/ "s3://$BUCKET/data/" --exclude "*" --include "*.csv" --delete

GOLDEN_PASSWORD=$(aws secretsmanager get-secret-value --secret-id "$GSECRET" --query SecretString --output text \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["password"])')
export BUCKET GOLDEN_PASSWORD
for f in sql/01_create_tables.sql sql/02_load.sql sql/03_golden_user.sql; do
  python3 aws/run_sql.py --workgroup "$WG" --secret-arn "$ADMIN" --database kestrel "$f"
done

echo
echo "Golden connection:  host=$(out Endpoint)  port=5439  db=kestrel  user=golden_ro"
echo "Password:           aws secretsmanager get-secret-value --secret-id $GSECRET --query SecretString --output text"
