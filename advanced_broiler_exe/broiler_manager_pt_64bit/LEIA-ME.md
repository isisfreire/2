# 🐔 Gerenciador de Granjas de Frango - Versão Offline (64 bits)

## ✅ APLICAÇÃO COMPLETA EM PORTUGUÊS

Esta é uma aplicação profissional e completamente offline para gestão de granjas de frango de corte, com todas as funcionalidades traduzidas para português brasileiro.

## 🚀 Início Rápido

### Linux/Mac
```bash
./iniciar_gerenciador.sh
```

### Windows (WSL/Python instalado)
```batch
iniciar_gerenciador.bat
```

### Manual
```bash
python3 BroilerFarmManager.py
```

## 🎯 Funcionalidades Principais

### ✅ Funcionalidades Solicitadas e Implementadas
1. **📅 Gestão de Datas de Entrada e Saída**
   - Campos de entrada para data de chegada dos pintinhos
   - Data de fechamento do lote
   - Cálculo automático da duração do lote
   - Validação (30-70 dias de duração)

2. **🐔 Cálculo de Viabilidade**
   - Total de frangos capturados com sucesso
   - Taxa de viabilidade em percentual
   - Destaque nas métricas principais

3. **🔓 Flexibilidade de Idade**
   - Removidas completamente as restrições de idade (35-60 dias)
   - Entrada livre de idade para todos os lotes de retirada

4. **📄 Relatórios PDF em Português**
   - Relatórios profissionais com todas as novas informações
   - Datas de entrada e saída incluídas
   - Informações de viabilidade detalhadas
   - Formatação profissional mantida

### 📊 Funcionalidades Completas do Sistema
- **Cálculo de Custos**: Todos os tipos de ração, medicamentos, custos diversos
- **Análise de TCA**: Taxa de Conversão Alimentar com insights automáticos
- **Gestão de Tratadores**: Ranking de desempenho e histórico
- **Gestão de Galpões**: Organização por galpões e localizações
- **Relatórios Detalhados**: PDF e JSON com análises completas
- **Banco de Dados Local**: SQLite offline, sem necessidade de internet

## 🔧 Especificações Técnicas

### Sistema
- **Arquitetura**: 64 bits (corrigido do problema de 32 bits)
- **Backend**: FastAPI com SQLite (37MB executável)
- **Frontend**: React SPA traduzido (100MB)
- **Idioma**: Português brasileiro completo
- **Dados**: Completamente offline e locais

### Requisitos
- **Sistema Operacional**: Linux 64 bits, Windows (via WSL), macOS
- **Python**: 3.7+ (para servidor frontend)
- **Navegador**: Chrome, Firefox, Safari, Edge
- **Espaço**: 200MB livres
- **Internet**: NÃO necessária

## 📁 Estrutura de Arquivos
```
broiler_manager_pt_64bit/
├── BroilerBackend64              # Executável backend (64 bits)
├── BroilerFarmManager.py         # Lançador principal
├── iniciar_gerenciador.sh        # Script Linux/Mac
├── iniciar_gerenciador.bat       # Script Windows
├── frontend/build/               # Aplicação React em português
├── LEIA-ME.md                    # Esta documentação
└── exports/                      # Relatórios gerados (criado automaticamente)
```

## 💾 Gerenciamento de Dados

### Banco de Dados
- **Arquivo**: `broiler_data.db` (SQLite)
- **Localização**: Mesma pasta da aplicação
- **Backup**: Copie o arquivo para fazer backup
- **Migração**: Mova o arquivo para nova instalação

### Relatórios
- **Localização**: Pasta `exports/`
- **Formatos**: PDF (português) e JSON
- **Nomenclatura**: Automática com data/hora

## 🎮 Como Usar

### 1. Criando um Novo Lote
1. Clique em "Cálculo de Lote"
2. Preencha **todas as informações básicas**:
   - ID do Lote (único)
   - Número do Galpão
   - Nome do Tratador
   - **📅 Data de Entrada** (nova funcionalidade)
   - **📅 Data de Saída** (nova funcionalidade)
3. Adicione dados de pintinhos e custos
4. Configure **todas as 4 fases da ração**
5. Adicione **lotes de retirada** (sem restrição de idade)
6. Clique "Calcular Custos"

### 2. Visualizando Resultados
- **Métricas principais**: TCA, Mortalidade, **Viabilidade**
- **Resumo de produção**: Com datas e duração do lote
- **Relatório PDF**: Gerado automaticamente em português
- **Insights**: Análises automáticas em português

### 3. Gestão Avançada
- **Histórico**: Ver todos os lotes calculados
- **Desempenho**: Ranking dos tratadores
- **Administração**: Gerenciar tratadores e galpões

## 🔍 Solução de Problemas

### Problemas Comuns
1. **Porta em uso**: Feche aplicações nas portas 3000 e 8001
2. **Python não encontrado**: Instale do python.org
3. **Permissão negada**: `chmod +x BroilerBackend64`
4. **Navegador não abre**: Vá para http://127.0.0.1:3000

### Verificar Status
- Console mostra status de inicialização
- Backend: http://127.0.0.1:8001/api/
- Frontend: http://127.0.0.1:3000

## 🏆 Diferenciais desta Versão

### ✅ Correções Implementadas
- **64 bits**: Corrigido problema de arquitetura
- **Português completo**: Interface e relatórios traduzidos
- **Datas implementadas**: Entrada, saída e duração
- **Viabilidade**: Cálculo e exibição implementados
- **Sem restrições**: Idade flexível para retirada

### 🎯 Qualidade Profissional
- Interface moderna e intuitiva
- Relatórios PDF profissionais
- Cálculos precisos e validados
- Dados seguros e locais
- Performance otimizada

## 📞 Suporte

Esta aplicação é **100% autocontida**. Todas as funcionalidades estão incluídas:
- Sem necessidade de internet
- Sem serviços externos
- Sem taxas ou assinaturas
- Dados completamente privados

**Sua granja de frangos agora tem uma ferramenta profissional completa em português! 🇧🇷🐔**
