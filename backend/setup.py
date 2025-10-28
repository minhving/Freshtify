"""
Setup script for the AI Stock Level Estimation API.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ai-stock-estimation-api",
    version="1.0.0",
    author="Team ChillGuys La Trobe University",
    author_email="quocan0106@gmail.com",
    description="AI-powered stock level estimation for supermarkets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/minhving/Freshtify/tree/main",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.0",
        ],
        "gpu": [
            "torch>=2.1.0",
            "torchvision>=0.16.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-stock-api=run:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": ["*.yaml", "*.yml", "*.json"],
    },
)
