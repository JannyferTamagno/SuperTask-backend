# SuperTask Backend 🚀

API REST completa para gerenciamento de tarefas com dashboard inteligente e frases motivacionais diárias. Desenvolvida com Django REST Framework.

> 📱 **Frontend:** [SuperTask Frontend (Next.js)](https://github.com/JannyferTamagno/SuperTask-frontend)

## 📋 Funcionalidades

- ✅ **CRUD completo de tarefas** - Criar, ler, atualizar e deletar tarefas
- 🏷️ **Sistema de categorias** - Organize suas tarefas por categorias personalizadas
- 📊 **Dashboard com estatísticas** - Visualize seu progresso com gráficos e métricas
- 💬 **Frase motivacional diária** - Comece o dia com inspiração usando a Quotable API
- 🔍 **Filtros e busca avançada** - Encontre tarefas por prioridade, status, categoria e data
- 🔐 **Autenticação JWT** - Sistema seguro de login e registro
- 📱 **Design responsivo** - Interface adaptável para desktop e mobile
- ⚡ **Real-time updates** - Atualizações em tempo real
- 🧪 **Testes automatizados** - Cobertura completa de testes no backend
- 🐳 **Docker ready** - Fácil deploy com Docker Compose

## 🛠️ Tech Stack

**Backend (Este repositório):**

- Django 4.2.7
- Django REST Framework 3.14.0
- PostgreSQL
- JWT Authentication (djangorestframework-simplejwt)
- CORS Headers
- Gunicorn

**Infrastructure:**

- Docker & Docker Compose
- PostgreSQL
- Render (Deploy)

**APIs Externas:**

- [Quotable API](https://github.com/lukePeavey/quotable) - Frases motivacionais

## 📦 Instalação

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.11+ (se executar sem Docker)

### Executando com Docker (Recomendado)

1. Clone o repositório:

```bash
git clone https://github.com/seu-usuario/supertask-backend.git
cd supertask-backend
```

2. Execute com Docker Compose:

```bash
docker-compose up --build
```

3. Acesse a API:

- Backend API: <http://localhost:8000>
- Documentação: <http://localhost:8000/>
- Admin: <http://localhost:8000/admin/>

### Executando localmente

1. Clone e configure o backend:

```bash
git clone https://github.com/seu-usuario/supertask-backend.git
cd supertask-backend

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure as variáveis de ambiente
cp .env.example .env

# Execute as migrações
python manage.py migrate

# Crie um superusuário
python manage.py createsuperuser

# Execute o servidor
python manage.py runserver
```

## 🔧 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://usuario:senha@localhost:5432/supertask_db

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=60
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7
```

## 🧪 Executando os Testes

```bash
# Executar todos os testes
python manage.py test

# Executar testes com verbose
python manage.py test --verbosity=2

# Executar testes específicos
python manage.py test accounts.tests
python manage.py test tasks.tests
```

## 📖 API Reference

### Autenticação

#### Registrar usuário

```http
POST /api/auth/register/
```

```json
{
  "username": "usuario",
  "email": "user@example.com",
  "password": "senha123",
  "password_confirm": "senha123",
  "first_name": "Nome",
  "last_name": "Sobrenome"
}
```

#### Login

```http
POST /api/auth/login/
```

```json
{
  "username": "usuario",
  "password": "senha123"
}
```

#### Obter informações do usuário

```http
GET /api/auth/user/
```

| Header | Type | Description |
| :-------- | :------- | :------------------------- |
| `Authorization` | `Bearer token` | **Required**. JWT access token |

### Tarefas

#### Listar tarefas

```http
GET /api/tasks/
```

**Query Parameters:**

| Parameter | Type | Description |
| :-------- | :------- | :-------------------------------- |
| `priority` | `string` | Filtrar por prioridade (low, medium, high) |
| `status` | `string` | Filtrar por status (pending, in_progress, completed) |
| `category` | `integer` | Filtrar por categoria (ID) |
| `due_date` | `string` | Filtrar por data (today, overdue) |
| `ordering` | `string` | Ordenar por campo (-created_at, due_date, priority) |

#### Criar tarefa

```http
POST /api/tasks/
```

```json
{
  "title": "Minha tarefa",
  "description": "Descrição da tarefa",
  "priority": "high",
  "status": "pending",
  "due_date": "2024-12-31",
  "category": 1
}
```

#### Obter tarefa específica

```http
GET /api/tasks/${id}/
```

#### Atualizar tarefa

```http
PATCH /api/tasks/${id}/
```

#### Deletar tarefa

```http
DELETE /api/tasks/${id}/
```

#### Alternar status da tarefa

```http
PATCH /api/tasks/${id}/toggle-status/
```

### Categorias

#### Listar categorias

```http
GET /api/categories/
```

#### Criar categoria

```http
POST /api/categories/
```

```json
{
  "name": "Trabalho",
  "color": "#ff6b6b"
}
```

### Dashboard

#### Obter estatísticas

```http
GET /api/dashboard/stats/
```

**Resposta:**

```json
{
  "completed": 15,
  "in_progress": 3,
  "overdue": 2,
  "high_priority": 5,
  "due_today": 1,
  "total_tasks": 25,
  "categories_stats": {
    "Trabalho": {
      "total": 10,
      "completed": 7,
      "pending": 3
    }
  }
}
```

#### Obter frase motivacional diária

```http
GET /api/dashboard/quote/
```

**Resposta:**

```json
{
  "quote": "The only way to do great work is to love what you do.",
  "author": "Steve Jobs",
  "source": "quotable_api"
}
```

## 🚀 Deploy

### Render

1. Conecte seu repositório ao Render
2. Configure as variáveis de ambiente
3. O arquivo `build.sh` será executado automaticamente
4. A aplicação será servida via Gunicorn

### Variáveis de ambiente para produção

```bash
SECRET_KEY=sua-chave-secreta-super-segura
DEBUG=False
DATABASE_URL=postgresql://usuario:senha@host:porta/database
ALLOWED_HOSTS=seu-dominio.onrender.com
```

## 📁 Estrutura do Projeto

```
supertask-backend/
├── accounts/              # App de autenticação
│   ├── models.py         # UserProfile
│   ├── serializers.py    # Serializers de auth
│   ├── views.py          # Views de auth
│   └── tests.py          # Testes de autenticação
├── tasks/                # App principal
│   ├── models.py         # Task e Category
│   ├── serializers.py    # Serializers de tasks
│   ├── views.py          # Views de tasks e dashboard
│   └── tests.py          # Testes de tasks
├── supertask/            # Configurações Django
│   ├── settings.py       # Configurações principais
│   └── urls.py           # URLs principais
├── requirements.txt      # Dependências Python
├── Dockerfile           # Configuração Docker
├── docker-compose.yml   # Orquestração de containers
└── build.sh            # Script de build para deploy
```

## 🤝 Contribuindo

1. Faça o fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📋 Roadmap

- [x] **API REST completa** - CRUD de tarefas e categorias
- [x] **Autenticação JWT** - Sistema seguro de auth
- [x] **Dashboard com estatísticas** - Métricas e analytics
- [x] **Frases motivacionais** - Integração com Quotable API
- [x] **Testes automatizados** - Cobertura completa
- [x] **Deploy Render** - Produção estável
- [x] **Frontend Next.js** - [Repositório Frontend](https://github.com/JannyferTamagno/SuperTask-frontend)
- [ ] **WebSockets** - Real-time updates
- [ ] **Notificações push** - Lembretes de tarefas
- [ ] **Upload de arquivos** - Anexos nas tarefas
- [ ] **API de relatórios** - Análises de produtividade
- [ ] **Integração calendário** - Google Calendar, Outlook
- [ ] **Sistema de colaboração** - Compartilhar tarefas
- [ ] **Templates de tarefas** - Modelos predefinidos
- [ ] **App mobile** - React Native

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 🔗 Repositórios Relacionados

- **Frontend:** [SuperTask Frontend](https://github.com/JannyferTamagno/SuperTask-frontend) - Interface Next.js com TailwindCSS
- **Backend:** Este repositório - API Django REST

## 👨‍💻 Autor

**Jannyfer Tamagno**

- GitHub: [@JannyferTamagno](https://github.com/JannyferTamagno)
- LinkedIn: [@jannyfer-tamagno](https://linkedin.com/in/jannyfertamagno)

## 🙏 Agradecimentos

- [Django REST Framework](https://www.django-rest-framework.org/) - Framework incrível para APIs
- [Quotable API](https://github.com/lukePeavey/quotable) - API de citações motivacionais
- [Render](https://render.com/) - Plataforma de deploy confiável

---

⭐ Não esqueça de dar uma estrela se este projeto te ajudou!
