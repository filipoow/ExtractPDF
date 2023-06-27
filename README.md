## Descrição do Código Python

```python
import pandas as pd
import numpy as np
import PyPDF2
import os
import re
```
### Funções
#### extrair_informacoes(texto)<br />
Essa função recebe um texto e extrai informações relevantes desse texto. Ela retorna um dicionário contendo as informações extraídas.

Parâmetros:<br /><br />
**texto (str):** O texto a partir do qual as informações serão extraídas.<br /><br />
Retorno:<br />
- informacoes (dict): Um dicionário contendo as informações extraídas.

#### extrair_informacoes_pdf(caminho_pdf)<br />
Essa função extrai informações de um arquivo PDF. Ela lê o arquivo PDF, extrai o texto de cada página e chama a função extrair_informacoes para extrair as informações relevantes. Retorna um dicionário contendo as informações extraídas.

Parâmetros:

**caminho_pdf (str):** O caminho do arquivo PDF a ser processado.<br /><br />
Retorno:<br />

- informacoes (dict): Um dicionário contendo as informações extraídas do arquivo PDF.<br /><br />
#### determinar_tipo_rota(origem, destino, rota)<br />
Essa função determina o tipo de rota com base nas informações de origem, destino e rota. Retorna uma string indicando o tipo de rota: 'COLETA', 'PRIMARIA' ou 'SECUNDARIA'.<br />

Parâmetros:<br />

**origem (str):** A origem da rota.<br />
**destino (str):** O destino da rota.<br />
**rota (str):** A descrição da rota.<br />
Retorno:<br />

- tipo_rota (str): O tipo de rota determinado.<br />
#### determinar_rota_unificada(tam)
Essa função determina se a rota é unificada com base no tamanho da lista de destinos. Retorna 'SIM' se a lista tiver apenas um elemento e 'NÃO' caso contrário.<br />

Parâmetros:<br />

tam (int): O tamanho da lista de destinos.<br />
Retorno:<br />

- rota_unificada (str): 'SIM' ou 'NÃO', indicando se a rota é unificada.<br />
#### determinar_trecho(origem, destino)
Essa função determina o tipo de trecho com base nas informações de origem e destino. Retorna 'IN' se o trecho for de origem para destino e 'OUT' se o trecho for de destino para origem.<br />

Parâmetros:<br />

**origem (str):** A origem do trecho.<br />
**destino (str):** O destino do trecho.<br />
Retorno:<br />

- trecho (str):** 'IN' ou 'OUT', indicando o tipo de trecho.<br />
#### separar_lista(coluna)
Essa função formata uma lista em uma string separada por barras ('/'). Retorna a string formatada.<br />

Parâmetros:<br />

**coluna (list):** A lista a ser formatada.<br />
Retorno:<br />

- resultado_formatado (str):** A string formatada com os elementos da lista separados por barras.

## Código Principal
O código principal realiza as seguintes etapas:

1. Importa as bibliotecas necessárias: pandas, numpy, PyPDF2, os e re.<br />
2. Define as funções descritas anteriormente.<br />
3. Inicia um DataFrame vazio chamado dados.<br />
4. Obtém a lista de arquivos PDF no diretório atual.<br />
5. Itera sobre cada arquivo PDF:<br />
6. Extrai informações do arquivo PDF usando a função extrair_informacoes_pdf.<br />
7. Adiciona as informações extraídas ao DataFrame dados.<br />
8. Exibe o DataFrame dados na saída.<br />

##### Se você tiver alguma outra pergunta, entre em contato comigo por **emaildofilipe.m@gmail.com.**
