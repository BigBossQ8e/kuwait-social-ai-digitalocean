#!/usr/bin/env python
"""
Test WebSocket functionality
"""
import socketio
import time
import json
from datetime import datetime

# Create a SocketIO client
sio = socketio.Client()

# Event handlers
@sio.event
def connect():
    print("Connected to server")

@sio.event
def disconnect():
    print("Disconnected from server")

@sio.on('admin_connected')
def on_admin_connected(data):
    print(f"Admin connected: {json.dumps(data, indent=2)}")

@sio.on('platform_update')
def on_platform_update(data):
    print(f"Platform update received: {json.dumps(data, indent=2)}")

@sio.on('feature_update')
def on_feature_update(data):
    print(f"Feature update received: {json.dumps(data, indent=2)}")

@sio.on('error')
def on_error(data):
    print(f"Error: {data.get('message')}")

def test_admin_connection():
    """Test admin WebSocket connection"""
    print("Testing Admin WebSocket Connection...")
    
    # Replace with a valid admin JWT token
    auth_token = "YOUR_ADMIN_JWT_TOKEN_HERE"
    
    try:
        # Connect to admin namespace
        sio.connect(
            'http://localhost:5001',
            namespaces=['/admin'],
            auth={'token': auth_token}
        )
        
        # Wait for connection
        time.sleep(1)
        
        # Request dashboard update
        sio.emit('request_dashboard_update', {'type': 'all'}, namespace='/admin')
        
        # Wait for response
        time.sleep(2)
        
        # Subscribe to platform updates
        sio.emit('subscribe_entity_updates', {
            'entity_type': 'platform',
            'entity_id': 1
        }, namespace='/admin')
        
        # Keep connection alive for testing
        print("Listening for updates... Press Ctrl+C to stop")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sio.disconnect()

def test_client_connection():
    """Test client WebSocket connection"""
    print("Testing Client WebSocket Connection...")
    
    # Replace with a valid client JWT token
    auth_token = "YOUR_CLIENT_JWT_TOKEN_HERE"
    
    try:
        # Connect to client namespace
        sio.connect(
            'http://localhost:5001',
            namespaces=['/client'],
            auth={'token': auth_token}
        )
        
        # Wait for connection
        time.sleep(1)
        
        # Check configuration
        sio.emit('config_check', {'client_id': 1}, namespace='/client')
        
        # Send heartbeat
        sio.emit('heartbeat', {'client_id': 1}, namespace='/client')
        
        # Keep connection alive
        print("Listening for updates... Press Ctrl+C to stop")
        while True:
            time.sleep(5)
            sio.emit('heartbeat', {'client_id': 1}, namespace='/client')
            
    except KeyboardInterrupt:
        print("\nStopping test...")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        sio.disconnect()

if __name__ == '__main__':
    print("WebSocket Test Script")
    print("1. Test Admin Connection")
    print("2. Test Client Connection")
    
    choice = input("Select option (1 or 2): ")
    
    if choice == '1':
        test_admin_connection()
    elif choice == '2':
        test_client_connection()
    else:
        print("Invalid option")