# Suíte de Aplicativos para Organização e Manipulação de Arquivos

![PyQt6](https://img.shields.io/badge/PyQt6-GUI-blue) ![Python](https://img.shields.io/badge/Python-3.10%2B-green)

Uma suíte completa e moderna para organizar, converter, renomear, redimensionar, analisar e extrair informações de arquivos e imagens, com interface gráfica intuitiva desenvolvida em PyQt6.

## Funcionalidades Principais

- **Organizador de Arquivos**: Organize pastas e arquivos rapidamente.
- **Conversor de Imagens**: Converta imagens em lote entre diversos formatos (PNG, JPG, BMP, GIF, WEBP, etc).
- **Renomeador em Massa**: Renomeie arquivos em lote com regras flexíveis.
- **Redimensionador de Imagens**: Redimensione imagens em lote, mantendo ou não a proporção.
- **Manipulação de PDF**: Divida, mescle, extraia texto e converta imagens para PDF.
- **OCR (Reconhecimento de Texto)**: Extraia texto de imagens e PDFs usando Tesseract OCR.
- **Relatórios Automáticos**: Gere relatórios detalhados sobre o conteúdo de uma pasta, incluindo gráficos e estatísticas.
- **Logs Avançados**: Visualize, filtre e exporte logs de eventos e erros.
- **Barra de Progresso e Cancelamento**: Todas as operações pesadas são executadas em segundo plano (thread), com barra de progresso e opção de cancelar.

## Capturas de Tela

> **Inclua aqui prints das principais telas para atrair usuários!**

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/willianpn01/accessories
   cd seu-repo
   ```
2. **Crie um ambiente virtual (opcional, mas recomendado):**
   ```bash
   python -m venv .venv
   # Ative o ambiente:
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Instale o Tesseract OCR:**
   - Baixe em: https://github.com/tesseract-ocr/tesseract
   - Adicione o executável ao PATH do sistema.

## Como Usar

1. Execute a aplicação:
   ```bash
   python interface_organizador.py
   ```
2. Navegue pelas abas para acessar as funcionalidades.
3. Todas as operações pesadas mostram barra de progresso e podem ser canceladas.
4. Consulte os logs para auditoria ou suporte.

## Estrutura do Projeto

- `interface_organizador.py`: Interface principal e integração das funcionalidades.
- `ocr_utils.py`: Funções para OCR de imagens e PDFs.
- `relatorio_utils.py`: Geração de relatórios e gráficos.
- `log_utils.py`: Sistema de logs.
- `docx_utils.py`: Conversão entre DOCX e PDF.
- `conversor_imagem.py`, `redimensionador.py`, etc: Manipulação de imagens.

## Requisitos
- Python 3.10 ou superior
- PyQt6
- Pillow
- PyPDF2
- pdfplumber
- pytesseract (e Tesseract OCR instalado)
- reportlab
- matplotlib

Veja `requirements.txt` para detalhes.

## Contribuição

Contribuições são bem-vindas! Abra issues ou pull requests para sugerir melhorias, reportar bugs ou adicionar novas funcionalidades.

## Licença

Este projeto está sob a licença MIT.

---

