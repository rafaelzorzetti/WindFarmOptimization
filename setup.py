
from setuptools import setup, find_packages

setup(
    name='WindFarmOptimization',  
    version='0.1',  
    description='Biblioteca Otimização Layout Parque Eólico Offshore',
    author='Rafael Zorzetti Pereira',
    author_email='rafaelzorzetti@usp.br',
    url='https://github.com/rafaelzorzetti/WindFarmOptimization',  
    packages=find_packages(),  
    install_requires=[
        'numpy',
        'matplotlib'
    ],
)
