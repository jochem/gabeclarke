#!/bin/bash
# Generate Strapi secrets for .env file

echo "Generating Strapi secrets..."
echo ""
echo "Add these to your strapi/.env file:"
echo ""
echo "JWT_SECRET=$(node -e "console.log(require('crypto').randomBytes(64).toString('base64'))")"
echo "ADMIN_JWT_SECRET=$(node -e "console.log(require('crypto').randomBytes(64).toString('base64'))")"
echo "APP_KEYS=$(node -e "console.log([...Array(4)].map(() => require('crypto').randomBytes(32).toString('base64')).join(','))")"
echo ""






