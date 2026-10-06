# Riscos e perguntas em aberto

## Riscos técnicos
| ID | Risco | Impacto | Evidência |
|---|---|---|---|
| R-01 | Dependência da estrutura HTML do site: se uma classe CSS mudar (`div.quote`, `span.text`, `small.author`, `a.tag`, `li.next a`), a coleta falha ou volta vazia | alto | `main.py:26`, `main.py:29-32`, `main.py:36` |
| R-02 | `select_one` sem verificação: um bloco de citação sem texto, autor ou link de autor gera erro não tratado e aborta a execução inteira | médio | `main.py:29`, `main.py:30`, `main.py:32` |
| R-03 | O limite de 10 páginas corta a coleta sem aviso se o site tiver mais páginas. O README do projeto diz que o processo "percorre todas as páginas" | médio | `main.py:13`, `main.py:20`, `README.md:3-4` |
| R-04 | Uma falha em qualquer página descarta tudo o que já foi coletado, porque nada é gravado antes do fim | baixo | `main.py:23`, `main.py:52-55` |
| R-05 | O arquivo `quotes.csv` é sobrescrito sem backup nem histórico | baixo | `main.py:45` |
| R-06 | Não há retry em caso de timeout ou erro temporário de rede | baixo | `main.py:22-23` |
| R-07 | O caminho de saída é fixo na pasta do script e não é configurável | baixo | `main.py:12` |
| R-08 | O inventário não registrou a escrita de `quotes.csv` como fonte de dados (`data_sources: []`). Ela foi identificada lendo o código | baixo | `main.py:45-48` |

## Perguntas em aberto (para o dono do processo)
- [ ] Quem consome o `quotes.csv` e para quê?
- [ ] Com que frequência o processo deve rodar? Há agendamento fora do código?
- [ ] O limite de 10 páginas é intencional ou o objetivo é coletar todas as páginas, como diz o README?
- [ ] Um resultado parcial (por exemplo, até a página que falhou) seria aceitável, ou a regra de "tudo ou nada" é obrigatória?
- [ ] Citações duplicadas ou malformadas devem ser tratadas de alguma forma?
- [ ] O arquivo anterior deve ser preservado (histórico, nome com data) ou basta sobrescrever?
- [ ] Onde o arquivo deve ser gravado num ambiente produtivo?

## Inferências feitas nesta documentação
- Não foi identificado um consumidor de negócio para o CSV. Base: o README descreve o projeto como exemplo de prática de scraping (`README.md:3-7`).
- Volumetria de cerca de 100 citações. Base: `quotes.csv` existente com 102 linhas (uma delas é o cabeçalho, e linhas com quebras internas podem alterar a contagem).
- O `quotes.csv` presente no repositório vem de uma execução anterior. Base: o script grava nesse mesmo caminho (`main.py:12`).
- Pré-condição de acesso à internet. Base: requisição HTTP para um site público (`main.py:22`).
- Um elemento ausente gera erro não tratado. Base: chamadas `.get_text` e `["href"]` diretamente sobre o retorno de `select_one`, sem checar `None` (`main.py:29-32`).
- Falhas de escrita do arquivo não são tratadas. Base: não há `try/except` em `save()` (`main.py:44-48`).
