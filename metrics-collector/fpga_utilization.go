package main

import (
	"bytes"
	"container/list"
	"encoding/gob"
	"time"
)

type UsageRequest struct {
	Usage     float64
	Timestamp time.Time
}

type UsageBasedFPGAUtilizationTracker struct {
	recentUsage float64
	Requests    *list.List
}

func NewFPGAUtilizationTracker() *UsageBasedFPGAUtilizationTracker {
	return &UsageBasedFPGAUtilizationTracker{
		Requests: list.New(),
	}
}

func (tracker *UsageBasedFPGAUtilizationTracker) Decay() {
	// Remove older requests (more than 5 minutes old)
	for e := tracker.Requests.Front(); e != nil; {
		next := e.Next()

		req := e.Value.(UsageRequest)
		if time.Now().Sub(req.Timestamp) > time.Minute*5 {
			tracker.Requests.Remove(e)
			tracker.recentUsage -= req.Usage
		}

		e = next
	}
}

func (tracker *UsageBasedFPGAUtilizationTracker) AddRequest(computeTime float64, timestampMillis int64) {
	timeFromTimestamp := time.Unix(0, timestampMillis*int64(time.Millisecond))

	// Add new request
	tracker.Requests.PushBack(UsageRequest{
		Usage:     computeTime,
		Timestamp: timeFromTimestamp,
	})
	tracker.recentUsage += computeTime
}

func (tracker *UsageBasedFPGAUtilizationTracker) GetUtilizationMillis() float64 {
	return tracker.recentUsage
}

func (tracker *UsageBasedFPGAUtilizationTracker) Serialize() ([]byte, error) {
	var buf bytes.Buffer
	encoder := gob.NewEncoder(&buf)

	var requests []UsageRequest
	for e := tracker.Requests.Front(); e != nil; e = e.Next() {
		requests = append(requests, e.Value.(UsageRequest))
	}

	err := encoder.Encode(requests)
	if err != nil {
		return nil, err
	}

	return buf.Bytes(), nil
}

func (tracker *UsageBasedFPGAUtilizationTracker) Deserialize(data []byte) error {
	buf := bytes.NewBuffer(data)
	decoder := gob.NewDecoder(buf)

	var exportable []UsageRequest

	err := decoder.Decode(&exportable)
	if err != nil {
		return err
	}

	tracker.recentUsage = 0
	for _, value := range exportable {
		tracker.Requests.PushBack(value)
		tracker.recentUsage += value.Usage
	}

	return nil
}

type ReconfigurationRequest struct {
	Timestamp           time.Time
	ReconfigurationTime float64
}

type ReconfigurationBasedFPGAUtilizationTracker struct {
	recentReconfigurationTime float64
	Requests                  *list.List
}

func NewReconfigurationBasedFPGAUtilizationTracker() *ReconfigurationBasedFPGAUtilizationTracker {
	return &ReconfigurationBasedFPGAUtilizationTracker{
		Requests: list.New(),
	}
}

func (tracker *ReconfigurationBasedFPGAUtilizationTracker) Decay() {
	// Remove older requests (more than five minutes old)
	for e := tracker.Requests.Front(); e != nil; {
		next := e.Next()

		req := e.Value.(ReconfigurationRequest)
		if time.Now().Sub(req.Timestamp) > time.Minute*5 {
			tracker.Requests.Remove(e)
			tracker.recentReconfigurationTime -= req.ReconfigurationTime
		}

		e = next
	}
}

func (tracker *ReconfigurationBasedFPGAUtilizationTracker) AddRequest(timestampMillis int64, reconfigurationTime float64) {
	timeFromTimestamp := time.Unix(0, timestampMillis*int64(time.Millisecond))

	// Add new request
	tracker.Requests.PushBack(ReconfigurationRequest{
		Timestamp:           timeFromTimestamp,
		ReconfigurationTime: reconfigurationTime,
	})
	tracker.recentReconfigurationTime += reconfigurationTime
}

func (tracker *ReconfigurationBasedFPGAUtilizationTracker) GetRecentReconfigurationTimeMillis() float64 {
	return tracker.recentReconfigurationTime
}

func (tracker *ReconfigurationBasedFPGAUtilizationTracker) Serialize() ([]byte, error) {
	var buf bytes.Buffer
	encoder := gob.NewEncoder(&buf)

	var requests []ReconfigurationRequest
	for e := tracker.Requests.Front(); e != nil; e = e.Next() {
		requests = append(requests, e.Value.(ReconfigurationRequest))
	}

	err := encoder.Encode(requests)
	if err != nil {
		return nil, err
	}

	return buf.Bytes(), nil
}

func (tracker *ReconfigurationBasedFPGAUtilizationTracker) Deserialize(data []byte) error {
	buf := bytes.NewBuffer(data)
	decoder := gob.NewDecoder(buf)

	var exportable []ReconfigurationRequest
	err := decoder.Decode(&exportable)
	if err != nil {
		return err
	}

	tracker.recentReconfigurationTime = 0
	for _, value := range exportable {
		tracker.Requests.PushBack(value)
		tracker.recentReconfigurationTime += value.ReconfigurationTime
	}

	return nil
}

type BitstreamIdentifierRequest struct {
	BitstreamIdentifier string
	Timestamp           time.Time
}

type BitstreamIdentifierTracker struct {
	recentBitstreams map[string]struct{}
	Requests         *list.List
}

func NewBitstreamIdentifierTracker() *BitstreamIdentifierTracker {
	return &BitstreamIdentifierTracker{
		Requests:         list.New(),
		recentBitstreams: make(map[string]struct{}),
	}
}

func (tracker *BitstreamIdentifierTracker) Decay() {
	// Remove older requests (more than 1 minute old)
	for e := tracker.Requests.Front(); e != nil; {
		next := e.Next()

		req := e.Value.(BitstreamIdentifierRequest)
		if time.Now().Sub(req.Timestamp) > 1*time.Minute {
			tracker.Requests.Remove(e)
			delete(tracker.recentBitstreams, req.BitstreamIdentifier)
		}

		e = next
	}
}

func (tracker *BitstreamIdentifierTracker) AddRequest(bitstreamIdentifier string, timestampMillis int64) {
	timeFromTimestamp := time.Unix(0, timestampMillis*int64(time.Millisecond))

	// Add new request
	tracker.Requests.PushBack(BitstreamIdentifierRequest{
		BitstreamIdentifier: bitstreamIdentifier,
		Timestamp:           timeFromTimestamp,
	})
	tracker.recentBitstreams[bitstreamIdentifier] = struct{}{}
}

func (tracker *BitstreamIdentifierTracker) GetRecentBitstreamIdentifiers() map[string]struct{} {
	return tracker.recentBitstreams
}

func (tracker *BitstreamIdentifierTracker) Serialize() ([]byte, error) {
	var buf bytes.Buffer
	encoder := gob.NewEncoder(&buf)

	var requests []BitstreamIdentifierRequest
	for e := tracker.Requests.Front(); e != nil; e = e.Next() {
		requests = append(requests, e.Value.(BitstreamIdentifierRequest))
	}

	err := encoder.Encode(requests)
	if err != nil {
		return nil, err
	}

	return buf.Bytes(), nil
}

func (tracker *BitstreamIdentifierTracker) Deserialize(data []byte) error {
	buf := bytes.NewBuffer(data)
	decoder := gob.NewDecoder(buf)

	var exportable []BitstreamIdentifierRequest

	err := decoder.Decode(&exportable)
	if err != nil {
		return err
	}

	tracker.recentBitstreams = make(map[string]struct{})
	for _, value := range exportable {
		tracker.Requests.PushBack(value)
		tracker.recentBitstreams[value.BitstreamIdentifier] = struct{}{}
	}

	return nil
}
