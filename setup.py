import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eufy-security-api-rihan", # Replace with your own username
    version="0.0.7",
    author="Rihan",
    author_email="aleatza@gmail.com",
    description="Cover the http API for eufy security devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Rihan9/eufySecurityApi",
    packages=setuptools.find_packages(),
    install_requires= ['requests', 'click', 'pytz', 'setuptools', 'asyncio'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    license= 'MIT License'
)