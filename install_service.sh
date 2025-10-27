#!/bin/bash
# IntelliVoice Device - Systemd Service Installation Script
# Run this script to install and configure the IntelliVoice service

set -e

echo "IntelliVoice Service Installation"
echo "=================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

SERVICE_FILE="intellivoice.service"
PROJECT_DIR="/home/mrchuck/Projects/intellivoice-device"
SYSTEMD_DIR="/etc/systemd/system"

# Check if service file exists
if [ ! -f "$SERVICE_FILE" ]; then
    echo "Error: $SERVICE_FILE not found in current directory"
    exit 1
fi

# Copy service file
echo "Installing service file..."
cp "$SERVICE_FILE" "$SYSTEMD_DIR/"

# Reload systemd
echo "Reloading systemd..."
systemctl daemon-reload

# Enable service (but don't start it yet - wait for hardware)
echo "Enabling service..."
systemctl enable intellivoice.service

echo ""
echo "Service installation complete!"
echo ""
echo "To start the service:"
echo "  sudo systemctl start intellivoice.service"
echo ""
echo "To check status:"
echo "  sudo systemctl status intellivoice.service"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u intellivoice.service -f"
echo ""
echo "Note: The service will auto-start on boot."
echo "      Start it manually after hardware is connected."

