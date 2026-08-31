"""Setup configuration for PDFusion."""
from setuptools import setup, find_packages

setup(
    name="pdfusion",
    version="1.0.0",
    description="Professional all-in-one offline PDF utility",
    author="PDFusion",
    python_requires=">=3.13",
    packages=find_packages(),
    install_requires=[
        "PySide6>=6.6.0",
        "PyMuPDF>=1.23.0",
        "pikepdf>=8.0.0",
        "pypdf>=3.17.0",
        "reportlab>=4.0.0",
        "Pillow>=10.0.0",
        "opencv-python-headless>=4.8.0",
        "pdf2image>=1.16.0",
        "python-docx>=1.0.0",
        "pytesseract>=0.3.10",
        "natsort>=8.4.0",
    ],
    entry_points={
        "console_scripts": [
            "pdfusion=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3.13",
        "Topic :: Office/Business",
    ],
)
