#!/usr/bin/env bash
# Normalize dynamic values in example output for reproducible comparison.
# Usage: normalize_output.sh < actual_output > normalized_output
# Compatible with both GNU sed and BSD sed (macOS).

sed -E \
  -e 's/CUBRID version: [0-9.]+/CUBRID version: {{VERSION}}/g' \
  -e 's/DBA@[a-zA-Z0-9_-]+/DBA@{{HOSTNAME}}/g' \
  -e 's/[0-9]{4}-[0-9]{2}-[0-9]{2}/{{DATE}}/g'
