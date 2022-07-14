#!/usr/bin/env bash

# This script does some minimal sanity checks of schema files.
# It expects to find a schema file for each version listed in CHANGELOG.md
# since 1.0.0 release.

set -e

BUILD_TOOL_SCHEMAS_VERSION=0.12.1

# List of vesions that do not require or have a schema.
declare -a skip_versions=("1.0.0" "1.0.1" "1.1.0" "1.2.0" "1.3.0" "1.6.0")

root_dir=$PWD
schemas_dir=$root_dir/schemas

# Find all version sections in CHANGELOG that start with a number in 1..9 range.
grep -o -e '## v[1-9].*\s' $root_dir/CHANGELOG.md | grep -o '[1-9].*' | while read ver; do
  if [[ " ${skip_versions[*]} " == *" $ver "* ]]; then
    # Skip this version, it does not need a schema file.
    continue
  fi

  file="$schemas_dir/$ver"
  echo -n "Ensure schema file $file exists... "

  # Check that the schema for the version exists.
  if [ -f "$file" ]; then
    echo "OK, exists."
  else
    echo "FAILED: $file does not exist. The schema file must exist because the version is declared in CHANGELOG.md."
    exit 3
  fi
done

# Now check the content of all schema files in the ../shemas directory.
for file in $schemas_dir/*; do
  # Filename is the version number.
  ver=$(basename $file)

  echo -n "Checking schema file $file for version $ver... "

  # Check that the version is defined in the schema file. 
  if ! grep -q "\s$ver:" $file; then
    echo "FAILED: $ver version definition is not found in $file"
    exit 1
  fi

  # Check that the schema_url matches the version.
  if ! grep -q "schema_url: https://opentelemetry.io/schemas/$ver" $file; then
    echo "FAILED: schema_url is not found in $file"
    exit 2
  fi

  docker run -v $schemas_dir:/schemas \
  		otel/build-tool-schemas:$BUILD_TOOL_SCHEMAS_VERSION --file /schemas/$ver --version=$ver

  echo "OK"
done
