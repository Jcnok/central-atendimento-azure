# 🏗 Arquitetura de Referência: Agentes Cognitivos Autônomos

## 📋 Sumário Executivo

Este documento detalha a arquitetura técnica da **Central de Atendimento Inteligente**, uma solução enterprise-grade para automação de atendimento ao cliente. A arquitetura utiliza o estado da arte em **IA Generativa**, **Computação em Nuvem** e **Engenharia de Dados** para entregar uma experiência de usuário superior e eficiência operacional.

A solução é construída sobre o ecossistema **Microsoft Azure**, garantindo segurança, conformidade e escalabilidade global.

---

## 🧩 Visão Geral da Arquitetura

A solução adota o padrão **Hierarchical Multi-Agent System (HMAS)**. Diferente de chatbots lineares, este sistema utiliza um "cérebro" central (Router) que delega tarefas complexas para agentes especialistas, cada um equipado com ferramentas e bases de conhecimento específicas.

### Diagrama de Componentes

```mermaid
graph TD
    Client[📱 Client Apps] -->|REST/WSS| Gateway[🛡️ Azure App Service]
    
    subgraph "Orchestration Layer"
        Gateway --> Router[🧠 Router Agent\n(GPT-4o-mini)]
    end
    
    subgraph "Specialized Agents Layer"
        Router --> Tech[🔧 Technical Agent\n(RAG-Enabled)]
        Router --> Sales[📈 Sales Agent\n(Persuasive Logic)]
        Router --> Fin[💰 Financial Agent\n(Transactional)]
    end
    
    subgraph "Cognitive Services"
        Tech <--> Embed[🔠 Azure OpenAI\nEmbeddings]
        Tech <--> VectorDB[(🗄️ Knowledge Base\npgvector)]
        Sales <--> GPT4[🤖 Azure OpenAI\nGPT-4o]
    end
    
    subgraph "Business Systems"
        Sales --> CRM[👥 CRM / ERP]
        Fin --> Billing[💳 Billing System]
        Tech --> ITSM[🎫 Ticketing System]
    end
```

---

## 🤖 Design dos Agentes Especialistas

### 1. Technical Agent (O Engenheiro)
Especialista em diagnóstico e resolução de problemas. Utiliza **RAG (Retrieval-Augmented Generation)** para acessar manuais técnicos e procedimentos em tempo real.

*   **Modelo Cognitivo**: GPT-4o + RAG
*   **Base de Conhecimento**: PostgreSQL com extensão `vector` (pgvector).
*   **Fluxo de RAG**:
    1.  User Query: "Luz PON piscando"
    2.  Embedding: `text-embedding-3-small` gera vetor.
    3.  Busca Vetorial: Consulta por similaridade de cosseno no DB.
    4.  Context Injection: Recupera "Manual de Fibra Ótica" e injeta no prompt.
    5.  Resposta: Instrução precisa baseada no manual.
*   **Ferramentas**:
    *   `get_open_tickets`: Verifica incidentes recorrentes.
    *   `create_ticket`: Abertura de chamados Nível 2.
    *   `check_system_status`: Validação de massivas.

### 2. Sales Agent (O Consultor)
Especialista em negociação, upgrades e retenção. Possui uma persona proativa e persuasiva ("Wolf of Wall Street" style), focada em conversão.

*   **Modelo Cognitivo**: GPT-4o (High Temperature para criatividade controlada).
*   **Lógica de Negócio**:
    *   **Upgrade Agressivo**: Oferta direta com prazos de ativação agressivos (ex: "2 horas para internet").
    *   **Retenção Inteligente**: Análise de sentimento. Se detectar risco de churn, ativa o protocolo de retenção.
    *   **Discount Engine**: Capacidade autônoma de ofertar descontos (ex: 20% off/6 meses) como último recurso.
*   **Ferramentas**:
    *   `upgrade_plan`: Execução imediata de mudança de contrato.
    *   `apply_discount`: Aplicação de regras de retenção.
    *   `calculate_upgrade_cost`: Comparativo financeiro em tempo real.

### 3. Router Agent (O Gerente)
Responsável pela triagem e direcionamento. Utiliza modelos mais leves (GPT-4o-mini) para garantir baixa latência na primeira resposta.

---

## 🧠 Estratégia de Dados e Memória

A solução implementa uma **Memória Híbrida** para garantir contexto e personalização:

1.  **Memória de Curto Prazo (Sessão)**:
    *   Armazenada em **Azure Redis Cache**.
    *   Mantém o contexto da conversa atual (últimas N mensagens).
    *   Garante fluidez no diálogo.

2.  **Memória de Longo Prazo (Semântica)**:
    *   Armazenada em **PostgreSQL (pgvector)**.
    *   Indexa histórico de tickets, manuais e interações passadas.
    *   Permite que o agente "lembre" de problemas recorrentes do cliente.

---

## 🔒 Segurança e Compliance

*   **Data Privacy**: Nenhum dado sensível (PII) é usado para treinamento dos modelos públicos da OpenAI (Azure OpenAI garante isolamento).
*   **Authentication**: Integração via JWT e OAuth2.
*   **Network Security**: Comunicação criptografada (TLS 1.2+) e VNET Integration no Azure.

---

## 📊 Métricas de Sucesso (KPIs)

A eficácia da arquitetura é medida através de:

*   **Taxa de Deflexão**: % de atendimentos resolvidos sem humano. (Meta: >70%)
*   **Precisão do RAG**: Relevância dos documentos recuperados.
*   **Taxa de Conversão**: % de upgrades aceitos pelo Sales Agent.
*   **Churn Prevention**: % de retenções bem-sucedidas após oferta de desconto.

---

<div align="center">
  <sub>Documentação Confidencial - Uso Interno</sub>
</div>
