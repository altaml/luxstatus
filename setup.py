from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="microphone-status-monitor",
    version="2.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Automatic availability status based on microphone usage",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/luxstatus",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pystray==0.19.4",
        "pillow>=9.5.0",
        "psutil>=5.9.0",
        "pyusb==1.2.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "flake8>=4.0",
            "pyinstaller>=5.0",
        ],
        "windows": [
            "pywin32>=304",
        ],
        "macos": [
            "pyobjc-core>=9.0",
            "pyobjc-framework-Cocoa>=9.0",
            "py2app>=0.28",
        ],
    },
    entry_points={
        "console_scripts": [
            "mic-monitor=secure_mic_monitor:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)