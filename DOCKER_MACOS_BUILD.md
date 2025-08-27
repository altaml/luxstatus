# 🐳 Docker macOS Build Guide

## ⚖️ Legal Considerations **FIRST**

### **Apple's Software License Agreement**
- macOS can **only legally run on Apple hardware**
- Running macOS on non-Apple hardware **violates Apple's SLA**
- This includes Docker containers on non-Apple systems

### **Legal Use Cases** ✅
- **Apple Silicon Macs** (M1/M2/M3)
- **Intel Macs** (with virtualization enabled)
- **Apple Mac Studio/Pro** in data centers
- **GitHub Actions** (uses Apple-provided macOS runners)

### **Illegal Use Cases** ❌
- Windows PCs
- Linux servers (non-Apple)
- AMD/Intel non-Apple hardware
- Most cloud providers (except Apple-licensed ones)

## 🔧 Technical Implementation

### **Option 1: Legal Docker on Apple Hardware**

If you have an Apple Mac, you can use Docker to build macOS apps:

```bash
# Run the unified deployment
python deploy_unified.py

# Use Docker build (only on Apple hardware)
./docker-build.sh
```

### **Option 2: Docker with sickcodes/docker-osx**

```dockerfile
# Only use this on Apple hardware!
FROM sickcodes/docker-osx:monterey

# Install development tools
RUN /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
RUN brew install python@3.9 git

# Install Python packages
COPY requirements.txt .
RUN pip3 install -r requirements.txt
RUN pip3 install py2app pyobjc

# Build the app
COPY . /app
WORKDIR /app
RUN python3 deploy_macos.py
```

### **Option 3: Alternative macOS Containers**

```bash
# OSX-KVM based (also requires Apple hardware)
docker run --privileged \
  -v /dev:/dev \
  -v $(pwd):/workspace \
  sickcodes/docker-osx:monterey

# Inside the container:
cd /workspace
python3 deploy_macos.py
```

## 📋 Requirements for Docker macOS Build

### **Hardware Requirements**
- Apple hardware (Mac, Mac Mini, Mac Studio, etc.)
- At least 8GB RAM (16GB recommended)
- 100GB+ free disk space
- Hardware virtualization enabled

### **Software Requirements**
```bash
# Install Docker Desktop for Mac
brew install --cask docker

# Install Docker Compose
brew install docker-compose

# Enable experimental features
echo '{"experimental": true}' > ~/.docker/config.json
```

### **Performance Considerations**
- **Very slow**: macOS in Docker is 5-10x slower than native
- **Large containers**: 10GB+ download for macOS base image
- **Memory intensive**: Requires significant RAM allocation
- **Build time**: 30-60 minutes for full build

## 🚀 Practical Usage

### **For Individual Developers**

If you have a Mac:
```bash
# Clone the project
git clone https://github.com/yourusername/luxstatus.git
cd luxstatus

# Run unified deployment (creates Docker files)
python deploy_unified.py

# Use Docker for consistent builds
./docker-build.sh
```

### **For Teams with Mixed Hardware**

**Best approach**: Don't use Docker for macOS builds. Instead:

1. **Native builds** on each platform
2. **GitHub Actions** for automated builds
3. **Shared build server** (Apple Mac Mini/Studio)

### **Docker Compose Setup**

```yaml
# docker-compose.yml
version: '3.8'
services:
  macos-build:
    build:
      dockerfile: Dockerfile.macos
    volumes:
      - ./dist:/output
    # Only enable on Apple hardware
    profiles:
      - apple-hardware-only
```

Run only on Apple hardware:
```bash
docker-compose --profile apple-hardware-only up macos-build
```

## ⚡ Performance Optimization

### **Speed Up Docker macOS Builds**

1. **Use cached base images**:
```dockerfile
FROM sickcodes/docker-osx:monterey
# Pin to specific version to enable caching
```

2. **Multi-stage builds**:
```dockerfile
# Build stage
FROM sickcodes/docker-osx:monterey as builder
RUN brew install python@3.9
COPY . /app
RUN python3 deploy_macos.py

# Extract stage
FROM scratch as export
COPY --from=builder /app/dist /dist
```

3. **Persistent volumes**:
```bash
# Cache Homebrew and pip downloads
docker volume create macos-brew-cache
docker volume create macos-pip-cache
```

## 🔄 Alternatives to Docker macOS

### **Recommended Approaches**

1. **GitHub Actions** (Free, legal, fast):
```yaml
jobs:
  build-macos:
    runs-on: macos-latest  # Apple-provided runners
    steps:
      - uses: actions/checkout@v3
      - run: python3 deploy_macos.py
```

2. **Cloud macOS Services**:
   - **MacStadium** - Dedicated Mac hosting
   - **AWS EC2 Mac** - Apple-licensed cloud Macs
   - **Anka Build** - macOS virtualization for CI/CD

3. **Local Mac Setup**:
   - Mac Mini for CI/CD
   - Developer's personal Mac
   - Shared team Mac

### **Why These Are Better Than Docker**

| Approach | Speed | Legal | Cost | Maintenance |
|----------|-------|-------|------|-------------|
| Docker macOS | ⭐ | ⚠️ | 💰💰 | 🔧🔧🔧 |
| GitHub Actions | ⭐⭐⭐ | ✅ | Free | ⭐ |
| Cloud Mac | ⭐⭐⭐ | ✅ | 💰💰💰 | ⭐⭐ |
| Local Mac | ⭐⭐⭐⭐ | ✅ | 💰 | ⭐⭐ |

## 🎯 Recommendation

### **For Your Windows Computer**

**Don't use Docker for macOS builds**. Instead:

1. **Immediate solution**: Use GitHub Actions
   ```bash
   python deploy_unified.py  # Sets up GitHub Actions
   git tag v1.0.0
   git push origin v1.0.0   # Triggers automated builds
   ```

2. **Long-term solution**: Get a Mac Mini ($599) for development
   - Much faster than Docker macOS
   - Legal and reliable
   - Can also build iOS apps in the future

3. **Professional solution**: Use MacStadium or AWS EC2 Mac
   - Pay-per-use
   - Fully managed
   - Enterprise-grade

### **Bottom Line**

While Docker macOS containers exist, they're:
- **Legally risky** on non-Apple hardware
- **Technically challenging** to set up
- **Performance poor** compared to alternatives
- **Not recommended** for production use

**Use GitHub Actions instead** - it's free, fast, legal, and maintained by professionals! 🚀
