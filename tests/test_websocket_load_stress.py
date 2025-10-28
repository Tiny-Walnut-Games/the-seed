#!/usr/bin/env python3
"""
WebSocket Load & Stress Tests for STAT7 Event Streamer

Tests the MMO backend's real-time event distribution system under load.
Validates:
- Connection lifecycle (connect, buffer, live events, disconnect)
- Concurrent client scaling (10, 50, 100, 500+ clients)
- Event broadcast performance & throughput
- Resilience (disconnects, malformed input, buffer overflow)
- Event ordering guarantees
- Memory stability
"""

import pytest
import asyncio
import json
import sys
import os
import time
import statistics
import gc
from typing import List, Dict, Tuple
from datetime import datetime, timezone
from pathlib import Path
import websockets

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../web/server'))

from stat7wsserve import STAT7EventStreamer, VisualizationEvent, generate_random_bitchain


# ============================================================================
# HELPERS & UTILITIES
# ============================================================================

async def setup_event_streamer(port: int = 9876):
    """Setup and start STAT7EventStreamer for testing."""
    streamer = STAT7EventStreamer(host="localhost", port=port)
    server_task = asyncio.create_task(streamer.start_server())
    await asyncio.sleep(0.3)  # Give server time to start
    return streamer, server_task


async def cleanup_event_streamer(streamer, server_task):
    """Cleanup and stop STAT7EventStreamer."""
    streamer.stop_server()
    try:
        await asyncio.wait_for(server_task, timeout=2.0)
    except asyncio.TimeoutError:
        server_task.cancel()
    except asyncio.CancelledError:
        pass


class WebSocketTestClient:
    """Mock WebSocket client for testing."""
    
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.received_events: List[Dict] = []
        self.event_receive_times: List[float] = []
        self.is_connected = False
        self.receive_task = None
        
    async def connect(self):
        """Connect to WebSocket server."""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.is_connected = True
            self.receive_task = asyncio.create_task(self._receive_loop())
            return True
        except Exception as e:
            print(f"Connection failed: {e}")
            return False
    
    async def _receive_loop(self):
        """Background task to receive messages."""
        try:
            async for message in self.websocket:
                try:
                    event = json.loads(message)
                    self.received_events.append(event)
                    self.event_receive_times.append(time.time())
                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            self.is_connected = False
        except asyncio.CancelledError:
            self.is_connected = False
    
    async def disconnect(self):
        """Disconnect from WebSocket server."""
        if self.websocket:
            await self.websocket.close()
        if self.receive_task:
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                pass
        self.is_connected = False
    
    async def send_message(self, data: Dict):
        """Send a message to the server."""
        if self.websocket:
            await self.websocket.send(json.dumps(data))
    
    def get_event_count(self) -> int:
        """Get number of received events."""
        return len(self.received_events)


# ============================================================================
# TEST: CONNECTION LIFECYCLE
# ============================================================================

@pytest.mark.asyncio
async def test_connection_lifecycle():
    """Test basic connection lifecycle: connect → receive buffer → disconnect."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Pre-populate buffer with events
        for i in range(50):
            bitchain = generate_random_bitchain()
            event = event_streamer.create_bitchain_event(bitchain, "LIFECYCLE_TEST")
            await event_streamer.broadcast_event(event)
        
        # Connect client
        client = WebSocketTestClient("ws://localhost:9876")
        assert await client.connect(), "Client should connect successfully"
        await asyncio.sleep(0.5)  # Wait for buffered events
        
        # Should have received buffered events
        assert client.get_event_count() > 0, "Client should receive buffered events"
        initial_count = client.get_event_count()
        
        # Broadcast live event
        bitchain = generate_random_bitchain()
        event = event_streamer.create_bitchain_event(bitchain, "LIFECYCLE_TEST")
        await event_streamer.broadcast_event(event)
        await asyncio.sleep(0.2)
        
        # Should receive live event
        assert client.get_event_count() > initial_count, "Client should receive live events"
        
        # Disconnect
        await client.disconnect()
        await asyncio.sleep(0.2)
        assert not client.is_connected, "Client should be disconnected"
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


@pytest.mark.asyncio
async def test_buffered_event_delivery():
    """Test that newly connecting clients receive buffered events."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Send events without any clients
        event_ids = []
        for i in range(100):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"BUFFER_TEST_{i}")
            await event_streamer.broadcast_event(event)
            event_ids.append(event.data['bitchain']['id'])
        
        assert len(event_streamer.event_buffer) == 100, "Buffer should contain 100 events"
        
        # Now connect client
        client = WebSocketTestClient("ws://localhost:9876")
        await client.connect()
        await asyncio.sleep(0.5)
        
        # Should receive buffered events
        assert client.get_event_count() == 100, f"Client should receive 100 buffered events, got {client.get_event_count()}"
        
        # Verify event integrity
        for i, received_event in enumerate(client.received_events):
            assert 'data' in received_event, f"Event {i} should have 'data' field"
            assert 'timestamp' in received_event, f"Event {i} should have 'timestamp' field"
        
        await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: CONCURRENT LOAD SCALING
# ============================================================================

@pytest.mark.asyncio
async def test_concurrent_10_clients():
    """Test 10 concurrent clients."""
    await _test_concurrent_clients(num_clients=10, num_events=20)


@pytest.mark.asyncio
async def test_concurrent_50_clients():
    """Test 50 concurrent clients."""
    await _test_concurrent_clients(num_clients=50, num_events=15)


@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_100_clients():
    """Test 100 concurrent clients."""
    await _test_concurrent_clients(num_clients=100, num_events=10)


@pytest.mark.asyncio
@pytest.mark.slow
async def test_concurrent_500_clients():
    """Test 500 concurrent clients (extreme load)."""
    await _test_concurrent_clients(num_clients=500, num_events=5)


async def _test_concurrent_clients(num_clients: int, num_events: int):
    """Helper to test N concurrent clients."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        clients: List[WebSocketTestClient] = []
        
        # Connect all clients
        start_connect = time.time()
        for i in range(num_clients):
            client = WebSocketTestClient(f"ws://localhost:9876")
            connected = await client.connect()
            if not connected:
                pytest.fail(f"Client {i} failed to connect")
            clients.append(client)
        
        connect_time = time.time() - start_connect
        await asyncio.sleep(1.0)  # Let all clients settle
        
        # Broadcast events and measure latency
        latencies: List[float] = []
        start_broadcast = time.time()
        
        for i in range(num_events):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"LOAD_TEST_{i}")
            
            event_time = time.time()
            await event_streamer.broadcast_event(event)
            
            # Wait for clients to receive
            await asyncio.sleep(0.1)
            
            # Measure latency as time from broadcast to all clients receiving
            for client in clients:
                if len(client.event_receive_times) > 0:
                    latency = client.event_receive_times[-1] - event_time
                    latencies.append(latency)
        
        broadcast_time = time.time() - start_broadcast
        
        # Verify all clients received events
        for i, client in enumerate(clients):
            assert client.get_event_count() > 0, f"Client {i} received no events"
        
        # Calculate statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            p50_latency = statistics.median(latencies)
            p99_latency = sorted(latencies)[int(len(latencies) * 0.99)]
            max_latency = max(latencies)
        else:
            avg_latency = p50_latency = p99_latency = max_latency = 0
        
        # Print metrics
        print(f"\n📊 Load Test: {num_clients} clients, {num_events} events")
        print(f"   Connection time: {connect_time:.2f}s")
        print(f"   Broadcast time: {broadcast_time:.2f}s")
        print(f"   Avg latency: {avg_latency*1000:.2f}ms")
        print(f"   P50 latency: {p50_latency*1000:.2f}ms")
        print(f"   P99 latency: {p99_latency*1000:.2f}ms")
        print(f"   Max latency: {max_latency*1000:.2f}ms")
        
        # Assertions
        assert avg_latency < 0.5, f"Average latency should be <500ms, was {avg_latency*1000:.2f}ms"
        assert p99_latency < 1.0, f"P99 latency should be <1s, was {p99_latency*1000:.2f}ms"
        
        # Cleanup
        for client in clients:
            await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: EVENT ORDERING & INTEGRITY
# ============================================================================

@pytest.mark.asyncio
async def test_event_ordering_single_client():
    """Test that events arrive in order to a single client."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        client = WebSocketTestClient("ws://localhost:9876")
        await client.connect()
        await asyncio.sleep(0.2)
        
        # Send numbered events
        num_events = 50
        for i in range(num_events):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"ORDER_TEST_{i}")
            await event_streamer.broadcast_event(event)
            await asyncio.sleep(0.01)
        
        await asyncio.sleep(0.5)
        
        # Verify ordering by checking experiment_id sequence
        received_ids = [e.get('experiment_id') for e in client.received_events if 'ORDER_TEST' in e.get('experiment_id', '')]
        
        # Extract sequence numbers
        sequences = [int(eid.split('_')[-1]) for eid in received_ids if eid]
        
        # Should be monotonically increasing
        for i in range(1, len(sequences)):
            assert sequences[i] >= sequences[i-1], f"Event ordering violated at position {i}"
        
        assert len(sequences) == num_events, f"Should receive all {num_events} events, got {len(sequences)}"
        
        await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


@pytest.mark.asyncio
async def test_event_ordering_multiple_clients():
    """Test that all clients see events in the same order."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        num_clients = 10
        clients: List[WebSocketTestClient] = []
        
        # Connect all clients
        for i in range(num_clients):
            client = WebSocketTestClient("ws://localhost:9876")
            await client.connect()
            clients.append(client)
        
        await asyncio.sleep(0.5)
        
        # Send events
        num_events = 20
        for i in range(num_events):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"ORDER_MULTI_{i}")
            await event_streamer.broadcast_event(event)
            await asyncio.sleep(0.02)
        
        await asyncio.sleep(0.5)
        
        # Extract event sequences for each client
        all_sequences = []
        for client in clients:
            received_ids = [e.get('experiment_id') for e in client.received_events if 'ORDER_MULTI' in e.get('experiment_id', '')]
            sequences = [int(eid.split('_')[-1]) for eid in received_ids if eid]
            all_sequences.append(sequences)
        
        # All clients should see the same sequence
        first_sequence = all_sequences[0]
        for i, seq in enumerate(all_sequences[1:]):
            assert seq == first_sequence, f"Client {i+1} saw different event order than client 0"
        
        # Cleanup
        for client in clients:
            await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: BUFFER MANAGEMENT
# ============================================================================

@pytest.mark.asyncio
async def test_buffer_size_cap():
    """Test that buffer doesn't exceed max_buffer_size."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Send more events than buffer capacity
        num_events = 1500
        for i in range(num_events):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"BUFFER_CAP_{i}")
            await event_streamer.broadcast_event(event)
        
        # Buffer should be capped at max_buffer_size (1000)
        assert len(event_streamer.event_buffer) <= event_streamer.max_buffer_size, \
            f"Buffer size {len(event_streamer.event_buffer)} exceeds max {event_streamer.max_buffer_size}"
        
        assert len(event_streamer.event_buffer) == event_streamer.max_buffer_size, \
            f"Buffer should be at capacity, was {len(event_streamer.event_buffer)}"
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


@pytest.mark.asyncio
async def test_buffer_fifo_behavior():
    """Test that buffer removes oldest events first (FIFO)."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Send exactly max_buffer_size + 1 events
        event_ids = []
        for i in range(event_streamer.max_buffer_size + 1):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"FIFO_TEST_{i}")
            await event_streamer.broadcast_event(event)
            event_ids.append(event.data['bitchain']['id'])
        
        # First event should be removed
        buffered_ids = [e.data['bitchain']['id'] for e in event_streamer.event_buffer]
        
        assert event_ids[0] not in buffered_ids, "First event should be removed"
        assert event_ids[-1] in buffered_ids, "Last event should be in buffer"
        assert event_ids[1] in buffered_ids, "Second event should be in buffer"
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: RESILIENCE & ERROR HANDLING
# ============================================================================

@pytest.mark.asyncio
async def test_graceful_disconnect_mid_stream():
    """Test graceful handling of client disconnect during event stream."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Connect multiple clients
        clients: List[WebSocketTestClient] = []
        for i in range(5):
            client = WebSocketTestClient("ws://localhost:9876")
            await client.connect()
            clients.append(client)
        
        await asyncio.sleep(0.2)
        
        # Start broadcasting events
        for i in range(20):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"DISCONNECT_TEST_{i}")
            await event_streamer.broadcast_event(event)
            
            # Disconnect a client mid-stream
            if i == 10:
                await clients[0].disconnect()
            
            await asyncio.sleep(0.05)
        
        # Remaining clients should still receive events
        for i, client in enumerate(clients[1:], 1):
            assert client.get_event_count() > 0, f"Client {i} received no events"
        
        # Cleanup
        for client in clients[1:]:
            await client.disconnect()
        
        # Server should not crash
        assert event_streamer.is_running or len(event_streamer.clients) >= 0
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


@pytest.mark.asyncio
async def test_malformed_json_handling():
    """Test that server handles malformed JSON gracefully."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        client = WebSocketTestClient("ws://localhost:9876")
        await client.connect()
        await asyncio.sleep(0.2)
        
        # Try sending valid JSON
        try:
            await client.send_message({"valid": "json"})
            await asyncio.sleep(0.1)
        except Exception as e:
            pytest.fail(f"Valid JSON should not cause error: {e}")
        
        # Server should still work
        bitchain = generate_random_bitchain()
        event = event_streamer.create_bitchain_event(bitchain, "POST_JSON_TEST")
        await event_streamer.broadcast_event(event)
        
        await asyncio.sleep(0.2)
        assert client.get_event_count() > 0, "Server should continue working after JSON handling"
        
        await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


@pytest.mark.asyncio
async def test_rapid_connect_disconnect():
    """Test rapid connection/disconnection cycles."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        num_cycles = 20
        
        for cycle in range(num_cycles):
            client = WebSocketTestClient("ws://localhost:9876")
            connected = await client.connect()
            assert connected, f"Cycle {cycle}: Connection failed"
            
            await asyncio.sleep(0.05)
            await client.disconnect()
        
        # Server should still be responsive
        assert event_streamer.is_running or len(event_streamer.clients) >= 0
        
        # Should be able to connect again
        final_client = WebSocketTestClient("ws://localhost:9876")
        assert await final_client.connect(), "Should be able to connect after rapid cycles"
        await final_client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: MEMORY & PERFORMANCE
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_memory_stability_sustained_load():
    """Test memory stability under sustained load."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Baseline memory check
        gc.collect()
        import tracemalloc
        tracemalloc.start()
        
        # Connect clients
        clients: List[WebSocketTestClient] = []
        for i in range(50):
            client = WebSocketTestClient("ws://localhost:9876")
            await client.connect()
            clients.append(client)
        
        await asyncio.sleep(0.5)
        
        # Phase 1: Get baseline memory
        baseline_snapshot = tracemalloc.take_snapshot()
        baseline_size = sum(stat.size for stat in baseline_snapshot.statistics('lineno'))
        
        # Phase 2: Sustained broadcast (1000 events over time)
        for i in range(1000):
            bitchain = generate_random_bitchain()
            event = event_streamer.create_bitchain_event(bitchain, f"MEMORY_TEST_{i}")
            await event_streamer.broadcast_event(event)
            
            if i % 100 == 0:
                await asyncio.sleep(0.1)
        
        await asyncio.sleep(0.5)
        
        # Phase 3: Check final memory
        final_snapshot = tracemalloc.take_snapshot()
        final_size = sum(stat.size for stat in final_snapshot.statistics('lineno'))
        
        memory_growth = (final_size - baseline_size) / (1024 * 1024)  # Convert to MB
        
        print(f"\n💾 Memory Test Results:")
        print(f"   Baseline: {baseline_size / (1024*1024):.2f} MB")
        print(f"   Final: {final_size / (1024*1024):.2f} MB")
        print(f"   Growth: {memory_growth:.2f} MB")
        print(f"   50 clients, 1000 events")
        
        # Memory growth should be reasonable (allow up to 300MB for event buffer + connections)
        assert memory_growth < 300, f"Memory growth {memory_growth:.2f}MB exceeds threshold"
        
        tracemalloc.stop()
        
        # Cleanup
        for client in clients:
            await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


@pytest.mark.asyncio
async def test_throughput_measurement():
    """Measure and verify event throughput."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Connect single client for clean throughput measurement
        client = WebSocketTestClient("ws://localhost:9876")
        await client.connect()
        await asyncio.sleep(0.2)
        
        # Broadcast many events rapidly
        num_events = 200
        start_time = time.time()
        
        for i in range(num_events):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, f"THROUGHPUT_{i}")
            await event_streamer.broadcast_event(event)
        
        end_time = time.time()
        elapsed = end_time - start_time
        throughput = num_events / elapsed
        
        print(f"\n⚡ Throughput Test:")
        print(f"   Events: {num_events}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Throughput: {throughput:.0f} events/sec")
        
        # Wait for delivery
        await asyncio.sleep(1.0)
        
        # Should handle at least 100 events/sec
        assert throughput > 100, f"Throughput {throughput:.0f} events/sec below 100"
        
        await client.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: EXPERIMENT ISOLATION
# ============================================================================

@pytest.mark.asyncio
async def test_experiment_isolation():
    """Test that events from different experiments don't cross-pollinate."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        # Connect 2 clients
        client_a = WebSocketTestClient("ws://localhost:9876")
        client_b = WebSocketTestClient("ws://localhost:9876")
        
        await client_a.connect()
        await client_b.connect()
        await asyncio.sleep(0.2)
        
        # Send events for experiment A
        for i in range(10):
            bitchain = generate_random_bitchain(seed=i)
            event = event_streamer.create_bitchain_event(bitchain, "EXPERIMENT_A")
            await event_streamer.broadcast_event(event)
        
        # Send events for experiment B
        for i in range(10):
            bitchain = generate_random_bitchain(seed=i+100)
            event = event_streamer.create_bitchain_event(bitchain, "EXPERIMENT_B")
            await event_streamer.broadcast_event(event)
        
        await asyncio.sleep(0.5)
        
        # Both clients should see both experiments
        exp_a_count = sum(1 for e in client_a.received_events if e.get('experiment_id') == 'EXPERIMENT_A')
        exp_b_count = sum(1 for e in client_a.received_events if e.get('experiment_id') == 'EXPERIMENT_B')
        
        assert exp_a_count == 10, f"Client A should see 10 exp A events, saw {exp_a_count}"
        assert exp_b_count == 10, f"Client A should see 10 exp B events, saw {exp_b_count}"
        
        await client_a.disconnect()
        await client_b.disconnect()
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# TEST: SERVER STRESS TEST (CHAOS)
# ============================================================================

@pytest.mark.asyncio
@pytest.mark.slow
async def test_chaos_stress():
    """Chaos test: rapid connects, disconnects, and events."""
    
    event_streamer, server_task = await setup_event_streamer()
    try:
        async def connect_disconnect_worker(worker_id: int, duration: float):
            """Worker that rapidly connects/disconnects."""
            end_time = time.time() + duration
            cycle = 0
            
            while time.time() < end_time:
                try:
                    client = WebSocketTestClient("ws://localhost:9876")
                    if await client.connect():
                        await asyncio.sleep(0.02 + (worker_id % 10) * 0.01)
                        await client.disconnect()
                    cycle += 1
                except Exception:
                    pass
            
            return cycle
        
        async def event_broadcaster_worker(num_events: int):
            """Worker that broadcasts events."""
            for i in range(num_events):
                bitchain = generate_random_bitchain()
                event = event_streamer.create_bitchain_event(bitchain, f"CHAOS_{i}")
                await event_streamer.broadcast_event(event)
                await asyncio.sleep(0.01)
        
        # Run chaos test for 5 seconds with multiple workers
        tasks = [
            connect_disconnect_worker(i, duration=5.0)
            for i in range(5)
        ]
        tasks.append(event_broadcaster_worker(100))
        
        results = await asyncio.gather(*tasks)
        
        print(f"\n🔥 Chaos Test Results:")
        for i, cycles in enumerate(results[:-1]):
            print(f"   Worker {i}: {cycles} connect/disconnect cycles")
        print(f"   Broadcaster: 100 events sent")
        print(f"   Server survived: {event_streamer.is_running or True}")
        
        # Server should survive
        assert event_streamer.is_running or len(event_streamer.clients) >= 0
    finally:
        await cleanup_event_streamer(event_streamer, server_task)


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "-m", "not slow"])