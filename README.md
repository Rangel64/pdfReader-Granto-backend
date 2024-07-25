# API de Processamento de Arquivos PDF

Este repositório contém uma aplicação de servidor baseada em FastAPI para lidar com uploads de arquivos PDF, autenticação de usuários e processamento de arquivos. Ele integra o Firebase para gerenciamento de usuários e armazenamento, e utiliza várias bibliotecas para manipulação de PDFs e outros tipos de arquivos.

## Funcionalidades

- Autenticação de Usuários (Login, Logout, Cadastro) usando Firebase
- Upload e processamento de arquivos (PDF, imagens, DOCX, HTML, TXT)
- Conversão de vários tipos de arquivos para PDF
- Extração e análise de conteúdo PDF
- Exportação de arquivos processados
- Endpoints de API RESTful

## Tecnologias Utilizadas

- **FastAPI**: Framework web para construção de APIs
- **Firebase**: Backend como Serviço para autenticação e armazenamento
- **PyPDF2**: Biblioteca para manipulação de PDFs
- **Langchain**: Ferramenta de processamento de texto
- **Sentence Transformers**: Modelos para transformação de sentenças
- **Pillow**: Biblioteca para manipulação de imagens
- **docx2pdf**: Conversão de DOCX para PDF
- **pdfkit**: Conversão de HTML para PDF
- **FPDF**: Geração de PDFs

## Instalação

1. Clone este repositório:
    ```sh
    git clone <url-do-repositorio>
    cd <nome-do-repositorio>
    ```

2. Crie um ambiente virtual e ative-o:
    ```sh
    python -m venv venv
    source venv/bin/activate  # No Windows, use `venv\Scripts\activate`
    ```

3. Instale as dependências:
    ```sh
    pip install -r requirements.txt
    ```

4. Configure suas credenciais do Firebase:
    - Coloque seu arquivo `serviceAccountKey.json` na raiz do projeto.
    - Preencha os detalhes de configuração do Firebase em `firebaseConfig` no código.

5. Inicie o servidor:
    ```sh
    uvicorn main:app --reload
    ```

## Endpoints da API

### Autenticação

- **Login**: `POST /login`
- **Logout**: `POST /logout`
- **Cadastro**: `POST /signup`
- **Validação de Token**: `POST /ping`

### Processamento de Arquivos

- **Upload de Arquivo**: `POST /upload`
- **Exportação de Arquivos do Usuário**: `GET /export_user_files/{file_id}`
- **Obter Arquivo do Usuário**: `GET /user_files/{file_id}`
- **Listar Arquivos do Usuário**: `GET /user_files`

### Raiz

- **Status do Servidor**: `GET /`

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir uma issue ou enviar um pull request.

## Licença

Este projeto está licenciado sob os termos da licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.