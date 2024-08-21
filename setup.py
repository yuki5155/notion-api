from setuptools import setup, find_packages

setup(
    name="notion-api",
    version="0.0.1",
    author="Yuki Asano",
    author_email="yukiafree@gmail.com",
    description="A short description of your package",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yuki5155/notion-api",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        # リストに依存パッケージを追加
        # 例: 'requests>=2.22.0',
    ],
)
