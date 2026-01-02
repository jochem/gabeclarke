#!/bin/bash
# Script to create Strapi 5 project non-interactively

cd /Users/jochem/yot/gabeclarke

# Remove old project if exists
rm -rf strapi

# Create Strapi project with all answers
{
  echo "N"  # Skip example structure
  echo "n"  # No TypeScript
} | npx create-strapi-app@latest strapi \
  --dbclient=postgres \
  --dbhost=localhost \
  --dbport=5432 \
  --dbname=strapi \
  --dbusername=strapi \
  --dbpassword=strapi \
  --no-run \
  --skip-cloud

echo "Strapi project creation completed!"






