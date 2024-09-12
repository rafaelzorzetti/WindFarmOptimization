
# WindFarmOptimization

Este projeto implementa a simulação de interferência Jensen para turbinas eólicas, 
com o objetivo de otimizar o layout de um parque eólico offshore.

## Instalação

Você pode instalar o pacote diretamente do GitHub:

```bash
pip install git+https://github.com/seu-usuario/WindFarmOptimization.git
```

## Uso

Após instalar o pacote, você pode importar e usar a classe `InterferenciaJensen`:

```python
from WindFarmOptimization.interferencia_jensen import InterferenciaJensen

# Exemplo de uso:
interferencia = InterferenciaJensen(k=0.05, power_curve=power_curve, wind_speeds=wind_speeds)
```

O pacote oferece funções para calcular a interferência entre turbinas, a perda de potência e o efeito esteira.
