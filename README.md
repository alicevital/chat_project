# PIXELCHAT - Plataforma de Chat em Tempo Real

Plataforma de chat desenvolvida com **Python**, **FastAPI**, **WebSockets** e **RabbitMQ**, permitindo comunicação em tempo real entre usuários, com suporte a histórico de mensagens e autenticação segura via JWT.

---

## Tecnologias Utilizadas
- **FastAPI** — API e gerenciamento de WebSockets  
- **RabbitMQ** — Mensageria e comunicação assíncrona  
- **JWT** — Autenticação e gerenciamento de sessões  
- **MongoDB** — Persistência de mensagens e usuários  

---

## Requisitos Funcionais

### RF1 — Cadastro e Autenticação
- Usuários podem criar contas e realizar login.
- Autenticação via **JWT** ou estratégia segura equivalente.
- Sessões compatíveis com conexões **WebSocket**.

### RF2 — Comunicação em Tempo Real
- Envio e recebimento de mensagens instantâneas via **WebSockets**.
- **Broadcast:** envio de mensagens para todos os usuários conectados.
- **Mensagens privadas:** comunicação direta entre dois usuários.
- Participação em **salas** com histórico acessível.

### RF3 — Filtragem e Persistência de Mensagens
- Todas as mensagens são armazenadas em banco de dados.
- Recuperação de histórico (público e privado).
- Cada mensagem inclui:
  - Remetente
  - Destinatário (ou broadcast)
  - Timestamp
  - Conteúdo

---

## Status do Projeto
Em desenvolvimento. Instruções de instalação, execução e deploy serão adicionadas em breve.

---

## Próximos Passos
- Adicionar documentação da API
- Adicionar docker-compose para subir RabbitMQ + aplicação
- Implementar interface frontend
