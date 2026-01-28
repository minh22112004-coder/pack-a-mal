# Network Simulation Example

This example demonstrates how Pack-A-Mal's network simulation feature works with INetSim to safely analyze malicious packages that make network requests.

## Overview

The network simulation redirects all network traffic from analyzed packages to INetSim, allowing you to:
- Capture malicious network behavior without real C2 communication
- Analyze packages that contact dead/expired domains
- Log all DNS queries and HTTP requests
- Safely test packages with network-based malware

## Files

- `demo_network_simulation.py` - Interactive demo showing network simulation capabilities

## Prerequisites

1. INetSim running via docker-compose:
   ```bash
   cd ..
   docker-compose -f docker-compose.network-sim.yml up -d
   ```

2. Python with requests library:
   ```bash
   pip install requests
   ```

## Usage

Run the demo:
```bash
python demo_network_simulation.py
```

The demo will:
1. Show current configuration
2. Test URL liveness detection
3. Explain how network simulation works
4. Check INetSim service status
5. Provide next steps

## Configuration

Enable network simulation by setting environment variables:

**Windows (PowerShell):**
```powershell
$env:OSSF_NETWORK_SIMULATION_ENABLED='true'
$env:OSSF_INETSIM_DNS_ADDR='172.20.0.2:53'
$env:OSSF_INETSIM_HTTP_ADDR='172.20.0.2:80'
```

**Linux/Mac (Bash):**
```bash
export OSSF_NETWORK_SIMULATION_ENABLED=true
export OSSF_INETSIM_DNS_ADDR=172.20.0.2:53
export OSSF_INETSIM_HTTP_ADDR=172.20.0.2:80
```

## How It Works

When network simulation is enabled:

1. **Before Analysis**: Worker configures sandbox with INetSim DNS server
2. **During Analysis**: Package network requests are redirected to INetSim
3. **After Analysis**: All network activity is logged and captured

Example flow:
```
Package code → requests.get("http://malicious-c2.example.com/data")
             ↓
INetSim DNS → Resolves to 172.20.0.2
             ↓
INetSim HTTP → Responds with simulated content
             ↓
Network behavior captured safely ✓
```

## Related Documentation

- [../../HUONG_DAN_CHAY.md](../../HUONG_DAN_CHAY.md) - Setup guide
- [../../README.md](../../README.md) - Main documentation
- [../../../service-simulation-module/](../../../service-simulation-module/) - INetSim configuration
