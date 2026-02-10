#!/usr/bin/env python3
"""
Automated Asset Discovery & Port Analysis Tool
==============================================
A network reconnaissance tool that resolves hostnames to IP addresses
and performs TCP port scanning using custom socket programming.

Author: Security Assessment Team
Purpose: Identify network entry points during security assessments
"""

import socket
import sys
import argparse
from urllib.parse import urlparse
from typing import Dict, List, Tuple


# Common ports and their associated services
PORT_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    8080: "HTTP-Proxy"
}

# Default ports to scan if none specified
DEFAULT_PORTS = [21, 22, 80, 443]


def parse_arguments() -> argparse.Namespace:
    """
    Parse and validate command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments containing target URL and options
    """
    parser = argparse.ArgumentParser(
        description="Automated Asset Discovery & Port Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scanme.nmap.org
  %(prog)s https://example.com
  %(prog)s 192.168.1.1 -p 22,80,443,8080
  %(prog)s example.com -p 1-1024
  %(prog)s example.com --timeout 2
        """
    )
    
    parser.add_argument(
        'target',
        help='Target URL or hostname (e.g., example.com or https://example.com)'
    )
    
    parser.add_argument(
        '-p', '--ports',
        help='Ports to scan (comma-separated or range, e.g., "22,80,443" or "1-1024")',
        default=None
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=float,
        default=1.0,
        help='Connection timeout in seconds (default: 1.0)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser.parse_args()


def extract_hostname(url: str) -> str:
    """
    Extract hostname from a URL or return the input if it's already a hostname.
    
    Args:
        url: URL or hostname string
        
    Returns:
        str: Extracted hostname
        
    Examples:
        >>> extract_hostname("https://example.com/path")
        'example.com'
        >>> extract_hostname("example.com")
        'example.com'
    """
    # If the URL doesn't have a scheme, add one for proper parsing
    if not url.startswith(('http://', 'https://', '//')):
        url = '//' + url
    
    parsed = urlparse(url)
    hostname = parsed.netloc or parsed.path
    
    # Remove port if present (e.g., example.com:8080 -> example.com)
    if ':' in hostname:
        hostname = hostname.split(':')[0]
    
    return hostname.strip()


def resolve_hostname(hostname: str) -> str:
    """
    Resolve a hostname to its IPv4 address using DNS.
    
    Args:
        hostname: The hostname to resolve
        
    Returns:
        str: Resolved IPv4 address
        
    Raises:
        socket.gaierror: If hostname resolution fails
        ValueError: If no IPv4 address is found
    """
    try:
        # Get address info for the hostname
        # AF_INET ensures we get IPv4 addresses
        addr_info = socket.getaddrinfo(
            hostname,
            None,
            socket.AF_INET,
            socket.SOCK_STREAM
        )
        
        if not addr_info:
            raise ValueError(f"No IPv4 address found for {hostname}")
        
        # Extract the IP address from the first result
        # addr_info returns: [(family, type, proto, canonname, sockaddr)]
        # sockaddr is a tuple: (address, port)
        ip_address = addr_info[0][4][0]
        return ip_address
        
    except socket.gaierror as e:
        raise socket.gaierror(f"Failed to resolve hostname '{hostname}': {e}")


def scan_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """
    Scan a single port using TCP connect scan (Three-Way Handshake).
    
    This function attempts to establish a full TCP connection to determine
    if a port is open. The TCP Three-Way Handshake process:
    1. Client sends SYN
    2. Server responds with SYN-ACK (if port is open)
    3. Client sends ACK to complete the handshake
    
    Args:
        ip: Target IP address
        port: Port number to scan
        timeout: Connection timeout in seconds
        
    Returns:
        bool: True if port is open, False if closed/filtered
    """
    # Create a TCP socket (SOCK_STREAM = TCP, AF_INET = IPv4)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        # Attempt to connect - this initiates the TCP Three-Way Handshake
        # If successful, the port is open
        result = sock.connect_ex((ip, port))
        
        # connect_ex returns 0 on success, error code otherwise
        return result == 0
        
    except socket.timeout:
        # Connection timed out - port is likely filtered
        return False
        
    except socket.error:
        # Other socket errors - treat as closed
        return False
        
    finally:
        # Always close the socket to free resources
        sock.close()


def parse_port_specification(port_spec: str) -> List[int]:
    """
    Parse port specification string into a list of ports.
    
    Supports:
    - Comma-separated: "22,80,443"
    - Ranges: "1-1024"
    - Mixed: "22,80-85,443"
    
    Args:
        port_spec: Port specification string
        
    Returns:
        List[int]: List of unique port numbers
        
    Raises:
        ValueError: If port specification is invalid
    """
    ports = set()
    
    for part in port_spec.split(','):
        part = part.strip()
        
        if '-' in part:
            # Handle range (e.g., "80-85")
            try:
                start, end = part.split('-')
                start, end = int(start), int(end)
                
                if start < 1 or end > 65535 or start > end:
                    raise ValueError(
                        f"Invalid port range: {part}. "
                        "Ports must be between 1-65535 and start <= end"
                    )
                
                ports.update(range(start, end + 1))
                
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Invalid port range format: {part}")
                raise
        else:
            # Handle single port
            try:
                port = int(part)
                if port < 1 or port > 65535:
                    raise ValueError(
                        f"Invalid port number: {port}. "
                        "Ports must be between 1-65535"
                    )
                ports.add(port)
                
            except ValueError:
                raise ValueError(f"Invalid port number: {part}")
    
    return sorted(list(ports))


def scan_ports(ip: str, ports: List[int], timeout: float = 1.0, 
               verbose: bool = False) -> Dict[int, bool]:
    """
    Scan multiple ports on a target IP address.
    
    Args:
        ip: Target IP address
        ports: List of ports to scan
        timeout: Connection timeout in seconds
        verbose: Enable verbose output during scanning
        
    Returns:
        Dict[int, bool]: Dictionary mapping port numbers to their status
                        (True = open, False = closed/filtered)
    """
    results = {}
    
    print(f"\nScanning {len(ports)} ports...")
    print("-" * 50)
    
    for port in ports:
        if verbose:
            print(f"Checking port {port}...", end=' ')
            
        is_open = scan_port(ip, port, timeout)
        results[port] = is_open
        
        if verbose:
            print("OPEN" if is_open else "CLOSED")
    
    return results


def display_results(target: str, ip: str, results: Dict[int, bool]) -> None:
    """
    Display scan results in a formatted table.
    
    Args:
        target: Original target hostname/URL
        ip: Resolved IP address
        results: Dictionary of port scan results
    """
    print("\n" + "=" * 50)
    print(f"Target: {target}")
    print(f"IP Address Resolved: {ip}")
    print("=" * 50)
    
    print("\nScan Results:")
    print("-" * 50)
    
    # Separate open and closed ports
    open_ports = [(port, status) for port, status in results.items() if status]
    closed_ports = [(port, status) for port, status in results.items() if not status]
    
    # Display open ports first
    for port, _ in open_ports:
        service = PORT_SERVICES.get(port, "Unknown")
        print(f"Port {port:<5} | {'OPEN':<8} | ({service})")
    
    # Display closed ports
    for port, _ in closed_ports:
        service = PORT_SERVICES.get(port, "Unknown")
        print(f"Port {port:<5} | {'CLOSED':<8} | ({service})")
    
    print("-" * 50)
    
    # Summary
    total_open = len(open_ports)
    total_closed = len(closed_ports)
    print(f"\nScan Complete.")
    print(f"Summary: {total_open} open, {total_closed} closed/filtered")
    print()


def main():
    """
    Main execution function for the port scanner.
    
    Orchestrates the entire scanning process:
    1. Parse command-line arguments
    2. Extract and resolve hostname
    3. Scan specified ports
    4. Display results
    """
    try:
        # Parse command-line arguments
        args = parse_arguments()
        
        # Extract hostname from URL
        hostname = extract_hostname(args.target)
        
        if not hostname:
            print("Error: Invalid target URL or hostname", file=sys.stderr)
            sys.exit(1)
        
        # Resolve hostname to IP address
        print(f"\n[*] Resolving hostname: {hostname}")
        try:
            ip_address = resolve_hostname(hostname)
            print(f"[+] Resolved to: {ip_address}")
        except socket.gaierror as e:
            print(f"\n[!] Error: {e}", file=sys.stderr)
            print("[!] Please check the hostname and try again.", file=sys.stderr)
            sys.exit(1)
        except ValueError as e:
            print(f"\n[!] Error: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Determine which ports to scan
        if args.ports:
            try:
                ports_to_scan = parse_port_specification(args.ports)
            except ValueError as e:
                print(f"\n[!] Error: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            ports_to_scan = DEFAULT_PORTS
            print(f"[*] Using default ports: {', '.join(map(str, ports_to_scan))}")
        
        # Validate timeout
        if args.timeout <= 0:
            print("\n[!] Error: Timeout must be greater than 0", file=sys.stderr)
            sys.exit(1)
        
        # Perform port scanning
        results = scan_ports(
            ip_address,
            ports_to_scan,
            timeout=args.timeout,
            verbose=args.verbose
        )
        
        # Display results
        display_results(args.target, ip_address, results)
        
    except KeyboardInterrupt:
        print("\n\n[!] Scan interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}", file=sys.stderr)
        if args.verbose if 'args' in locals() else False:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()