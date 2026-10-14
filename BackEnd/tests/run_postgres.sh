#!/usr/bin/env bash
# PostgreSQL sementara; tidak membaca kredensial database aplikasi.
set -euo pipefail
cd "$(dirname "$0")/.."
mr_test_dir=$(mktemp -d /tmp/mr-governance-pg.XXXXXX)
cleanup() {
  pg_ctl -D "$mr_test_dir/data" -m fast -w stop >/dev/null 2>&1 || true
  rm -rf -- "$mr_test_dir"
}
trap cleanup EXIT
initdb -D "$mr_test_dir/data" -A trust --no-locale -E UTF8 >"$mr_test_dir/init.log"
pg_ctl -D "$mr_test_dir/data" -l "$mr_test_dir/postgres.log" -o "-k $mr_test_dir -p 55439 -c listen_addresses=''" -w start >/dev/null
createdb -h "$mr_test_dir" -p 55439 mr_test_governance
export MR_TEST_DATABASE_URL="postgresql+psycopg:///mr_test_governance?host=$mr_test_dir&port=55439"
.venv/bin/python -m unittest discover -s tests -p test_tata_kelola.py -v
