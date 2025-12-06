# 🚀 PDF Extract Pro - Automação RPA Desktop

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Status](https://img.shields.io/badge/Status-Concluído-success)
![UI](https://img.shields.io/badge/Interface-CustomTkinter-green)

> Uma aplicação Desktop robusta para extração de dados tabulares de PDFs em larga escala, convertendo-os automaticamente para Excel com gestão de falhas e relatórios consolidados.

## 📸 Demonstração
*(Coloque aqui um GIF ou Screenshot da sua interface rodando)*

## 🎯 O Problema
Processar manualmente centenas ou milhares de arquivos PDF para extrair tabelas é uma tarefa repetitiva, lenta e propensa a erros humanos. Scripts simples muitas vezes falham ao encontrar um único arquivo corrompido, interrompendo todo o fluxo de trabalho.

## 💡 A Solução
O **PDF Extract Pro** foi desenvolvido para ser uma ferramenta "à prova de balas". Ele itera sobre uma pasta de input, classifica os arquivos, extrai os dados e gera relatórios, tudo isso envolvido em uma interface gráfica moderna e responsiva que não trava durante o processamento pesado.

### ✨ Funcionalidades Principais

*   **Processamento em Lote (Batch Processing):** Capacidade de processar milhares de arquivos sem interrupção.
*   **Resiliência (Error Handling):** Se um arquivo estiver corrompido ou protegido, o sistema registra o erro, move o arquivo para quarentena e continua o processo.
*   **Classificação Inteligente:**
    *   📄 **Sucesso:** Gera um Excel individual e adiciona ao relatório geral.
    *   🖼️ **Escaneado (Imagem):** Detecta PDFs sem texto selecionável e move para uma pasta específica para análise manual ou OCR futuro.
    *   ⚠️ **Falha:** Isola arquivos corrompidos.
*   **Interface Moderna (GUI):** Desenvolvida com **CustomTkinter**, oferecendo tema Dark/Light, responsividade e feedback visual em tempo real.
*   **Multithreading:** O processamento ocorre em uma thread separada, mantendo a interface fluida e responsiva (sem "Não está respondendo").
*   **Relatório Consolidado:** Além dos arquivos individuais, gera um `Relatorio_Geral_Master.xlsx` unificando todos os dados extraídos.

## 🛠️ Tecnologias Utilizadas

*   **Linguagem:** Python 3.x
*   **Interface Gráfica:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) (Wrapper moderno do Tkinter)
*   **Manipulação de PDF:** `pdfplumber` (Alta precisão na extração de tabelas)
*   **Manipulação de Dados:** `pandas` & `openpyxl`
*   **Concorrência:** `threading` (Biblioteca nativa)

## ⚙️ Instalação e Execução

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/pdf-extract-pro.git
   cd pdf-extract-pro

Crie um ambiente virtual (Opcional, mas recomendado)

code
Bash
download
content_copy
expand_less
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

Instale as dependências

code
Bash
download
content_copy
expand_less
pip install customtkinter pdfplumber pandas openpyxl

Execute a aplicação

code
Bash
download
content_copy
expand_less
python app_pro.py
📂 Estrutura de Saída

O programa organiza automaticamente a pasta de trabalho:

code
Text
download
content_copy
expand_less
Pasta_Selecionada/
├── 01_Convertidos/           # Arquivos .xlsx gerados com sucesso
├── 02_Escaneados_Sem_Texto/  # PDFs que são imagens (precisam de OCR)
├── 03_Falhas_Corrompidos/    # PDFs quebrados ou com senha
└── Relatorio_Geral_Master.xlsx # Todos os dados consolidados
🧠 Lógica de Código (Destaques)
Separação de Responsabilidades (SoC)

O código é dividido em duas classes principais:

PDFProcessor: Lógica pura de backend (extração, pandas, file system). Totalmente desacoplada da interface.

App: Gerenciamento da GUI, eventos e atualização de widgets.

Threading & UX

Para evitar o congelamento da GUI durante o loop de 1000 arquivos, a função executar_lote roda em uma background thread. A comunicação com a GUI (barra de progresso e logs) é feita através de callbacks seguros (after method) para respeitar a Main Loop do Tkinter.

👨‍💻 Gabriel Hipólito da Mata

Desenvolvido por [Seu Nome]
Engenheiro de Software & Especialista em Automação
