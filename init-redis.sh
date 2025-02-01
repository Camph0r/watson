#!/bin/sh

# Adding hardcoded entry for testing
DEVICE_KEY="device:host2-bishal.pulchowk"
EXPECTED_FINGERPRINT="1F3997D9B25C8A119697A98C8FFDF6627B2E87D19BB8127632781A1483A73478"

DEVICE_EXISTS=$(redis-cli EXISTS $DEVICE_KEY)

if [ "$DEVICE_EXISTS" = "1" ]; then
  CURRENT_FINGERPRINT=$(redis-cli HGET $DEVICE_KEY fingerprint)
  if [ "$CURRENT_FINGERPRINT" = "$EXPECTED_FINGERPRINT" ]; then
    echo "Device entry exists with matching fingerprint"
    exit 0
  fi
fi

echo "Creating new device entry..."
redis-cli HSET $DEVICE_KEY \
  fingerprint "$EXPECTED_FINGERPRINT" \
  status "active" \
  created_at "$(date -u +"%Y-%m-%dT%H:%M:%SZ")" \
  last_seen "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "Device entry created successfully"