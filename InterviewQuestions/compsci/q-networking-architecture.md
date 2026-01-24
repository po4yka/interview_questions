---
id: cs-net-arch
title: Networking - Network Architecture
topic: networking
difficulty: medium
tags:
- cs_networking
- architecture
anki_cards:
- slug: cs-net-arch-0-en
  language: en
  anki_id: 1769160678674
  synced_at: '2026-01-23T13:31:19.095172'
- slug: cs-net-arch-0-ru
  language: ru
  anki_id: 1769160678701
  synced_at: '2026-01-23T13:31:19.099175'
- slug: cs-net-arch-1-en
  language: en
  anki_id: 1769160678724
  synced_at: '2026-01-23T13:31:19.100489'
- slug: cs-net-arch-1-ru
  language: ru
  anki_id: 1769160678750
  synced_at: '2026-01-23T13:31:19.101807'
---
# Network Architecture

## Network Devices

### Hub (Layer 1)

- Broadcasts to all ports
- No intelligence
- Creates collision domain
- Obsolete

### Switch (Layer 2)

- Forwards by MAC address
- Learns MAC-to-port mapping
- Creates separate collision domains
- Maintains broadcast domain

**MAC address table**:
```
MAC Address      | Port
-----------------|------
AA:BB:CC:DD:EE:FF| 1
11:22:33:44:55:66| 3
```

### Router (Layer 3)

- Forwards by IP address
- Connects different networks
- Separates broadcast domains
- Makes routing decisions

**Routing table**:
```
Destination      | Gateway       | Interface
-----------------|---------------|----------
192.168.1.0/24   | 0.0.0.0       | eth0
10.0.0.0/8       | 192.168.1.1   | eth0
0.0.0.0/0        | 192.168.1.1   | eth0 (default)
```

### Load Balancer (Layer 4/7)

- Distributes traffic across servers
- Health checking
- SSL termination (L7)
- Session persistence

**Algorithms**:
- Round Robin
- Least Connections
- Weighted
- IP Hash
- Least Response Time

## NAT (Network Address Translation)

Translates private IPs to public IPs.

**Types**:
- **SNAT**: Source NAT (outgoing)
- **DNAT**: Destination NAT (incoming)
- **PAT/NAPT**: Port-based NAT (many-to-one)

```
Internal Network        NAT Router         Internet
192.168.1.10:5000  --> 203.0.113.1:10000  --> Server
192.168.1.20:6000  --> 203.0.113.1:10001  --> Server
```

**NAT table**:
```
Internal IP:Port    | External Port
--------------------|---------------
192.168.1.10:5000   | 10000
192.168.1.20:6000   | 10001
```

## Subnetting

Divide network into smaller networks.

**Subnet mask**: Identifies network vs host bits.

```
IP:          192.168.  1.  100
Mask:        255.255.255.  0
Binary mask: 11111111.11111111.11111111.00000000
CIDR:        /24

Network:     192.168.1.0
Broadcast:   192.168.1.255
Hosts:       192.168.1.1 - 192.168.1.254 (254 hosts)
```

**Subnet calculation**:
```
/24 = 256 addresses, 254 hosts
/25 = 128 addresses, 126 hosts (2 subnets from /24)
/26 = 64 addresses, 62 hosts (4 subnets from /24)
```

## VLANs (Virtual LANs)

Logical network segmentation at Layer 2.

**Benefits**:
- Security isolation
- Reduced broadcast domain
- Flexibility

**802.1Q tagging**: 4-byte tag in Ethernet frame.
```
[Dest MAC | Src MAC | 802.1Q Tag | Type | Data | FCS]
                     ^
              VLAN ID (12 bits = 4096 VLANs)
```

## Sockets

Endpoint for communication.

```python
# TCP Server
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 8080))
server.listen(5)

while True:
    client, addr = server.accept()
    data = client.recv(1024)
    client.send(b'Response')
    client.close()
```

```python
# TCP Client
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('server.com', 8080))
client.send(b'Request')
response = client.recv(1024)
client.close()
```

### Socket States (TCP)

```
CLOSED -> LISTEN (server)
CLOSED -> SYN_SENT -> ESTABLISHED (client)
LISTEN -> SYN_RECEIVED -> ESTABLISHED (server)
ESTABLISHED -> FIN_WAIT_1 -> FIN_WAIT_2 -> TIME_WAIT -> CLOSED
ESTABLISHED -> CLOSE_WAIT -> LAST_ACK -> CLOSED
```

**TIME_WAIT**: 2*MSL wait to handle delayed packets.

## WebSockets

Full-duplex communication over single TCP connection.

**Handshake** (HTTP upgrade):
```
Request:
GET /chat HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13

Response:
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

**Use cases**: Chat, real-time updates, gaming.

## CDN (Content Delivery Network)

Distributed servers caching content near users.

**Benefits**:
- Reduced latency
- Lower origin load
- DDoS protection
- High availability

**Cache behavior**:
```
User -> Edge Server (cache hit) -> Return cached content
User -> Edge Server (cache miss) -> Origin -> Cache -> Return
```

**Cache headers**:
```
Cache-Control: public, max-age=86400
Vary: Accept-Encoding
ETag: "abc123"
```

## Proxy Types

### Forward Proxy

Client -> Proxy -> Server

**Use cases**: Anonymity, filtering, caching.

### Reverse Proxy

Client -> Reverse Proxy -> Server

**Use cases**: Load balancing, SSL termination, caching, security.

```
           +--------+
           | Client |
           +--------+
               |
        +------v-------+
        | Reverse Proxy|  (nginx, HAProxy)
        +------+-------+
               |
    +----------+----------+
    |          |          |
+---v---+ +----v----+ +---v---+
|Server1| | Server2 | |Server3|
+-------+ +---------+ +-------+
```

## API Gateway

Centralized entry point for microservices.

**Features**:
- Request routing
- Authentication
- Rate limiting
- Request/response transformation
- Monitoring

```
Client -> API Gateway -> Service A
                     -> Service B
                     -> Service C
```

## Firewall

Controls traffic based on rules.

**Types**:
- **Packet filter**: IP, port, protocol
- **Stateful**: Tracks connection state
- **Application (WAF)**: Inspects HTTP content

**Rules example**:
```
Allow TCP from any to 80 (HTTP)
Allow TCP from any to 443 (HTTPS)
Allow TCP from 10.0.0.0/8 to 22 (SSH internal)
Deny all
```

## Network Troubleshooting

### Tools

```bash
ping host.com        # ICMP reachability
traceroute host.com  # Path to destination
nslookup host.com    # DNS lookup
dig host.com         # Detailed DNS
netstat -an          # Network connections
ss -tuln             # Socket statistics
tcpdump              # Packet capture
curl -v url          # HTTP debugging
```

### Common Issues

| Symptom | Possible Cause |
|---------|----------------|
| No connectivity | DNS, routing, firewall |
| Slow connection | Congestion, packet loss |
| Intermittent | Load balancer, timeout |
| Connection refused | Service not running |
| Connection timeout | Firewall, wrong port |

## Interview Questions

1. **How does a load balancer work?**
   - Receives incoming requests
   - Selects backend server (algorithm)
   - Forwards request
   - Returns response to client
   - Health checks backends

2. **Difference between L4 and L7 load balancer?**
   - L4: TCP/UDP level, faster, less intelligent
   - L7: HTTP level, content routing, SSL termination

3. **What is NAT and why is it needed?**
   - Translates private to public IPs
   - Conserves IPv4 addresses
   - Provides some security (hides internal IPs)

4. **How do you troubleshoot "cannot connect to server"?**
   - Check DNS (nslookup)
   - Check network (ping)
   - Check route (traceroute)
   - Check port (telnet/nc)
   - Check firewall
   - Check service logs
