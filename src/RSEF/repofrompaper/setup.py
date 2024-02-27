from setuptools import setup, find_packages

setup(
    name='rfp',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'transformers==4.38.1',
        'torch==2.2.1',
        'tika==2.6.0',
    ],
    author='Aleksandar Stankovski',
    author_email='a.stankovski@alumnos.upm.es',
    description='Ths package is used to extract the repository link from a pdf file. It uses a model to extract the top sentences from the pdf and then searches for the link in the footnotes, references and sentences.',
    url='https://github.com/SoftwareUnderstanding/RSEF',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers/Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python'
    ],
)
