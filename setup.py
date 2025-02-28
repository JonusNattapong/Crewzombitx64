from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zombitx64",
    version="1.0.0",
    author="zombitx64",
    author_email="",  # Add your email here
    description="A powerful web scraping and content analysis tool with AI integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/zombitx64",  # Replace with your repository URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beautifulsoup4>=4.9.3",
        "requests>=2.25.1",
        "python-dotenv>=0.19.0",
        "mistralai>=0.0.1",
        "flask>=2.0.1",
    ],
    entry_points={
        "console_scripts": [
            "zombitx64-normal=zombitx64.normal:main",
            "zombitx64-api=zombitx64.api:main",
            "zombitx64-web=zombitx64.app:main",
        ],
    },
)