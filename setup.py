from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="sofizpay-sdk",
    version = "1.0.2",
    author="SofizPay Team",
    author_email="support@sofizpay.com",
    description="Professional Python SDK for SofizPay payments using Stellar blockchain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kenandarabeh/sofizpay-sdk-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="stellar, payment, blockchain, cryptocurrency, DZT, sofizpay, fintech, stellar-network",
    project_urls={
        "Bug Reports": "https://github.com/kenandarabeh/sofizpay-sdk-python/issues",
        "Source": "https://github.com/kenandarabeh/sofizpay-sdk-python",
        "Documentation": "https://github.com/kenandarabeh/sofizpay-sdk-python#readme",
        "Homepage": "https://sofizpay.com",
    },
    include_package_data=True,
    zip_safe=False,
)
