from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="codementorai",
    version="0.1.0",
    author="CodeMentorAI Team",
    description="Python 학습을 위한 AI 기반 멘토링 플랫폼",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.11",
    install_requires=[
        "anthropic>=0.40.0",
        "tiktoken>=0.5.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
        "pylint>=3.0.0",
        "pycodestyle>=2.11.0",
        "bandit>=1.7.0",
        "radon>=6.0.0",
        "black>=24.0.0",
        "sqlalchemy>=2.0.0",
        "tenacity>=8.0.0",
        "watchdog>=4.0.0",
        "pygments>=2.16.0",
    ],
    entry_points={
        "console_scripts": [
            "codementorai=main:main",
        ],
    },
)