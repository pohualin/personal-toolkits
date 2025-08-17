from setuptools import setup, find_packages

setup(
    name='automation-scripts',
    version='1.0.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='Collection of Python automation scripts for data processing, GitHub analytics, and reporting',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/automation-scripts',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
        "pandas>=1.3.0",
        "openpyxl>=3.0.0",
        "pytest>=6.0.0",
        "pytube>=12.1.0",
        "youtube-transcript-api>=0.4.1",
        "openAI>=0.27.0"
    ],
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'black>=21.0.0',
            'flake8>=3.9.0'
        ]
    },
    entry_points={
        'console_scripts': [
            'json-to-excel=customer_cleanup.json_to_excel:main',
            'customer-sync=customer_cleanup.customer_sync:main',
            'github-projects=github_analytics.projects_by_query:main',
            'weekly-report=reporting.fetch_weekly_report:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    python_requires='>=3.8',
)