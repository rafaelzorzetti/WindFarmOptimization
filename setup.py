
from setuptools import setup, find_packages

setup(
    name='WindFarmOptimization',  # Nome do seu pacote
    version='0.1',  # Versão do pacote
    description='Simulação de Interferência Jensen para otimização de layout de parques eólicos offshore',
    author='Seu Nome',
    author_email='seuemail@exemplo.com',
    url='https://github.com/seu-usuario/WindFarmOptimization',  # URL do repositório no GitHub
    packages=find_packages(),  # Inclui todos os pacotes no diretório
    install_requires=[  # Lista de dependências
        'numpy',
        'matplotlib'
    ],
)
