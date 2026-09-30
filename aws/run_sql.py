"""Run a .sql file against Redshift Serverless via the Redshift Data API (aws CLI, no drivers needed).

    python3 aws/run_sql.py --workgroup WG --secret-arn ARN --database kestrel sql/01_create_tables.sql

${VARS} in the file are substituted from the environment. Statements are split on ';'.
"""
import argparse
import json
import os
import re
import string
import subprocess
import sys
import time


def aws(*args):
    res = subprocess.run(["aws", "redshift-data", *args, "--output", "json"], capture_output=True, text=True)
    if res.returncode:
        sys.exit(res.stderr)
    return json.loads(res.stdout)


def run(stmt, a):
    sid = aws("execute-statement", "--workgroup-name", a.workgroup, "--secret-arn", a.secret_arn,
              "--database", a.database, "--sql", stmt)["Id"]
    while True:
        d = aws("describe-statement", "--id", sid)
        if d["Status"] in ("FINISHED", "FAILED", "ABORTED"):
            return d
        time.sleep(1)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--workgroup", required=True)
    p.add_argument("--secret-arn", required=True)
    p.add_argument("--database", default="kestrel")
    p.add_argument("file")
    a = p.parse_args()

    sql = string.Template(open(a.file).read()).substitute(os.environ)
    sql = re.sub(r"--[^\n]*", "", sql)
    stmts = [s.strip() for s in sql.split(";") if s.strip()]
    print(f"{a.file}: {len(stmts)} statements")
    for stmt in stmts:
        label = " ".join(stmt.split())[:90].replace(os.environ.get("GOLDEN_PASSWORD") or "\0", "****")
        d = run(stmt, a)
        if d["Status"] == "FINISHED":
            print(f"  ok    {label}")
        elif "already exists" in d.get("Error", ""):
            print(f"  skip  {label}  (already exists)")
        else:
            sys.exit(f"  FAIL  {label}\n        {d.get('Error')}")


if __name__ == "__main__":
    main()
