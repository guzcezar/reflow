# Levantamento de bots Automation Anywhere

## 1. Inventário e plataforma
- Qual versão do Automation Anywhere vocês usam: A360 (cloud ou on-prem), v11 ou 10.x? Há mais de uma convivendo?
- Quantos bots existem no Control Room? 
- Algum bot já foi migrado do v11 para o A360?
- Vocês conseguem exportar os bots (permissão **Export bots**, sem senha e sem packages) ou listar pela API?

## 2. Execução e volume (define attended ou unattended)
- Cada bot roda attended (alguém dispara na máquina) ou unattended (agendado ou por fila, sem usuário)?
- Qual a frequência e a janela de execução de cada bot: diário, horário, sob demanda, 24x7?
- Quanto tempo dura cada execução e qual o volume processado (itens, notas, registros por dia)?
- Quais bots precisam rodar em paralelo ou ao mesmo tempo que outros?
- Usam Workload Management (filas), triggers (e-mail, arquivo) ou só agendamento?
- Qual é o SLA? O que acontece se o bot atrasar ou falhar?

## 3. Licenças e infraestrutura atuais
- Quantas licenças AA vocês têm hoje de cada tipo: Bot Creator, Bot Runner attended, Bot Runner unattended, Control
  Room? Quando vence o contrato?
- Quantas máquinas ou VMs rodam bots? Ficam em VDI, Citrix ou servidor dedicado?
- Os runners usam usuário de serviço dedicado ou o usuário de uma pessoa?
- Quantas licenças estão de fato em uso?

## 4. Aplicações e tipo de interação (define PAD, PARTIAL ou NOT_PAD)
- Com quais sistemas cada bot interage: web, desktop Win32/.NET, SAP GUI, terminal/mainframe, Citrix, Java, Excel
  desktop?
- A interação é por seletores ou por imagem/OCR/coordenadas?
- Algum sistema roda via Citrix ou RDP, ou seja, só como imagem?
- Os bots usam APIs, bancos de dados, SFTP ou e-mail diretamente, sem passar pela UI?
- Há lógica de negócio pesada dentro do bot (regras, cálculos, conciliações), ou ele é basicamente "tela"?

## 5. Dados, credenciais e segurança
- Onde ficam as credenciais: Credential Vault do AA, CyberArk, arquivo? Para onde podem ir no destino (Azure Key Vault,
  conexões do Power Automate)?
- Algum bot trata dados sensíveis (LGPD, financeio)? Há exigência de auditoria ou log?
- Quais entradas e saídas cada bot usa: pastas de rede, planilhas, e-mails, sistemas?

## 6. Ambiente de destino (Power Automate)
- As máquinas que vão rodar o PAD são Windows 10/11 ou Server, ficam on-prem ou em Azure? Podem usar machine groups e
  hosted machines?
- Quem vai orquestrar: cloud flows, agendamento ou triggers? Quais políticas de DLP vigoram no tenant?

## 7. Negócio e priorização
- Quem é o dono de negócio de cada bot e quem mantém o bot hoje (area, sigla, squad)?
- Qual a criticidade de cada bot (alta, média, baixa) e o custo de ficar sem ele (tierlist)?
- Lista de bots que serão desligado?
- Existe documentação ou só o código?
- Qual o prazo, ou seja, quando acaba a licença do AA, e há restrição de janela para cutover?
