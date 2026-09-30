-- Read-only login for Golden Analytics. ${GOLDEN_PASSWORD} is substituted by aws/run_sql.py.
-- (CREATE USER fails harmlessly on re-run, so ALTER resets the password.)

CREATE USER golden_ro PASSWORD '${GOLDEN_PASSWORD}';
ALTER USER golden_ro PASSWORD '${GOLDEN_PASSWORD}';
GRANT USAGE ON SCHEMA ref, internal, external, forecast TO golden_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA ref, internal, external, forecast TO golden_ro;
