# 🍇 Açaízon — Sistema de Pedidos com Reconhecimento Facial

O **Açaízon** é um projeto educacional desenvolvido em equipe com o objetivo de unir **automação, reconhecimento/detecção facial, gerenciamento de pedidos e banco de dados** em uma aplicação desktop.

O sistema permite que o cliente realize seu cadastro, registre uma imagem facial por meio da webcam e utilize o fluxo de Face ID para facilitar o acesso ao sistema. Além disso, possui cardápio, carrinho, finalização de pedidos, histórico de informações e um **Root Master**, responsável pelo gerenciamento administrativo dos clientes e pedidos.

O projeto foi desenvolvido em **Python**, com interface gráfica desktop, banco de dados local **SQLite3**, processamento de imagens com **OpenCV** e exportação de dados em **JSON**.

> **Projeto educacional:** o sistema foi desenvolvido para fins de aprendizado e demonstração. O mecanismo atual de câmera utiliza detecção facial com OpenCV/Haar Cascade e o fluxo de validação facial do protótipo não deve ser tratado como uma solução biométrica de produção.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3** — Linguagem principal do projeto
- **Tkinter** — Interface gráfica e componentes da aplicação
- **CustomTkinter** — Componentes visuais utilizados pela interface
- **SQLite3** — Banco de dados local
- **OpenCV** — Acesso à webcam e detecção facial
- **NumPy** — Suporte ao processamento utilizado pelo OpenCV
- **Pillow (PIL)** — Manipulação e exibição de imagens
- **JSON** — Exportação de dados de clientes, pedidos e comprovantes
- **OS / Sys / Datetime** — Recursos nativos utilizados pelo sistema

As bibliotecas padrão `sqlite3`, `json`, `os`, `sys`, `datetime` e `tkinter` não precisam ser instaladas separadamente pelo `pip`.

---

## 🚀 Funcionalidades do Sistema

### 👤 Cadastro de Cliente

- Cadastro de cliente com dados pessoais.
- Validação de CPF para evitar duplicidade.
- Armazenamento dos dados no banco SQLite.
- Registro de pontos de fidelidade.
- Armazenamento do caminho da imagem facial cadastrada.
- Captura da imagem pela webcam durante o cadastro.

### 📷 Câmera e Face ID

- Abertura da webcam para captura da face.
- Detecção de rosto utilizando **OpenCV + Haar Cascade**.
- Exibição de um retângulo sobre o rosto detectado.
- Salvamento da imagem facial na pasta `assets/faces`.
- Fluxo de acesso por Face ID integrado ao login do cliente.

### 🍇 Cardápio e Carrinho

- Visualização do cardápio.
- Seleção de tamanho do açaí.
- Adição de acompanhamentos/toppings.
- Adição de produtos ao carrinho.
- Visualização e atualização do carrinho.
- Cálculo de subtotal, taxa de entrega e total.
- Aplicação de desconto conforme as regras implementadas no sistema.

### 🔁 "Peça o de Sempre"

Após o acesso de um cliente que possui pedido anterior registrado, o sistema pode recuperar o último pedido e apresentar a opção de repetir a combinação anterior.

### 🧾 Pedidos e Comprovantes

- Registro dos pedidos no banco de dados.
- Identificação do pedido por ID.
- Armazenamento de:
  - Cliente;
  - Tamanho;
  - Toppings;
  - Forma de pagamento;
  - Opção de entrega;
  - Subtotal;
  - Taxa de entrega;
  - Total;
  - Data e horário.
- Exibição do comprovante após a finalização.
- Exportação do comprovante do pedido em formato `.json`.

### 👑 Root Master

O sistema possui uma área administrativa chamada **Root Master**, destinada ao gerenciamento dos dados armazenados.

O administrador pode:

- Acessar o painel administrativo por login.
- Visualizar clientes cadastrados.
- Consultar informações dos clientes.
- Selecionar um cliente e exportar seus dados em `.json`.
- Exportar todos os clientes em um único arquivo `.json`.
- Visualizar os pedidos registrados.
- Consultar informações de cada pedido.
- Exportar o comprovante de um pedido em `.json`.
- Exportar todos os pedidos em um único arquivo `.json`.

### 📦 Exportação JSON

O sistema permite exportar informações para arquivos `.json`, facilitando:

- Backup dos dados;
- Demonstração do projeto;
- Análise das informações;
- Compartilhamento de registros;
- Geração de comprovantes digitais.

Os arquivos são salvos no local escolhido pelo usuário por meio da janela de seleção de arquivo.

---

## 🗃️ Banco de Dados

O sistema utiliza **SQLite3**, um banco de dados local que não exige servidor externo.

O arquivo principal do banco é:

```text
database/acai_sistema.db
```

### Tabela `clientes`

Armazena informações relacionadas aos clientes, incluindo:

- `id`
- `nome`
- `apelido`
- `cpf`
- `telefone`
- `email`
- `endereco`
- `idade`
- `pontos_fidelidade`
- `foto_path`

### Tabela `pedidos`

Armazena os pedidos realizados pelos clientes:

- `id`
- `cliente_id`
- `tamanho`
- `toppings`
- `forma_pagamento`
- `opcao_entrega`
- `subtotal`
- `taxa_entrega`
- `total`
- `data_hora`

Existe uma relação entre `pedidos.cliente_id` e `clientes.id`.

---

## 📂 Estrutura do Projeto

A organização esperada dos arquivos é:

```text
📁 projetos_cdt/
│
├── 📁 assets/
│   └── 📁 faces/
│       └── 🖼️ face_<cpf>.jpg
│
├── 📁 database/
│   ├── 🗃️ acai_sistema.db
│   └── 🐍 db.py
│
├── 📁 src/
│   ├── 🐍 app.py
│   └── 🐍 camera.py
│
├── 🐍 main.py
├── 📄 requirements.txt
└── 📄 README.md
```

### Descrição das principais pastas e arquivos

| Arquivo/Pasta | Função |
|---|---|
| `main.py` | Ponto de entrada da aplicação e integração entre a interface e o fluxo de Face ID |
| `src/app.py` | Interface gráfica, cadastro, cardápio, carrinho, checkout, comprovante e Root Master |
| `src/camera.py` | Controle da webcam, captura da imagem facial e detecção de rosto |
| `database/db.py` | Criação/atualização do banco, cadastro, consultas, pedidos e exportação JSON |
| `database/acai_sistema.db` | Banco de dados SQLite utilizado pela aplicação |
| `assets/faces/` | Armazena as imagens faciais cadastradas |
| `requirements.txt` | Lista das dependências externas do projeto |
| `README.md` | Documentação do projeto |

---

## 📦 Instalação

### 1. Clonar ou baixar o projeto

Abra o terminal na pasta do projeto.

### 2. Criar um ambiente virtual

No Windows:

```bash
python -m venv .venv
```

Ative o ambiente:

```bash
.venv\Scripts\activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

As principais dependências externas são:

```text
opencv-python
numpy
customtkinter
Pillow
```

---

## ▶️ Executando o Sistema

Com as dependências instaladas, execute:

```bash
python main.py
```

Na primeira execução, o sistema cria automaticamente os diretórios e inicializa o banco SQLite quando necessário.

---

## 📤 Exportação de Dados

A exportação pode ser realizada pelo cliente, no caso do comprovante, ou pelo Root Master, para gerenciamento administrativo.

### Cliente

Após finalizar um pedido, o sistema disponibiliza a opção de exportar o comprovante em:

```text
comprovante_pedido_<id>.json
```

### Root Master

O administrador pode exportar:

```text
cliente_<id>.json
clientes_acai_zon.json
comprovante_pedido_<id>.json
pedidos_acai_zon.json
```

O local de salvamento é escolhido pelo usuário no momento da exportação.

---

## 👥 Organização da Equipe

O projeto foi dividido em módulos para facilitar o desenvolvimento colaborativo:

### 👩‍💻 Pessoa 1 — Visão Computacional (Lari)

Responsável pelo módulo relacionado à:

- Webcam;
- OpenCV;
- Detecção facial;
- Captura das imagens;
- Fluxo de Face ID.

### 👩‍💻 Pessoa 2 — Back-end e Banco de Dados (Lu)

Responsável pelo:

- Banco de dados SQLite;
- Cadastro e consulta de clientes;
- Registro dos pedidos;
- Pontos de fidelidade;
- Recuperação de dados;
- Exportação em JSON;
- Suporte ao módulo administrativo Root Master.

### 👩‍💻 Pessoa 3 — Interface Gráfica / Front-end (Yas)

Responsável pela:

- Interface gráfica;
- Organização visual das telas;
- Navegação da aplicação;
- Componentes de interação com o usuário;
- Integração visual das funcionalidades do sistema.

---

## 🔒 Observações de Segurança e Privacidade

O projeto trabalha com dados pessoais e imagens faciais, portanto, em uma aplicação real seria necessário implementar medidas adicionais de segurança e privacidade.

Entre elas:

- Proteção adequada das credenciais administrativas;
- Controle de acesso;
- Criptografia de dados sensíveis;
- Armazenamento seguro das imagens faciais;
- Políticas de retenção e exclusão de dados;
- Tratamento adequado de dados pessoais e biométricos;
- Auditoria de acesso às informações administrativas.

Neste projeto educacional, essas funcionalidades são apresentadas em uma implementação local para fins de estudo e demonstração.

---

## 📚 Objetivo Educacional

O principal objetivo do Açaízon é aplicar, em um único projeto, conhecimentos de:

- Lógica de programação;
- Python;
- Programação orientada a funções;
- Banco de dados;
- CRUD;
- Interface gráfica;
- Manipulação de arquivos;
- JSON;
- Integração entre módulos;
- Visão computacional;
- Webcam;
- Automação;
- Controle de acesso;
- Organização de projetos de software.

O projeto também demonstra como diferentes módulos desenvolvidos por uma equipe podem ser integrados em uma única aplicação desktop.

---

## 👩‍💻 Projeto Educacional

**Açaízon — Automação + Reconhecimento Facial**

Projeto desenvolvido em equipe para fins educacionais, com foco na integração entre **Python, banco de dados, interface gráfica, visão computacional e automação de pedidos**.
