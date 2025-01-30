package registry

import (
	"strings"
	"sync"
	"time"
)

// Device represents a registered device.
type Device struct {
	DeviceID        string
	CertFingerprint string
	LastSeen        time.Time
	Status          string // "active" or "revoked"
}

// Registry stores approved devices.
type Registry struct {
	mu      sync.RWMutex
	devices map[string]Device
}

// NewRegistry initializes a device registry.
func NewRegistry() *Registry {
	return &Registry{
		devices: make(map[string]Device),
	}
}

// RegisterDevice adds a new device to the registry.
func (r *Registry) RegisterDevice(deviceID, certFingerprint string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.devices[deviceID] = Device{
		DeviceID:        deviceID,
		CertFingerprint: certFingerprint,
		LastSeen:        time.Now(),
		Status:          "active",
	}
}

// IsDeviceValid checks if the device is registered and active.
func (r *Registry) IsDeviceValid(deviceID, certFingerprint string) bool {
	r.mu.RLock()
	defer r.mu.RUnlock()
	device, exists := r.devices[deviceID]
	return exists && device.Status == "active" && strings.Compare(strings.ToLower(device.CertFingerprint), strings.ToLower(certFingerprint)) == 0
}

// RevokeDevice revokes a device certificate.
func (r *Registry) RevokeDevice(deviceID string) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if device, exists := r.devices[deviceID]; exists {
		device.Status = "revoked"
		r.devices[deviceID] = device
	}
}
