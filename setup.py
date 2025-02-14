from setuptools import setup, find_packages

# Read dependencies from requirements.txt
with open("requirements.txt", "r") as req_file:
    requirements = [line.strip() for line in req_file if line.strip()
                    and not line.startswith("#")]

setup(
    name='zk-rag',
    version='1.0.0',
    packages=find_packages(),  # replaced py_modules with packages=find_packages()
    install_requires=requirements,  # added to install modules from requirements.txt
    entry_points={
        'console_scripts': [
            'zk_reindex=zk_chat.reindex:main',  # updated entry point for root modules
            'zk_chat=zk_chat.chat:main'         # updated entry point for root modules
        ]
    },
)
