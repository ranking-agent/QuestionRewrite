"""Setup file for QRW package."""
from setuptools import setup

setup(
    name='Question augmentation',
    version='1.0.0',
    author='Phil Owen',
    author_email='powen@renci.org',
    url='https://github.com/TranslatorIIPrototypes/QuestionRewrite',
    description='Question augmentation - Offers additional relevant questions based initial question asked.',
    packages=['qrw'],
    include_package_data=True,
    zip_safe=False,
    license='MIT',
    python_requires='>=3.8',
)
