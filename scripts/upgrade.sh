#!/bin/bash
# Upgrade all packages in requirements.txt

set -e

REQUIREMENTS_FILE="${1:-requirements.txt}"

if [[ ! -f "$REQUIREMENTS_FILE" ]]; then
    echo "Error: $REQUIREMENTS_FILE not found"
    exit 1
fi

# Check if pip-tools is available, install if needed
if ! command -v pip-compile &> /dev/null; then
    echo "Installing pip-tools..."
    pip install pip-tools
fi

echo "Upgrading packages in $REQUIREMENTS_FILE..."

# Process each package
while IFS= read -r line || [[ -n "$line" ]]; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && continue

    # Extract package name (before ==, >=, ~=, etc.)
    package=$(echo "$line" | sed -E 's/([a-zA-Z0-9_-]+).*/\1/')

    if [[ -n "$package" ]]; then
        echo "Checking $package..."
        # Get latest version from pip
        latest=$(pip index versions "$package" 2>/dev/null | head -1 | sed -E 's/.*\(([^)]+)\).*/\1/' || echo "")

        if [[ -n "$latest" ]]; then
            echo "  -> $package==$latest"
            # Update the line in requirements.txt
            sed -i "s/^${package}==.*/${package}==${latest}/" "$REQUIREMENTS_FILE"
        else
            echo "  -> Could not determine latest version for $package"
        fi
    fi
done < "$REQUIREMENTS_FILE"

echo ""
echo "Done! Updated $REQUIREMENTS_FILE:"
cat "$REQUIREMENTS_FILE"

echo ""
echo "Run 'pip install -r $REQUIREMENTS_FILE' to install the updated packages."
