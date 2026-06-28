# CHECKLIST DE VALIDAÇÃO (QA)

Antes do usuário aplicar manualmente o código sugerido pela IA ou executar um `git commit`, os seguintes pontos devem ser validados de forma rigorosa:

## 1. Integridade do Fluxo Central
- [ ] O arquivo alvo das alterações principais foi o `ditado_f8_widget.py`?
- [ ] O fluxo de Segurar F8 > Gravar > Soltar > Whisper > Colar continua funcionando sem congelar a UI?
- [ ] O Python continua responsável por capturar o texto do Whisper e salvar o TXT (sem delegar essa tarefa para o CLI)?

## 2. Validação de Regras do Projeto
- [ ] Os caminhos absolutos atuais (`C:\whispercpp\...`) foram preservados e não foram quebrados por exigências de "caminhos relativos" prematuras?
- [ ] Os arquivos gerados continuam usando estritamente o padrão `YYYYMMDD_HHMMSS.wav` e `YYYYMMDD_HHMMSS.txt`?
- [ ] A IA NÃO assumiu que alguma funcionalidade do Roadmap (ex: `config.json`, toggle mode) já existe?

## 3. Qualidade do Código e UI
- [ ] Foram entregues os arquivos **inteiros**, sem utilizar placeholders maliciosos (como `... restante igual ...`)?
- [ ] O widget permanece sem bordas, arrastável e com os botões originais funcionando?
- [ ] O inicializador silencioso `.vbs` (usando `pythonw.exe`) não foi prejudicado?

## 4. Segurança e GitHub
- [ ] O código não introduziu dependências online? (O sistema é 100% local).
- [ ] Nenhuma pasta proibida (`whisper-bin-x64/`, `gravacoes_ditado/`, etc) foi adicionada nos comandos do `git add` sugeridos pela IA?
- [ ] A instrução de teste local e a sugestão de commit foram fornecidas?
