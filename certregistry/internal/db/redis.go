package db

import (
	"context"
	"fmt"
	"log"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
)

type DeviceStore struct {
	rdb *redis.Client
}

func NewDeviceStore(redisURL string) (*DeviceStore, error) {
	log.Println("Connecting to Redis at", redisURL)
	opt, err := redis.ParseURL(redisURL)
	if err != nil {
		return nil, fmt.Errorf("invalid redis URL: %w", err)
	}

	rdb := redis.NewClient(opt)

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := rdb.Ping(ctx).Err(); err != nil {
		return nil, fmt.Errorf("failed to connect to Redis: %w", err)
	}

	return &DeviceStore{rdb: rdb}, nil
}

func (s *DeviceStore) RegisterDevice(deviceID, fingerprint string) error {
	ctx := context.Background()
	return s.rdb.HSet(ctx, fmt.Sprintf("device:%s", deviceID), map[string]interface{}{
		"fingerprint": fingerprint,
		"status":      "active",
		"created_at":  time.Now().UTC().Format(time.RFC3339),
		"last_seen":   time.Now().UTC().Format(time.RFC3339),
	}).Err()
}

func (s *DeviceStore) ValidateDevice(deviceID, fingerprint string) (bool, error) {
	ctx := context.Background()

	values, err := s.rdb.HGetAll(ctx, fmt.Sprintf("device:%s", deviceID)).Result()
	if err == redis.Nil {
		return false, nil
	}
	if err != nil {
		return false, err
	}
	if len(values) == 0 {
		return false, nil
	}

	return values["status"] == "active" && strings.EqualFold(values["fingerprint"], fingerprint), nil
}

func (s *DeviceStore) RevokeDevice(deviceID string) error {
	ctx := context.Background()
	return s.rdb.HSet(ctx, fmt.Sprintf("device:%s", deviceID), "status", "revoked").Err()
}

func (s *DeviceStore) Close() error {
	return s.rdb.Close()
}
