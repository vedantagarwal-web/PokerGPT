from setuptools import setup, find_packages

setup(
    name="pokergpt",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask==3.0.2",
        "flask-sqlalchemy==3.1.1",
        "flask-login==0.6.3",
        "flask-caching==2.1.0",
        "python-dotenv==1.0.1",
        "numpy==1.26.4",
        "pandas==2.2.1",
        "scikit-learn==1.4.2",
        "torch==2.2.1",
        "transformers==4.38.2",
        "pytest==8.0.2",
        "gunicorn==21.2.0",
        "python-json-logger==2.0.7",
        "requests==2.31.0",
        "tqdm==4.66.2",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="An AI-powered poker learning system",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pokergpt",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
) 