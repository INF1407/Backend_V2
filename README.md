# WeShop

## Integrantes
- Tomás Lenzi
- Gabriel Emile

## Escopo do Site
- O WeShop é um marketplace de roupas que conecta múltiplos varejistas a potenciais clientes. Ele oferece funcionalidades completas de navegação, login e gerenciamento de carrinho de compras.

## Funcionamento do Site
- Página inicial
- Shopping cart
- Login/Cadastro

## Funcionamento do Backend
- Operações CRUD para produtos, pedidos e usuários.
- Sistema de autenticação com endpoints protegidos.
- Endpoints documentados com Swagger.

## Link do Backend Publicado

👉 https://we-shop-3f005a9a94c2.herokuapp.com/

Instruções para Rodar Localmente
Backend

    Clone o repositório:

git clone https://github.com/INF1407/Backend_V2.git
cd Backend_V2

Instale as dependências:

pip install -r requirements.txt

Realize as migrações:

python manage.py migrate

Inicie o servidor:

python manage.py runserver

Documentação disponível em /swagger/.
