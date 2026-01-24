---
id: cs-net-osi-tcp
title: Networking - OSI Model and TCP/IP
topic: networking
difficulty: medium
tags:
- cs_networking
- protocols
anki_cards:
- slug: cs-net-osi-0-en
  language: en
  anki_id: 1769160673974
  synced_at: '2026-01-23T13:31:18.782443'
- slug: cs-net-osi-0-ru
  language: ru
  anki_id: 1769160673999
  synced_at: '2026-01-23T13:31:18.784977'
- slug: cs-net-osi-1-en
  language: en
  anki_id: 1769160674024
  synced_at: '2026-01-23T13:31:18.788256'
- slug: cs-net-osi-1-ru
  language: ru
  anki_id: 1769160674049
  synced_at: '2026-01-23T13:31:18.790395'
- slug: cs-net-osi-2-en
  language: en
  anki_id: 1769160674074
  synced_at: '2026-01-23T13:31:18.792963'
- slug: cs-net-osi-2-ru
  language: ru
  anki_id: 1769160674100
  synced_at: '2026-01-23T13:31:18.795051'
---
# OSI Model and TCP/IP

## OSI Model (7 Layers)

| Layer | Name | Function | Protocols/Examples |
|-------|------|----------|-------------------|
| 7 | Application | User interface, application services | HTTP, FTP, SMTP, DNS |
| 6 | Presentation | Data formatting, encryption | SSL/TLS, JPEG, ASCII |
| 5 | Session | Session management | NetBIOS, RPC |
| 4 | Transport | End-to-end delivery, reliability | TCP, UDP |
| 3 | Network | Routing, addressing | IP, ICMP, routers |
| 2 | Data Link | Frame delivery, error detection | Ethernet, MAC, switches |
| 1 | Physical | Bits on wire | Cables, hubs, signals |

**Mnemonic**: "Please Do Not Throw Sausage Pizza Away" (bottom-up)

### Layer Details

**Physical (1)**: Raw bits, voltages, cables, connectors.

**Data Link (2)**:
- Framing (start/end of data)
- MAC addressing
- Error detection (CRC)
- Access control (CSMA/CD)

**Network (3)**:
- Logical addressing (IP)
- Routing between networks
- Packet fragmentation

**Transport (4)**:
- Port numbers
- Segmentation
- Reliability (TCP) or speed (UDP)
- Flow/congestion control

**Session (5)**:
- Establish/maintain/terminate sessions
- Dialog control

**Presentation (6)**:
- Data translation
- Compression
- Encryption/decryption

**Application (7)**:
- User-facing protocols
- Network services

## TCP/IP Model (4 Layers)

| TCP/IP Layer | OSI Equivalent | Function |
|--------------|----------------|----------|
| Application | 5, 6, 7 | Application protocols |
| Transport | 4 | TCP, UDP |
| Internet | 3 | IP routing |
| Network Access | 1, 2 | Physical transmission |

## Data Encapsulation

```
Application Data
      |
      v
Transport [Header | Application Data]     = Segment (TCP) / Datagram (UDP)
      |
      v
Network   [IP Header | Segment]           = Packet
      |
      v
Data Link [Frame Header | Packet | FCS]   = Frame
      |
      v
Physical  [Bits]
```

## IP (Internet Protocol)

### IPv4 Header

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|Version|  IHL  |    DSCP   |ECN|          Total Length         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         Identification        |Flags|      Fragment Offset    |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Time to Live |    Protocol   |         Header Checksum       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Source Address                          |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Destination Address                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

**Key fields**:
- **TTL**: Decrements at each hop, prevents infinite loops
- **Protocol**: Upper layer (6=TCP, 17=UDP, 1=ICMP)
- **Source/Destination**: 32-bit addresses

### IPv4 Addressing

**Address format**: 4 octets (e.g., 192.168.1.1)

**Classes** (historical):
| Class | Range | Default Mask |
|-------|-------|--------------|
| A | 1-126.x.x.x | /8 |
| B | 128-191.x.x.x | /16 |
| C | 192-223.x.x.x | /24 |

**Private addresses** (RFC 1918):
- 10.0.0.0/8
- 172.16.0.0/12
- 192.168.0.0/16

**CIDR notation**: 192.168.1.0/24 (24 bits for network)

### IPv6

**Address**: 128 bits, 8 groups of 4 hex digits.
Example: 2001:0db8:85a3:0000:0000:8a2e:0370:7334

**Benefits**:
- Larger address space (2^128)
- Simplified header
- No NAT needed
- Built-in security (IPsec)

## TCP (Transmission Control Protocol)

### TCP Header

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Sequence Number                        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                    Acknowledgment Number                      |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|  Data |           |U|A|P|R|S|F|                               |
| Offset| Reserved  |R|C|S|S|Y|I|            Window             |
|       |           |G|K|H|T|N|N|                               |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|           Checksum            |         Urgent Pointer        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### TCP Flags

| Flag | Meaning |
|------|---------|
| SYN | Synchronize sequence numbers |
| ACK | Acknowledgment |
| FIN | Finish (close connection) |
| RST | Reset connection |
| PSH | Push data immediately |
| URG | Urgent data |

### Three-Way Handshake

```
Client                    Server
   |                         |
   |-------- SYN ----------->|
   |    seq=x                |
   |                         |
   |<----- SYN-ACK ----------|
   |    seq=y, ack=x+1       |
   |                         |
   |-------- ACK ----------->|
   |    seq=x+1, ack=y+1     |
   |                         |
   |   Connection established |
```

### Connection Termination (Four-Way)

```
Client                    Server
   |                         |
   |-------- FIN ----------->|
   |                         |
   |<------- ACK ------------|
   |                         |
   |<------- FIN ------------|
   |                         |
   |-------- ACK ----------->|
   |                         |
   | Connection closed       |
```

### TCP Reliability

1. **Sequence numbers**: Order segments
2. **Acknowledgments**: Confirm receipt
3. **Retransmission**: On timeout or duplicate ACKs
4. **Checksums**: Detect corruption

### Flow Control (Sliding Window)

**Receive window**: How much data receiver can accept.

```
Sender window:
[Sent & ACKed | Sent, not ACKed | Can send | Cannot send]
                    ^                ^
               Send base        Send base + window
```

### Congestion Control

**Slow start**: Double window each RTT until threshold.

**Congestion avoidance**: Increase window by 1 each RTT.

**Fast retransmit**: Retransmit on 3 duplicate ACKs.

**Fast recovery**: Don't go back to slow start on fast retransmit.

```
Window
  ^
  |        /\
  |       /  \    congestion
  |      /    \   avoidance
  |     /      --------
  |    / slow
  |   /  start
  +------------------------> Time
```

## UDP (User Datagram Protocol)

### UDP Header

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|          Source Port          |       Destination Port        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|            Length             |           Checksum            |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

### TCP vs UDP

| Aspect | TCP | UDP |
|--------|-----|-----|
| Connection | Connection-oriented | Connectionless |
| Reliability | Guaranteed delivery | Best effort |
| Order | In-order delivery | No ordering |
| Speed | Slower (overhead) | Faster |
| Use cases | Web, email, file transfer | DNS, streaming, gaming |

## Interview Questions

1. **Why does TCP need three-way handshake?**
   - Both sides agree on initial sequence numbers
   - Confirms both directions work
   - Prevents old duplicate connections

2. **What happens if packet is lost?**
   - Sender times out, retransmits
   - Or receiver sends duplicate ACKs (fast retransmit)

3. **When would you use UDP over TCP?**
   - Real-time: video, voice, gaming
   - Simple request-response: DNS
   - When app handles reliability
