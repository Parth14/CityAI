# Activate Browser Use API - Integration Guide

Base URL: `https://activate-browser-use.onrender.com`

This guide shows how to integrate with the Activate Browser Use API from Python and TypeScript applications.

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/value` | Get just the activation value (0 or 1) |
| GET | `/status` | Get current activation status (detailed) |
| POST | `/activate` | Set activation state to 1 |
| POST | `/deactivate` | Set activation state to 0 |
| GET | `/health` | Health check |

## Python Integration

### Prerequisites
```bash
pip install requests
```

### Basic Usage

```python
import requests
import json

BASE_URL = "https://activate-browser-use.onrender.com"

class BrowserUseActivator:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    def get_value(self):
        """Get just the activation value (0 or 1)"""
        try:
            response = requests.get(f"{self.base_url}/value")
            response.raise_for_status()
            return response.json()  # Returns just 0 or 1
        except requests.exceptions.RequestException as e:
            print(f"Error getting value: {e}")
            return None
    
    def get_status(self):
        """Get current activation status"""
        try:
            response = requests.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting status: {e}")
            return None
    
    def activate(self):
        """Activate the service (set to 1)"""
        try:
            response = requests.post(f"{self.base_url}/activate")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error activating: {e}")
            return None
    
    def deactivate(self):
        """Deactivate the service (set to 0)"""
        try:
            response = requests.post(f"{self.base_url}/deactivate")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error deactivating: {e}")
            return None
    
    def is_active(self):
        """Check if service is currently active"""
        status = self.get_status()
        return status and status.get("value") == 1

# Example usage
activator = BrowserUseActivator()

# Get just the value (0 or 1)
value = activator.get_value()
print(f"Current value: {value}")  # Output: 0 or 1

# Get detailed status
status = activator.get_status()
print(f"Detailed status: {status}")  # Output: {"value": 0, "status": "inactive"}

# Activate the service
result = activator.activate()
print(f"Activation result: {result}")

# Check if active
if activator.is_active():
    print("Service is now active!")
    
# Deactivate when done
deactivate_result = activator.deactivate()
print(f"Deactivation result: {deactivate_result}")
```

### Async Python Example (with aiohttp)

```python
import aiohttp
import asyncio

BASE_URL = "https://activate-browser-use.onrender.com"

class AsyncBrowserUseActivator:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
    
    async def get_value(self, session):
        """Get just the activation value (0 or 1)"""
        try:
            async with session.get(f"{self.base_url}/value") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error getting value: {e}")
            return None
    
    async def get_status(self, session):
        """Get current activation status"""
        try:
            async with session.get(f"{self.base_url}/status") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error getting status: {e}")
            return None
    
    async def activate(self, session):
        """Activate the service"""
        try:
            async with session.post(f"{self.base_url}/activate") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error activating: {e}")
            return None
    
    async def deactivate(self, session):
        """Deactivate the service"""
        try:
            async with session.post(f"{self.base_url}/deactivate") as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error deactivating: {e}")
            return None

# Example usage
async def main():
    activator = AsyncBrowserUseActivator()
    
    async with aiohttp.ClientSession() as session:
        # Check status
        status = await activator.get_status(session)
        print(f"Status: {status}")
        
        # Activate
        await activator.activate(session)
        print("Service activated")
        
        # Verify activation
        status = await activator.get_status(session)
        print(f"New status: {status}")

# Run the async example
# asyncio.run(main())
```

## TypeScript/JavaScript Integration

### Prerequisites
```bash
npm install axios
# or
npm install node-fetch
```

### Basic Usage with Axios

```typescript
import axios, { AxiosResponse } from 'axios';

const BASE_URL = 'https://activate-browser-use.onrender.com';

interface StatusResponse {
  value: number;
  status: string;
}

interface ActivationResponse {
  value: number;
  message: string;
}

class BrowserUseActivator {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getValue(): Promise<number | null> {
    try {
      const response: AxiosResponse<number> = await axios.get(
        `${this.baseUrl}/value`
      );
      return response.data;
    } catch (error) {
      console.error('Error getting value:', error);
      return null;
    }
  }

  async getValue(): Promise<number | null> {
    try {
      const response = await fetch(`${this.baseUrl}/value`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting value:', error);
      return null;
    }
  }

  async getStatus(): Promise<StatusResponse | null> {
    try {
      const response: AxiosResponse<StatusResponse> = await axios.get(
        `${this.baseUrl}/status`
      );
      return response.data;
    } catch (error) {
      console.error('Error getting status:', error);
      return null;
    }
  }

  async activate(): Promise<ActivationResponse | null> {
    try {
      const response: AxiosResponse<ActivationResponse> = await axios.post(
        `${this.baseUrl}/activate`
      );
      return response.data;
    } catch (error) {
      console.error('Error activating:', error);
      return null;
    }
  }

  async deactivate(): Promise<ActivationResponse | null> {
    try {
      const response: AxiosResponse<ActivationResponse> = await axios.post(
        `${this.baseUrl}/deactivate`
      );
      return response.data;
    } catch (error) {
      console.error('Error deactivating:', error);
      return null;
    }
  }

  async isActive(): Promise<boolean> {
    const status = await this.getStatus();
    return status ? status.value === 1 : false;
  }
}

// Example usage
async function example() {
  const activator = new BrowserUseActivator();

  // Check current status
  const status = await activator.getStatus();
  console.log('Current status:', status);

  // Activate the service
  const activationResult = await activator.activate();
  console.log('Activation result:', activationResult);

  // Check if active
  const isActive = await activator.isActive();
  console.log('Is active:', isActive);

  // Deactivate when done
  const deactivationResult = await activator.deactivate();
  console.log('Deactivation result:', deactivationResult);
}
```

### Using Native Fetch (Node.js/Browser)

```typescript
const BASE_URL = 'https://activate-browser-use.onrender.com';

interface StatusResponse {
  value: number;
  status: string;
}

interface ActivationResponse {
  value: number;
  message: string;
}

class SimpleBrowserUseActivator {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  async getStatus(): Promise<StatusResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/status`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error getting status:', error);
      return null;
    }
  }

  async activate(): Promise<ActivationResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/activate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error activating:', error);
      return null;
    }
  }

  async deactivate(): Promise<ActivationResponse | null> {
    try {
      const response = await fetch(`${this.baseUrl}/deactivate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error deactivating:', error);
      return null;
    }
  }

  async waitForActivation(timeoutMs: number = 30000): Promise<boolean> {
    const startTime = Date.now();
    
    while (Date.now() - startTime < timeoutMs) {
      const status = await this.getStatus();
      if (status && status.value === 1) {
        return true;
      }
      await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
    }
    
    return false;
  }
}

// Example usage
async function exampleUsage() {
  const activator = new SimpleBrowserUseActivator();

  console.log('Checking initial status...');
  const initialStatus = await activator.getStatus();
  console.log('Initial status:', initialStatus);

  console.log('Activating service...');
  await activator.activate();

  console.log('Waiting for activation...');
  const isActivated = await activator.waitForActivation(10000);
  console.log('Service activated:', isActivated);

  // Do your work here while service is active
  console.log('Service is active, doing work...');
  
  console.log('Deactivating service...');
  await activator.deactivate();
  console.log('Service deactivated');
}

// Run the example
// exampleUsage();
```

## Common Integration Patterns

### Pattern 1: Service Coordination
Use this when multiple services need to coordinate:

```python
# Service A - Worker that waits for activation
import time

def worker_service():
    activator = BrowserUseActivator()
    
    while True:
        if activator.is_active():
            print("Service is active, performing work...")
            # Do your work here
            time.sleep(5)
        else:
            print("Service inactive, waiting...")
            time.sleep(2)

# Service B - Controller that activates
def controller_service():
    activator = BrowserUseActivator()
    
    # Activate when needed
    activator.activate()
    print("Work initiated")
    
    # Let it run for a while
    time.sleep(30)
    
    # Deactivate when done
    activator.deactivate()
    print("Work completed")
```

### Pattern 2: Health Monitoring
```typescript
// Monitor service health and activation status
class ServiceMonitor {
  private activator: SimpleBrowserUseActivator;
  
  constructor() {
    this.activator = new SimpleBrowserUseActivator();
  }
  
  async startMonitoring() {
    setInterval(async () => {
      const status = await this.activator.getStatus();
      if (status) {
        console.log(`[${new Date().toISOString()}] Service status: ${status.status} (value: ${status.value})`);
      } else {
        console.error('Failed to get service status');
      }
    }, 5000); // Check every 5 seconds
  }
}

const monitor = new ServiceMonitor();
monitor.startMonitoring();
```

## Error Handling Best Practices

1. **Always handle network errors** - The service might be temporarily unavailable
2. **Implement retries** - For critical operations, add retry logic
3. **Use timeouts** - Don't wait indefinitely for responses
4. **Log appropriately** - Include enough context for debugging
5. **Fallback behavior** - Have a plan when the service is unavailable

## Testing

You can test the API directly with curl:

```bash
# Get just the value (0 or 1)
curl https://activate-browser-use.onrender.com/value

# Get detailed status
curl https://activate-browser-use.onrender.com/status

# Activate
curl -X POST https://activate-browser-use.onrender.com/activate

# Deactivate  
curl -X POST https://activate-browser-use.onrender.com/deactivate

# Health check
curl https://activate-browser-use.onrender.com/health
```

```powershell
# Get the simple value (0 or 1)
Invoke-RestMethod -Uri "https://activate-browser-use.onrender.com/value" -Method Get

# Get detailed status
Invoke-RestMethod -Uri "https://activate-browser-use.onrender.com/status" -Method Get

# Activate (set to 1)
Invoke-RestMethod -Uri "https://activate-browser-use.onrender.com/activate" -Method Post

# Deactivate (set to 0)
Invoke-RestMethod -Uri "https://activate-browser-use.onrender.com/deactivate" -Method Post

# Health check
Invoke-RestMethod -Uri "https://activate-browser-use.onrender.com/health" -Method Get
```