#!/bin/bash

# BAYMAX Installation Script
# This script automates the installation of BAYMAX and its dependencies

set -e  # Exit on any error

echo "🤖 BAYMAX Healthcare Assistant - Installation Script"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "This script should not be run as root. Please run as a regular user."
        exit 1
    fi
}

# Check Python version
check_python() {
    print_status "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
        
        # Check if version is 3.7 or higher
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)"; then
            print_success "Python version is compatible"
        else
            print_error "Python 3.7 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_status "Installing system dependencies..."
    
    # Detect package manager
    if command -v apt-get &> /dev/null; then
        PACKAGE_MANAGER="apt-get"
        UPDATE_CMD="sudo apt-get update"
        INSTALL_CMD="sudo apt-get install -y"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
        UPDATE_CMD="sudo yum update -y"
        INSTALL_CMD="sudo yum install -y"
    elif command -v dnf &> /dev/null; then
        PACKAGE_MANAGER="dnf"
        UPDATE_CMD="sudo dnf update -y"
        INSTALL_CMD="sudo dnf install -y"
    else
        print_error "Unsupported package manager. Please install dependencies manually."
        exit 1
    fi
    
    print_status "Using package manager: $PACKAGE_MANAGER"
    
    # Update package list
    print_status "Updating package list..."
    eval $UPDATE_CMD
    
    # Install system dependencies
    print_status "Installing system packages..."
    
    # Common dependencies
    eval $INSTALL_CMD cmake
    eval $INSTALL_CMD build-essential
    eval $INSTALL_CMD pkg-config
    
    # OpenCV dependencies
    eval $INSTALL_CMD libopencv-dev
    eval $INSTALL_CMD python3-opencv
    
    # Face recognition dependencies
    eval $INSTALL_CMD libopenblas-dev
    eval $INSTALL_CMD liblapack-dev
    eval $INSTALL_CMD libx11-dev
    eval $INSTALL_CMD libgtk-3-dev
    eval $INSTALL_CMD libboost-python-dev
    
    # Audio dependencies
    eval $INSTALL_CMD portaudio19-dev
    eval $INSTALL_CMD python3-pyaudio
    
    # Text-to-speech dependencies
    eval $INSTALL_CMD espeak
    
    print_success "System dependencies installed"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        print_status "Installing pip3..."
        sudo apt-get install -y python3-pip
    fi
    
    # Upgrade pip
    print_status "Upgrading pip..."
    python3 -m pip install --upgrade pip
    
    # Install Python packages
    print_status "Installing Python packages..."
    
    # Install packages one by one to handle errors better
    packages=(
        "opencv-python==4.8.1.78"
        "numpy==1.24.3"
        "pandas==2.0.3"
        "pillow==10.0.1"
        "schedule==1.2.0"
        "pygame==2.5.2"
        "matplotlib==3.7.2"
        "scikit-learn==1.3.0"
    )
    
    for package in "${packages[@]}"; do
        print_status "Installing $package..."
        pip3 install $package
    done
    
    # Install face recognition (may take longer)
    print_status "Installing face recognition (this may take a while)..."
    pip3 install dlib
    pip3 install face-recognition==1.3.0
    
    # Install text-to-speech
    print_status "Installing text-to-speech..."
    pip3 install pyttsx3==2.90
    
    # Install speech recognition
    print_status "Installing speech recognition..."
    pip3 install speechrecognition==3.10.0
    
    print_success "Python dependencies installed"
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    
    if python3 test_baymax.py; then
        print_success "All tests passed! BAYMAX is ready to use."
    else
        print_warning "Some tests failed. Please check the output above."
        print_status "You can still try running BAYMAX with: python3 baymax_main.py"
    fi
}

# Create desktop shortcut
create_desktop_shortcut() {
    print_status "Creating desktop shortcut..."
    
    DESKTOP_FILE="$HOME/Desktop/BAYMAX.desktop"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BAYMAX Healthcare Assistant
Comment=Smart healthcare assistant inspired by Big Hero 6
Exec=python3 $(pwd)/baymax_main.py
Icon=applications-science
Terminal=true
Categories=Science;Medical;Utility;
EOF
    
    chmod +x "$DESKTOP_FILE"
    print_success "Desktop shortcut created"
}

# Main installation function
main() {
    echo "Starting BAYMAX installation..."
    echo
    
    # Run installation steps
    check_root
    check_python
    install_system_deps
    install_python_deps
    test_installation
    create_desktop_shortcut
    
    echo
    echo "🎉 BAYMAX installation completed!"
    echo
    echo "Next steps:"
    echo "1. Run BAYMAX: python3 baymax_main.py"
    echo "2. Or double-click the desktop shortcut"
    echo "3. Follow the on-screen instructions to register users"
    echo
    echo "For help, see the README.md file or run: python3 test_baymax.py"
    echo
    echo "Thank you for choosing BAYMAX! 🤖💙"
}

# Run main function
main "$@"