#!/bin/bash

clear
cat << "EOF"
  _______ _                 _ _         _       _____           _      _____                                 
 |__   __| |               (_) |       ( )     |  __ \         | |    / ____|                                
    | |  | |__   __ _ _ __  _| | ____ _|/ ___  | |__) |__  _ __| |_  | (___   ___ __ _ _ __  _ __   ___ _ __ 
    | |  | '_ \ / _` | '_ \| | |/ / _` | / __| |  ___/ _ \| '__| __|  \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
    | |  | | | | (_| | | | | |   < (_| | \__ \ | |  | (_) | |  | |_   ____) | (_| (_| | | | | | | |  __/ |   
    |_|  |_| |_|\__,_|_| |_|_|_|\_\__,_| |___/ |_|   \___/|_|   \__| |_____/ \___\__,_|_| |_|_| |_|\___|_|   
                                                                                                             
                                                                                                             
EOF

TARGET="$1"
[ -z "$TARGET" ] && echo "Usage: scan <host>" && exit 1

CORE_PORTS=(80 443)
OTHER_PORTS=(
  8080 8443
  21 22 25 53 110 143 465 587 993 995
  3306 5432 1433 27017
  3389 445 8000 8888 3000
)

ALL_PORTS=("${CORE_PORTS[@]}" "${OTHER_PORTS[@]}")
TOTAL_PORTS=${#ALL_PORTS[@]}

echo "Target: $TARGET"
echo
echo "Choose scan output:"
echo "1) Open ports only"
echo "2) Closed ports only"
echo "3) Open and closed ports"
read -p "Enter choice (1/2/3): " CHOICE
echo

TMP_FILE=$(mktemp)
PROGRESS_FILE=$(mktemp)

MAX_JOBS=25
PER_PORT_TIMEOUT=2
GLOBAL_TIMEOUT=120

START_TIME=$(date +%s)
END_TIME=$((START_TIME + GLOBAL_TIMEOUT))

running=0

# -------------------------------
# Progress bar
# -------------------------------
progress_monitor() {
  while true; do
    completed=$(wc -l < "$PROGRESS_FILE")
    printf "\r[%-20s] %d/%d" \
      "$(printf '%*s' "$((completed * 20 / TOTAL_PORTS))" | tr ' ' '#')" \
      "$completed" "$TOTAL_PORTS"

    [ "$completed" -ge "$TOTAL_PORTS" ] && break
    [ "$(date +%s)" -ge "$END_TIME" ] && break
    sleep 0.2
  done
}

progress_monitor &
PROGRESS_PID=$!

# -------------------------------
# Scan with global deadline
# -------------------------------
for port in "${ALL_PORTS[@]}"; do
  # Stop launching new scans if time is up
  [ "$(date +%s)" -ge "$END_TIME" ] && break

  {
    if timeout "$PER_PORT_TIMEOUT" bash -c "echo > /dev/tcp/$TARGET/$port" 2>/dev/null; then
      echo "OPEN:$port" >> "$TMP_FILE"
    else
      echo "CLOSED:$port" >> "$TMP_FILE"
    fi
    echo 1 >> "$PROGRESS_FILE"
  } &

  ((running++))
  if (( running >= MAX_JOBS )); then
    wait
    running=0
  fi
done

# Wait until global timeout expires
while [ "$(date +%s)" -lt "$END_TIME" ] && \
      [ "$(wc -l < "$PROGRESS_FILE")" -lt "$TOTAL_PORTS" ]; do
  sleep 0.2
done

kill "$PROGRESS_PID" 2>/dev/null
echo

# -------------------------------
# Mark unscanned ports as CLOSED
# -------------------------------
scanned_ports=$(cut -d: -f2 "$TMP_FILE" | sort -n)

for port in "${ALL_PORTS[@]}"; do
  if ! grep -qx "$port" <<< "$scanned_ports"; then
    echo "CLOSED:$port" >> "$TMP_FILE"
  fi
done

# -------------------------------
# Output
# -------------------------------
OPEN_PORTS=()
CLOSED_PORTS=()

while IFS=: read status port; do
  [[ $status == OPEN ]] && OPEN_PORTS+=("$port") || CLOSED_PORTS+=("$port")
done < "$TMP_FILE"

rm -f "$TMP_FILE" "$PROGRESS_FILE"

case "$CHOICE" in
  1) printf "Port %s is OPEN\n" "${OPEN_PORTS[@]}" ;;
  2) printf "Port %s is CLOSED\n" "${CLOSED_PORTS[@]}" ;;
  3)
    printf "Port %s is OPEN\n" "${OPEN_PORTS[@]}"
    echo
    printf "Port %s is CLOSED\n" "${CLOSED_PORTS[@]}"
    ;;
esac

echo
echo "Scan completed (max time: 2 minutes)."
