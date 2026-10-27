# ⚡ System Pulse — Monitor de Desempenho do PC

Aplicação Desktop desenvolvida em Python e PyQt6 para monitoramento de hardware e rede em tempo real, acompanhamento e gerenciamento de processos ativos, além de registro histórico com armazenamento local em **SQLite**.

O projeto conta com interface em modo escuro (Dark Theme), atualização dinâmica de métricas, alertas visuais automáticos para alto consumo de recursos e controle otimizado para encerramento de processos do sistema.

---

## 👥 Autor

* **Nicolas Santana de Melo**

---

## 🚀 Funcionalidades Principais

* **📊 Monitoramento de Hardware e Rede em Tempo Real:**
  * Leitura e renderização visual instantânea (atualizada a cada 1 segundo) do uso de **CPU**, **Memória RAM** e **Disco Principal (C:)**.
  * Acompanhamento do tráfego de **Rede (Download e Upload)** formatado dinamicamente em KB/s ou MB/s.
  * **Alertas Visuais Dinâmicos:** As barras de progresso mudam automaticamente para a cor vermelha quando o uso de algum componente ultrapassa **90%**, facilitando a identificação de gargalos.

* **🖥️ Gestão de Processos Ativos:**
  * Lista organizada dos principais processos consumidores do sistema com dados de **PID**, **Nome**, **Uso de CPU (%)** e **Uso de Memória (%)**.
  * **Taxa de Atualização Estabilizada:** A tabela atualiza a cada 5 segundos para garantir que o usuário consiga ler, navegar e selecionar processos com estabilidade e sem oscilações bruscas.
  * **Encerramento de Processos:** Botão dedicado para finalizar o processo selecionado na tabela mediante janela de confirmação de segurança.

* **💾 Histórico Automático e Banco de Dados Local:**
  * Gravação automática das métricas de desempenho no banco de dados **SQLite** a cada 30 segundos em segundo plano, sem interromper a usabilidade da aplicação.

---

## 📂 Estrutura do Projeto

| Arquivo / Pasta | Descrição |
| :--- | :--- |
| `main.py` | Ponto de entrada da aplicação que inicializa a interface e o ciclo de vida do PyQt6. |
| `ui/main_window.py` | Interface gráfica principal (GUI) com abas, tabelas, barras de progresso, alertas visuais e tema Dark. |
| `modules/hardware.py` | Módulo encarregado da coleta de métricas via `psutil` e do encerramento de processos. |
| `modules/database.py` | Módulo de configuração, criação do banco de dados SQLite (`system_pulse.db`) e persistência do histórico. |
| `data/system_pulse.db` | Arquivo do banco de dados SQLite (gerado automaticamente no primeiro arranque). |
| `requirements.txt` | Lista de dependências e bibliotecas Python necessárias para execução do projeto. |

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.x
* **Interface Gráfica (GUI):** PyQt6
* **Monitoramento de Sistema:** `psutil`
* **Banco de Dados:** SQLite 3
* **Empacotamento Executável:** PyInstaller

---

## 📦 Como Executar o Projeto

### 1. Pré-requisitos
Certifique-se de ter o **Python 3.10+** instalado em sua máquina.

### 2. Configuração e Ativação do Ambiente Virtual (venv)
No terminal do Windows (PowerShell):

```powershell
# 1. Criar o ambiente virtual
python -m venv venv

# 2. Ativar o ambiente virtual
.\venv\Scripts\Activate.ps1
```

### 3. Instalação das Dependências
Com o ambiente virtual ativo `(venv)`, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

*(Ou manualmente: `pip install PyQt6 psutil pyinstaller`)*

---

### 4. Executando em Modo de Desenvolvimento

Para rodar a aplicação via código-fonte Python:

```bash
python main.py
```

---

### 5. Gerando o Executável (.EXE)

Para compilar e gerar a versão executável autônoma para Windows (sem necessidade do Python instalado no sistema de destino):

```bash
pyinstaller --noconsole --onedir main.py
```

O aplicativo final compilado e pronto para uso estará disponível dentro do diretório **`dist/main/`**.

---

## 💾 Banco de Dados & Armazenamento

* **`data/system_pulse.db`**: Armazena localmente o histórico do consumo de hardware coletado durante o tempo em que a aplicação permaneceu em execução.