from setuptools import setup, find_packages

setup(
    name="stateful_multi_agent",
    version="0.1.0",
    packages=find_packages(),
    package_data={
        "stateful_multi_agent": [
            "customer_service_agent/prompts/*.yaml",
            "customer_service_agent/sub_agents/*/prompts/*.yaml",
        ]
    },
    python_requires=">=3.8",
    install_requires=[
        "google-adk>=1.14.1",
        "pyyaml>=6.0.1",
    ],
    extras_require={
        "test": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "pytest-asyncio>=0.23.5",
            "pytest-xdist>=3.5.0",
        ],
    },
)