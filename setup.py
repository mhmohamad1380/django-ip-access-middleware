"""
Setup configuration for Django IP Access Control Middleware
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README file
readme_file = Path(__file__).parent / 'README.md'
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ''

setup(
    name='django-ip-access-middleware',
    version='1.0.0',
    description='Django middleware for IP and hostname-based access control',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Mohammad Mohammad Hosseini',
    author_email='dev.mohammadhosseiny@gmail.com',
    url='https://github.com/mhmohamad1380/django-ip-access-middleware',
    packages=find_packages(exclude=['tests', 'test_middleware', 'test_middleware.*', 'example_project', 'example_project.*', '*.tests', '*.tests.*']),
    include_package_data=True,
    install_requires=[
        'Django>=3.2',
    ],
    extras_require={
        'dev': [
            'netifaces>=0.11.0',  # Optional: for better network interface detection
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Framework :: Django :: 5.1',
        'Framework :: Django :: 5.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Security',
    ],
    python_requires='>=3.8',
    keywords='django middleware ip access control hostname kubernetes security',
    zip_safe=False,
)

