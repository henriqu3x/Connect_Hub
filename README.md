# ConnectHub - Sistema de Gestão de Condomínio

O ConnectHub é um sistema completo de gestão de condomínios que facilita a comunicação entre síndicos e moradores, além de oferecer ferramentas para gerenciamento de ocorrências, reservas de áreas comuns, envio de comunicados e muito mais.

## 🚀 Funcionalidades

### Para Moradores
- **Acesso via login seguro**
- **Registro de ocorrências** com fotos
- **Reserva de áreas comuns** (salão de festas, churrasqueira, etc.)
- **Visualização de comunicados** do síndico
- **Notificações em tempo real**
- **Perfil personalizado**

### Para Síndicos
- **Dashboard administrativo**
- **Gerenciamento de moradores**
- **Aprovação de reservas**
- **Envio de comunicados**
- **Relatórios e estatísticas**
- **Gerenciamento de ocorrências**

## 🛠️ Tecnologias Utilizadas

- **Frontend**: KivyMD (Python)
- **Backend**: Python
- **Banco de Dados**: PostgreSQL
- **Autenticação**: Sistema próprio com criptografia bcrypt
- **Gerenciamento de Estado**: Kivy Properties
- **Interface**: Design responsivo e intuitivo

## 📋 Pré-requisitos

- Python 3.8 ou superior
- PostgreSQL 12+
- pip (gerenciador de pacotes do Python)
- Bibliotecas listadas em `requirements.txt`

## 🚀 Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/connecthub-condominio.git
   cd connecthub-condominio
   ```

2. **Crie um ambiente virtual (recomendado)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: .\venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o banco de dados**
   - Crie um banco de dados PostgreSQL
   - Atualize as configurações em `db/db_config.py`
   - Execute o script de atualização do banco de dados:
     ```bash
     python db/update_database.py
     ```

5. **Execute o aplicativo**
   ```bash
   python main.py
   ```

## 🏗️ Estrutura do Projeto

```
connecthub-condominio/
├── db/
│   ├── connection.py     # Conexão com o banco de dados
│   ├── db_config.py      # Configurações do banco de dados
│   ├── update_database.py # Script de atualização do banco
│   └── update_schema.sql # Esquema do banco de dados
├── screens/
│   ├── dashboard_morador_screen.py  # Tela do morador
│   ├── dashboard_sindico_screen.py  # Tela do síndico
│   ├── morador_login_screen.py      # Login do morador
│   ├── sindico_login_screen.py      # Login do síndico
│   ├── sindico_cadastro_screen.py   # Cadastro de síndico
│   ├── esqueci_minha_senha_screen.py# Recuperação de senha
│   └── redefina_sua_senha_screen.py # Redefinição de senha
├── utils/
│   ├── exportador_pdf.py # Geração de relatórios em PDF
│   └── file_manager.py   # Gerenciamento de arquivos
├── assets/               # Recursos visuais
├── main.py               # Ponto de entrada do aplicativo
└── requirements.txt      # Dependências do projeto
```

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Desenvolvido com ❤️ pela Equipe ConnectHub
=======
# Connect_Hub
Sistema de gerenciamento de condominio
>>>>>>> 8fd2e07c9762c71164d73c55cbb7c45cb20da00d
