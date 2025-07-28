from setuptools import setup, find_packages

setup(
    name='cashapp-analyzer-gui',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A GUI application for analyzing Cash App transactions with CSV import functionality.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'pandas',
        'matplotlib',
        'tkinterdnd2',  # For drag-and-drop functionality
        'tkinter',       # Tkinter is included with Python, but can be specified if needed
    ],
    entry_points={
        'console_scripts': [
            'cashapp-analyzer=main:main',  # Adjust according to your main function location
        ],
    },
)