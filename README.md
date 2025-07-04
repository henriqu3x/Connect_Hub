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

## 📝 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---
=======
# Connect_Hub
Sistema de gerenciamento de condominio
