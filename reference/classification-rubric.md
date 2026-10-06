# Rubrica de classificação

Esta rubrica é lida pelo agent `reflow-classifier`. É possível editá-la para recalibrar os critérios sem mexer nos prompts.

## Princípio

**KISS: um sistema é mais simples que dois sistemas e um contrato entre eles.** Se o processo tem UI, ele vai inteiro
para o PAD, inclusive a parte não-UI que cabe em ações nativas (ler e gravar CSV/Excel/texto, montar URLs e variáveis,
SQL simples, e-mail, log). Só se separa (`PARTIAL`) quando a parte não-UI tem **complexidade real**, que ficaria pior no
Robin do que onde está hoje.

## Categorias

| Veredito | Quando | O que acontece |
|---|---|---|
| `PAD` | Há UI, e a parte não-UI (se houver) é simples o bastante para ações nativas do PAD. | Converte o processo inteiro para Robin |
| `PARTIAL` | Há UI **e** uma parte não-UI complexa (ver "Como decidir"). | Converte **só** a parte de UI. O resto fica no sistema atual e o contrato vai para `boundary.md` |
| `NOT_PAD` | Nenhum critério de UI (C1–C5) é atendido. | Só documenta. O pipeline para depois do classify |

## Critérios de UI (qualquer um atendido → há escopo PAD)

| # | Critério | Evidência típica no inventário |
|---|---|---|
| C1 | Automação de UI web (clicar, digitar, navegar em página) | `selenium`, `playwright`, `a360:Browser`, `a360:Recorder` sobre browser, `selenium` em C# |
| C2 | Automação de UI desktop (janelas, controles, apps Win32/.NET/Java) | `pywinauto`, `pyautogui`, `uiautomation`, `a360:Recorder`, `a360:Window`, `flaui`, `win32`, `winforms` (SendKeys) |
| C3 | Raspagem de tela/HTML de sistema **sem API** (portal, tabela HTML, OCR) | `find_elements` + leitura de texto, `BeautifulSoup`/`htmlagilitypack` sobre HTML de portal, `a360:OCR` |
| C4 | Emulador de terminal, SAP GUI, Citrix, reconhecimento de imagem | `a360:TerminalEmulator`, `sapgui`, `a360:ImageRecognition`, `locateOnScreen` |
| C5 | API "não convencional": sessão por cookie/login de tela, endpoints internos de front, download via browser | `requests` com cookie copiado do browser, POST para `.aspx` com `__VIEWSTATE` |

## Critérios de não-UI (avalie o peso, não a presença)

Atender um critério N **não** leva a `PARTIAL`. Ele só identifica a parte não-UI, cujo peso é avaliado em "Como decidir".

| # | Critério | Evidência típica |
|---|---|---|
| N1 | Transformação de dados (pandas, joins, agregações, regras de cálculo) | `pandas`, loops com lógica de negócio densa |
| N2 | API REST/SOAP documentada, com autenticação padrão (token, OAuth, basic) | `requests`/`HttpClient` para `/api/...` com JSON, `a360:RestWebServices` |
| N3 | Banco de dados (leitura/escrita via SQL) | `pyodbc`, `SqlConnection`, `a360:Database` |
| N4 | Arquivos (CSV/Excel/pastas) manipulados sem abrir a UI do Excel | `openpyxl`, `to_excel`, `ClosedXML`/`EPPlus`, `a360:Excel_MS` em modo background |
| N5 | E-mail, notificações, logs | `smtplib`, `a360:Email` |

## Como decidir

1. Avalie C1–C5. Para cada critério atendido, cite as evidências `arquivo:linha`.
2. Nenhum atendido → `NOT_PAD`.
3. Algum atendido → avalie N1–N5. É `PARTIAL` só se a parte não-UI disparar **pelo menos um** destes gatilhos:
   - **G1** regras de negócio ou cálculos densos (muitas condições, conciliações, fórmulas), ou transformação pesada
     de dados (pandas, joins, agregações)
   - **G2** integração que exige código: API com autenticação complexa, SDK, criptografia, protocolo sem ação nativa
     no PAD
   - **G3** volume ou desempenho que o Robin não comporta bem (milhares de linhas processadas em loop, por exemplo)

   **Prova obrigatória:** um `PARTIAL` cita qual gatilho disparou, com evidência `arquivo:linha` que mostre a
   complexidade (não só a existência da parte não-UI). Sem essa prova, o veredito é `PAD`.
4. Se não → `PAD`. Ler e gravar arquivos (CSV, Excel, JSON, texto), escolher formato ou pasta de saída, limpar textos,
   montar URLs, retry, espera e log são **simples** e ficam no flow.
5. Na dúvida entre `PAD` e `PARTIAL`, escolha `PAD`: separar cria um segundo sistema e um contrato para manter.

## Alertas de portabilidade (registrar, não mudam o veredito)

- **A1** DLL ou componente custom chamado pela parte de UI
- **A2** UI dependente de resolução ou coordenadas (clique por posição, imagem)
- **A3** Captcha, MFA ou token físico no login
- **A4** Lógica de negócio misturada dentro dos passos de UI (difícil de separar na fronteira)
- **A5** Credencial hardcoded no código legado
