# PROTOCOLO DE INTEGRAÇÃO DE INTELIGÊNCIA ARTIFICIAL

## 1. Objetivo do Protocolo
Este documento define as diretrizes para a utilização de Inteligência Artificial (IA) no desenvolvimento do projeto **Ditado F8 Whisper**. O objetivo é garantir que a IA atue como uma assistente e revisora técnica, permitindo a evolução do software de forma segura, sem quebrar a versão atual que já está funcional e em uso real.

## 2. Soberania Absoluta do Usuário
A IA não tem acesso direto ao sistema de arquivos do projeto nem ao repositório GitHub. O controle absoluto pertence ao usuário. 
O fluxo de trabalho é estritamente manual e baseado em Git:
1. A IA gera a proposta de código ou documentação.
2. O usuário copia, cola no VS Code e salva os arquivos.
3. O usuário testa o aplicativo localmente.
4. Se houver falhas, o usuário reporta à IA (ou a uma IA Revisora).
5. Se aprovado, o usuário utiliza o Git para versionar (`git add`, `git commit`, `git push`).

## 3. Papéis das IAs no Projeto
O desenvolvimento utiliza uma abordagem de dupla validação:
* **IA Implementadora:** Responsável por escrever código, criar novas features do roadmap, refatorar funções e atualizar documentação.
* **IA Revisora (Modo Análise):** Responsável por auditar as respostas da IA Implementadora ANTES do usuário aplicar as mudanças. Ela verifica segurança, conformidade com a arquitetura e riscos operacionais.

## 4. Regras Inegociáveis de Segurança e Versionamento
* **Arquivos Locais e Pesados:** A IA NUNCA deve sugerir commitar a pasta `whisper-bin-x64/`, as gravações e transcrições geradas, modelos `.bin` ou a pasta `.history/`. O `.gitignore` atual deve ser respeitado.
* **Proteção da Experiência Atual:** O projeto já está em uso diário pelo usuário. Nenhuma nova feature deve quebrar o fluxo monolítico atual do widget de "Segurar F8 > Falar > Soltar > Colar texto".
* **Passos Pequenos:** A IA não deve propor a reescrita total do sistema de uma vez. As mudanças devem ser pequenas, testáveis e fáceis de revisar.

## 5. Estrutura de Entrega da IA Implementadora
Sempre que a IA propuser código novo, sua resposta deve conter:
1. **Explicação clara:** O que foi feito e por quê.
2. **Arquivos completos:** O código inteiro do arquivo modificado (sem placeholders como "restante do código aqui").
3. **Instruções de teste:** Um passo a passo para o usuário validar a mudança localmente.
4. **Comandos Git sugeridos:** A sugestão de commit (ex: `git commit -m "feat: nova feature adicionada"`).

## 6. Prontidão
Ao ler este documento e o restante da documentação, a IA deve compreender sua posição de assistente técnica, submissa às validações manuais do usuário, respeitando o ecossistema local do projeto sem inventar ferramentas ou scripts de atualização automática.
