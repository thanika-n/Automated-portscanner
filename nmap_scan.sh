#!/bin/bash

# ==============================
# Automated Asset & Port Scanner
# Fixed Security Port Baseline
# ==============================

# Important ports list
PORT_LIST="21,22,25,53,80,443,465,993,3000,3306,3389,5432,6379,6443,8080,9092,27017"

# ---- Get target ----
get_target() {
    if [ -z "$1" ]; then
        read -rp "Enter a URL (example.com): " TARGET
    else
        TARGET=$1
    fi

    while [ -z "$TARGET" ]; do
        echo "No URL provided."
        read -rp "Please enter a valid URL: " TARGET
    done
}

# ---- Validate URL ----
validate_url() {
    if ! [[ "$TARGET" =~ ^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        echo "Invalid URL"
        exit 1
    fi
}

# ---- Resolve IPv4 ----
resolve_ip() {
    IP=$(dig +short A "$TARGET" | head -n1)

    if [ -z "$IP" ]; then
        echo "Invalid URL"
        exit 1
    fi
}

# ---- Check host ----
check_host_up() {
    nmap -sn "$IP" > /tmp/hostcheck.txt

    if ! grep -q "Host is up" /tmp/hostcheck.txt; then
        echo "Host is down"
        exit 1
    fi
}

# ---- Scan selected ports ----
scan_ports() {
    echo ""
    echo "Scanning essential security ports..."
    nmap -p $PORT_LIST -T4 "$IP" -oG /tmp/nmap_scan.txt > /dev/null
}

# ---- Map port to service name ----
get_service_name() {
    case $1 in
        21) echo "FTP";;
        22) echo "SSH";;
        25) echo "SMTP";;
        53) echo "DNS";;
        80) echo "HTTP";;
        443) echo "HTTPS";;
        465) echo "SMTPS";;
        993) echo "IMAPS";;
        3000) echo "Node/Grafana";;
        3306) echo "MySQL";;
        3389) echo "RDP";;
        5432) echo "PostgreSQL";;
        6379) echo "Redis";;
        6443) echo "Kubernetes API";;
        8080) echo "HTTP-Alt/Proxy";;
        9092) echo "Kafka";;
        27017) echo "MongoDB";;
        *) echo "Unknown";;
    esac
}

# ---- Parse and display ----
show_results() {

    OPEN_PORTS=()
    CLOSED_PORTS=()

    PORT_LINE=$(grep "Ports:" /tmp/nmap_scan.txt)
    IFS=',' read -ra RESULTS <<< "$(echo "$PORT_LINE" | sed 's/.*Ports: //')"

    for entry in "${RESULTS[@]}"; do
        PORT=$(echo "$entry" | awk -F/ '{print $1}' | xargs)
        STATE=$(echo "$entry" | awk -F/ '{print $2}')
        SERVICE=$(get_service_name $PORT)

        if [ "$STATE" == "open" ]; then
            OPEN_PORTS+=("$PORT | OPEN   | $SERVICE")
        else
            CLOSED_PORTS+=("$PORT | CLOSED | $SERVICE")
        fi
    done

    echo ""
    echo "Target: $TARGET"
    echo "IP Address Resolved: $IP"
    echo ""
    echo "--------------------------------------"
    printf "%-6s | %-6s | %s\n" "PORT" "STATE" "SERVICE"
    echo "--------------------------------------"

    # OPEN FIRST
    for p in "${OPEN_PORTS[@]}"; do
        printf "%-6s\n" "$p"
    done

    # CLOSED SECOND
    for p in "${CLOSED_PORTS[@]}"; do
        printf "%-6s\n" "$p"
    done

    echo "--------------------------------------"
    echo "Scan Complete."
}

# ---- MAIN FLOW ----
get_target "$1"
validate_url
resolve_ip
check_host_up
scan_ports
show_results
