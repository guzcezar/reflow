# Whitelist de ações Robin

Os agents `reflow-pad-converter` e `reflow-pad-tester` **só podem usar as ações deste arquivo**. Uma ação que não está aqui vira
`# TODO reflow: ação não mapeada — ...` no flow gerado.

## Como validar uma ação

1. No PAD, monte a ação no designer com parâmetros reais.
2. Selecione a ação e dê **Ctrl+C**. O clipboard recebe o Robin exato.
3. Substitua o snippet abaixo pelo texto copiado (troque valores reais por placeholders).
4. Troque `[não validado]` por `[validado PAD <versão>]`.

Fatos do PAD real:
- Ctrl+C de um subflow inteiro vem embrulhado em `FUNCTION <Nome> GLOBAL` … `END FUNCTION`, mas colar esse texto na
  lista de subflows **não** cria o subflow: crie o subflow à mão e cole só o corpo, sem o `FUNCTION`.
- Caminho literal: `$'''C:\\Robos\\arquivo.txt'''` (barra invertida dobrada).
- Enums vistos: `File.IfFileExists.Overwrite`, `File.FileEncoding.Unicode`, `File.TextFileEncoding.UTF8`.

Aceitos no Ctrl+V (sintaxe ok, execução ainda não testada): `Variables.CreateNewDatatable` com `{ ^['col', ...] }`,
`Variables.AddRowToDataTable.AppendRowToDataTable`, `Text.Replace`, `Text.Trim`, `WebAutomation.LaunchChrome`,
`WebAutomation.GoToWebPage`, `WebAutomation.ExtractData.ExtractTable` com seletor literal, `WebAutomation.CloseWebBrowser`.


Ida e volta completa (colado e copiado de novo do PAD, sem alteração): `output/quote-scraper/04-pad/coletar_citacoes/Main.robin`.
Ali estão validados também: `LOOP ... FROM ... TO ... STEP 1`, `LOOP FOREACH`, `IF ... ELSE ... END`, `StartsWith`,
`File.IfFileExists.Append`, `File.FileEncoding.UTF8`, e aspas duplas dentro de `$'''...'''` escritas como `\"`.

Não existem no PAD (erro "Module or action wasn't found"): `Text.Replace`, `File.WriteCSV`.

Edge sem extensão (WebDriver):
```robin
WebAutomation.LaunchEdge.LaunchEdgeWithDriver Url: cfg_url_portal ClearCookies: False WindowState: WebAutomation.BrowserWindowState.Maximized WaitForPageToLoadTimeout: 60 Timeout: 60 PiPUserDataFolderMode: WebAutomation.PiPUserDataFolderModeEnum.AutomaticProfile TargetDesktop: $'''{\"DisplayName\":\"Local computer\",\"Route\":{\"ServerType\":\"Local\",\"ServerAddress\":\"\"},\"DesktopType\":\"local\"}''' BrowserInstance=> browser
```

> Todos os snippets iniciais foram escritos de memória e estão **`[não validado]`**. Parâmetros e enums podem diferir
> na sua versão do PAD. O primeiro paste de cada um é o teste.

---

## Linguagem

### Variável `[validado PAD]`
```robin
SET contador TO 0
SET mensagem TO $'''Processando %in_cnpj%'''
```

### Comentário `[validado PAD]`
```robin
# Comentário de uma linha
```

### Condição `[parcial: IF ... THEN / END validado; ELSE IF não]`
```robin
IF IsEmpty(in_cnpj) THEN
    SET out_error_message TO $'''CNPJ vazio'''
ELSE IF contador > 3 THEN
    # ...
END
```

### Loop em lista / em DataTable `[não validado]`
```robin
LOOP FOREACH linha IN tabela_notas
    # linha['Coluna']
END
LOOP indice FROM 0 TO tabela_notas.RowsCount - 1 STEP 1
END
```

### Funções em expressões `[parcial: IsEmpty e Contains validados; demais não]`
```robin
IF IsEmpty(in_cnpj) THEN
END
IF IsNotEmpty(out_error_message) THEN
END
IF Contains(conteudo_log, $'''Portal aberto''', False) THEN
END
IF NotContains(conteudo_log, $'''Finalize''', False) THEN
END
IF StartsWith(texto_status, $'''OK''', False) THEN
END
```

### Chamar subflow `[não validado]`
```robin
CALL step_login_portal
```

### Sair do subflow / parar o flow `[não validado]`
```robin
EXIT FUNCTION
EXIT Code: 1 ErrorMessage: $'''Falha no login'''
```

### Esperar (segundos) `[validado PAD]` (aceita decimal: `WAIT 0.5`)
```robin
WAIT 2
```

## Tratamento de erro

### Bloco com tratamento de erro `[parcial: formato abaixo é o do PAD; o corpo do ON BLOCK ERROR não aceita ações livres]`

Forma real (Ctrl+C): nome entre aspas e corpo padrão `THROW ERROR`.
```robin
BLOCK 'nome-do-bloco'
ON BLOCK ERROR
THROW ERROR
END
    # ações
END
```

Snippet antigo (de memória, **não cola**):
```robin
BLOCK processo
ON BLOCK ERROR
    CALL error_handler
END
    CALL init
    CALL step_login_portal
    CALL finalize
END
```

### Retry local em uma ação `[não validado]`
```robin
WebAutomation.Click.Click BrowserInstance: browser Control: appmask['portal']['botao_consultar'] WaitForPageToLoadTimeout: cfg_timeout_segundos
ON ERROR REPEAT 2 TIMES WAIT 2
END
```

### Obter último erro `[não validado]`
```robin
GET LAST ERROR ErrorDetails=> ultimo_erro
```

## Browser (web)

### Abrir Chrome `[não validado]`
```robin
WebAutomation.LaunchChrome.LaunchChrome Url: cfg_url_portal WindowState: WebAutomation.BrowserWindowState.Maximized ClearCache: False ClearCookies: False WaitForPageToLoadTimeout: 60 Timeout: 60 BrowserInstance=> browser
```

### Abrir Edge `[validado PAD: rodou]` (exige a extensão Microsoft Power Automate no Edge)
```robin
WebAutomation.LaunchEdge.LaunchEdge Url: cfg_url_portal WindowState: WebAutomation.BrowserWindowState.Maximized ClearCache: False ClearCookies: False WaitForPageToLoadTimeout: 60 Timeout: 60 BrowserInstance=> browser
```

### Navegar para URL `[validado PAD: rodou]`
```robin
WebAutomation.GoToWebPage.GoToWebPage BrowserInstance: browser Url: cfg_url_portal WaitForPageToLoadTimeout: 60
```

### Preencher campo `[não validado]`
```robin
WebAutomation.PopulateTextField.PopulateTextFieldUsePhysicalKeyboard BrowserInstance: browser Control: appmask['portal']['campo_usuario'] Text: in_usuario Mode: WebAutomation.PopulateTextMode.Replace UnfocusAfterPopulate: False WaitForPageToLoadTimeout: 60
```

### Clicar `[não validado]`
```robin
WebAutomation.Click.Click BrowserInstance: browser Control: appmask['portal']['botao_consultar'] WaitForPageToLoadTimeout: 60
```

### Selecionar opção em dropdown `[não validado]`
```robin
WebAutomation.SelectDropDownListValue.SelectDropDownListValueByName BrowserInstance: browser Control: appmask['portal']['lista_uf'] OptionNames: in_uf WaitForPageToLoadTimeout: 60
```

### Esperar elemento na página `[não validado]`
```robin
WAIT (WebAutomation.WaitForWebPageContent.WebPageToContainElement BrowserInstance: browser Control: appmask['portal']['tabela_notas'])
```

### Ler texto/atributo de elemento `[não validado]`
```robin
WebAutomation.GetDetailsOfElement BrowserInstance: browser Control: appmask['portal']['mensagem'] AttributeName: $'''Own Text''' WaitForPageToLoadTimeout: 60 AttributeValue=> texto_mensagem
```

### Extrair lista/tabela da página `[validado PAD: rodou]`
`Control` aponta para o elemento que **se repete** (uma linha por ocorrência). Cada coluna é
`[seletor relativo ao Control, atributo, regex, nome da coluna]`; o nome da coluna é obrigatório.
**Se o `Control` não existir na página, a ação dá erro ("Data extraction element not found"), não devolve tabela
vazia.** Não use para testar se um elemento existe (ex.: link "Next" na última página). Acesse as colunas por índice
(`linha[0]`), que é a forma que rodou.
```robin
WebAutomation.ExtractData.ExtractTable BrowserInstance: browser Control: $'''html > body > div.container > div.row > div.col-md-8 > div.quote''' ExtractionParameters: {[$'''span.text''', $'''Own Text''', $'''''', $'''text'''], [$'''span > a''', $'''Href''', $'''''', $'''author_url'''] } PostProcessData: False TimeoutInSeconds: 60 ExtractedData=> tabela_pagina
```

### Fechar browser `[validado PAD: rodou]`
```robin
WebAutomation.CloseWebBrowser BrowserInstance: browser
```

## UI desktop

### Executar aplicação `[não validado]`
```robin
System.RunApplication.RunApplication ApplicationPath: cfg_caminho_app WindowStyle: System.ProcessWindowStyle.Maximized ProcessId=> app_process_id
```

### Esperar janela `[não validado]`
```robin
UIAutomation.WaitForWindow.ToOpenByTitleClass Title: cfg_titulo_janela Class: $'''''' FocusWindow: True Timeout: 60
```

### Focar janela `[não validado]`
```robin
UIAutomation.Windows.FocusByTitleClass Title: cfg_titulo_janela Class: $''''''
```

### Clicar em elemento `[não validado]`
```robin
UIAutomation.Click Element: appmask['app']['botao_salvar'] ClickType: UIAutomation.ClickType.LeftClick MousePositionRelativeToElement: UIAutomation.RectangleEdgePoint.MiddleCenter OffsetX: 0 OffsetY: 0
```

### Preencher campo `[não validado]`
```robin
UIAutomation.PopulateTextField Element: appmask['app']['campo_valor'] Text: valor Mode: UIAutomation.PopulateTextMode.Replace ClickType: UIAutomation.PopulateMouseClickType.Default
```

### Ler texto de elemento `[não validado]`
```robin
UIAutomation.GetDetailsOfElement Element: appmask['app']['status'] AttributeName: $'''Own Text''' AttributeValue=> texto_status
```

### Enviar teclas `[não validado]`
```robin
MouseAndKeyboard.SendKeys.FocusAndSendKeys TextToSend: $'''{Enter}''' DelayBetweenKeystrokes: 10 SendTextAsHardwareKeys: False
```

### Fechar janela `[não validado]`
```robin
UIAutomation.Windows.CloseByTitleClass Title: cfg_titulo_janela Class: $''''''
```

## Arquivos, config e log

### Ler arquivo de texto `[validado PAD]`
```robin
File.ReadTextFromFile.ReadText File: cfg_caminho_config Encoding: File.TextFileEncoding.UTF8 Content=> conteudo_config
```

### Converter JSON em objeto (config) `[não validado]`
```robin
Variables.ConvertJsonToCustomObject Json: conteudo_config CustomObject=> config
SET cfg_url_portal TO config['urlPortal']
```

### Escrever linha de log `[parcial: estrutura validada; enums Append e UTF8 não]`
```robin
DateTime.GetCurrentDateTime.Local DateTimeFormat: DateTime.DateTimeFormat.DateAndTime CurrentDateTime=> agora
File.WriteText File: cfg_caminho_log TextToWrite: $'''%agora% | %mensagem%''' AppendNewLine: True IfFileExists: File.IfFileExists.Append Encoding: File.FileEncoding.UTF8
```

### Screenshot `[não validado]`
```robin
Workstation.TakeScreenshot.TakeScreenshotAndSaveToFile File: $'''%cfg_pasta_evidencias%\\erro_%agora%.png''' ImageFormat: Workstation.ImageFormat.Png
```

### Escrever arquivo de texto `[parcial: estrutura validada; enum UTF8 não]`
```robin
File.WriteText File: cfg_caminho_saida TextToWrite: conteudo AppendNewLine: False IfFileExists: File.IfFileExists.Overwrite Encoding: File.FileEncoding.UTF8
```

### Converter objeto/lista em JSON `[não validado]`
```robin
Variables.ConvertCustomObjectToJson CustomObject: citacoes Json=> conteudo_json
```

### Escrever CSV `[validado PAD: rodou]`
`File.WriteCSV` **não existe** no PAD. Grave o cabeçalho com `Overwrite` e uma linha por registro com `Append`:
```robin
File.WriteText File: cfg_caminho_saida TextToWrite: $'''text,author''' AppendNewLine: True IfFileExists: File.IfFileExists.Overwrite Encoding: File.FileEncoding.UTF8
File.WriteText File: cfg_caminho_saida TextToWrite: $'''\"%texto%\",\"%autor%\"''' AppendNewLine: True IfFileExists: File.IfFileExists.Append Encoding: File.FileEncoding.UTF8
```

## Teste

### Executar outro desktop flow `[não validado]`
```robin
External.RunFlow FlowId: '<id-do-flow>' @in_cnpj: in_cnpj @@out_status=> out_status @@out_error_message=> out_error_message
```
