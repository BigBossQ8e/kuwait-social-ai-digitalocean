#!/bin/bash

# Test the deployed API
echo "Testing Kuwait Social AI Live API..."
echo "==================================="

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s https://kwtsocial.com/api/health | python3 -m json.tool

# Test trending endpoint (public)
echo -e "\n2. Testing trending content (public)..."
curl -s https://kwtsocial.com/api/competitor/trending | python3 -m json.tool | head -20

echo -e "\nAPI is responding!"