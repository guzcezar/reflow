# Fluxo do processo

```mermaid
flowchart TD
    A[Início: gatilho] --> B[UC-01 ...]
    B --> C{decisão?}
    C -- sim --> D[UC-02 ...]
    C -- não --> E[Fim]
```

## Narrativa
<Passo a passo ponta a ponta, referenciando os UCs e os arquivos/bots (`arquivo:linha`).>

## Mapa de componentes legados
| Componente (bot/módulo) | Papel | Chamado por |
|---|---|---|
| `Bots/Main` | orquestrador | entrypoint |
