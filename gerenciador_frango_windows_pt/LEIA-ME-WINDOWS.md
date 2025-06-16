# 🐔 GERENCIADOR DE GRANJAS DE FRANGO - VERSÃO WINDOWS

## 🎯 **PROBLEMAS RESOLVIDOS:**

### ✅ **Erro 193 (Win32 inválido) - CORRIGIDO**
- Removido executável compilado no Linux
- Usando Python diretamente para máxima compatibilidade
- Funciona em Windows 10/11, Linux e macOS

### ✅ **Problema do Banco de Dados - CORRIGIDO**
- Inicialização automática do SQLite
- Verificação de conectividade
- Criação automática de tabelas
- Tratamento de erros melhorado

---

## 🚀 **COMO USAR (WINDOWS):**

### **Método 1: Automático (Recomendado)**
1. **Duplo clique** em `INICIAR_APLICACAO.bat`
2. **Aguarde** a instalação automática das dependências
3. **Navegador abre automaticamente** em português

### **Método 2: Manual**
```cmd
python iniciar_aplicacao.py
```

---

## 📋 **REQUISITOS:**

### **Python (Obrigatório)**
- **Download**: https://python.org/downloads/
- **Versão**: 3.7 ou superior
- **⚠️ IMPORTANTE**: Marcar "Add Python to PATH" na instalação

### **Dependências (Instalação Automática)**
- O sistema instala automaticamente: `fastapi`, `uvicorn`, `pydantic`, `reportlab`

---

## 🎯 **FUNCIONALIDADES IMPLEMENTADAS:**

### ✅ **Suas Solicitações:**
1. **📅 Datas de Entrada e Saída**
   - Campos na página inicial
   - Validação automática (30-70 dias)
   - Exibição nos resultados e PDF

2. **🐔 Viabilidade**
   - Cálculo automático de frangos capturados
   - Taxa de viabilidade em percentual
   - Destaque nas métricas principais

3. **🔓 Idade Flexível**
   - Sem restrições de 35-60 dias
   - Entrada livre de qualquer idade

4. **🇧🇷 Interface em Português**
   - 100% traduzida para português brasileiro
   - Relatórios PDF em português
   - Mensagens de erro em português

### 📊 **Sistema Completo:**
- **Cálculo de TCA** (Taxa de Conversão Alimentar)
- **Análise de mortalidade** com insights automáticos
- **Gestão de tratadores** com ranking de performance
- **Gestão de galpões** por localização
- **Relatórios profissionais** em PDF e JSON
- **Banco local SQLite** - funciona sem internet

---

## 💾 **ESTRUTURA DE ARQUIVOS:**

```
gerenciador_frango_windows_pt/
├── INICIAR_APLICACAO.bat        # ← Duplo clique aqui (Windows)
├── iniciar_aplicacao.py         # Lançador principal
├── server.py                    # Backend FastAPI
├── database.py                  # Banco SQLite
├── translations_pt.py           # Traduções
├── frontend/                    # Interface React
├── broiler_data.db             # Banco (criado automaticamente)
└── exports/                    # Relatórios (criado automaticamente)
```

---

## 🔧 **SOLUÇÃO DE PROBLEMAS:**

### **Erro: Python não encontrado**
```cmd
❌ 'python' is not recognized as an internal or external command
```
**Solução**: Instale Python do site python.org e marque "Add to PATH"

### **Erro: Porta em uso**
```
❌ Port 8001 is already in use
```
**Solução**: Feche outras aplicações ou reinicie o computador

### **Banco não conecta**
```
❌ Database connection failed
```
**Solução**: A aplicação agora cria o banco automaticamente. Se persistir, delete `broiler_data.db` e reinicie.

### **Frontend não carrega**
- Certifique-se que as portas 3000 e 8001 estão livres
- Verifique se o Windows Firewall não está bloqueando
- Tente acessar manualmente: http://127.0.0.1:3000

---

## 📱 **COMO USAR A APLICAÇÃO:**

### **1. Criando um Novo Lote:**
1. Clique em "Cálculo de Lote"
2. Preencha **informações básicas**:
   - ID do Lote (único)
   - Número do Galpão  
   - Nome do Tratador
   - **📅 Data de Entrada** (nova!)
   - **📅 Data de Saída** (nova!)

3. Configure **dados dos pintinhos**:
   - Quantidade inicial
   - Custo por pintinho
   - Pintinhos mortos

4. Configure **todas as 4 fases da ração**:
   - Pré-inicial (0-10 dias)
   - Inicial (10-24 dias)
   - Crescimento (24-35 dias)  
   - Final (35+ dias)

5. Adicione **lotes de retirada**:
   - Quantidade removida
   - Peso total
   - **Idade (sem restrições!)** 

6. Clique "**Calcular Custos**"

### **2. Visualizando Resultados:**
- **Métricas principais**: TCA, Mortalidade, **Viabilidade**
- **Resumo de produção**: Com datas e duração
- **Relatório PDF**: Gerado automaticamente em português
- **Insights**: Recomendações automáticas

### **3. Gestão Avançada:**
- **Histórico**: Todos os lotes calculados
- **Performance**: Ranking dos tratadores  
- **Administração**: Gerenciar tratadores e galpões

---

## 💡 **DICAS DE USO:**

### **Para Melhores Resultados:**
- Use IDs únicos para cada lote
- Preencha todas as datas corretamente
- Configure todas as fases da ração
- Adicione múltiplos lotes de retirada se necessário

### **Backup dos Dados:**
- Copie o arquivo `broiler_data.db` regularmente
- Salve a pasta `exports/` com seus relatórios

### **Performance:**
- Primeira inicialização pode demorar mais (instalação de dependências)
- Próximas execuções são muito mais rápidas

---

## 🏆 **VANTAGENS DESTA VERSÃO:**

### ✅ **Compatibilidade Total**
- Funciona em qualquer Windows com Python
- Sem problemas de arquitetura (32/64 bits)
- Instalação automática de dependências

### ✅ **Funcionamento Garantido**
- Banco SQLite com inicialização automática
- Verificações de conectividade
- Tratamento robusto de erros

### ✅ **Interface Profissional**
- 100% em português brasileiro
- Relatórios PDF profissionais
- Validações inteligentes

### ✅ **Dados Seguros**
- Tudo armazenado localmente
- Sem necessidade de internet
- Backup simples (copiar arquivos)

---

## 🎉 **PRONTO PARA USAR!**

Sua aplicação está **100% funcional** e **totalmente em português**. 

**Para começar**: Duplo clique em `INICIAR_APLICACAO.bat`

**Dúvidas?** Todas as funcionalidades estão incluídas e testadas!