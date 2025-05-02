
## 🧾 PDF to PNG OCR-Ready API

Transforma qualquer PDF (texto ou escaneado) em imagens `.png` prontas pro OCR, com contraste turbinado, cortes nos espaços em branco e tudo em base64.

---

### 🚀 O que essa belezinha faz?

* 📄 Aceita um PDF (upload via `multipart/form`)
* 🔍 Converte cada página em PNG com DPI alto (300)
* 🌈 Melhora contraste e nitidez
* ✂️ Corta os espaços em branco automagicamente
* 🧬 Retorna as imagens em **base64**, o nome do arquivo e um UUID

---

### 🔧 Como rodar com Docker

```bash
docker build -t pdf-api .
docker run -d -p 9999:9999 --name pdf-api pdf-api
```

Não tem `docker-compose` porque não

---

### Como usar

**POST /convert-pdf**

Envie um arquivo PDF no corpo da requisição (`form-data`), com o campo chamado `file`.

**Exemplo de resposta:**

```json
{
  "uuid": "xxxxxx-xxxx-xxxx-xxxx",
  "filename": "meuarquivo.pdf",
  "images_base64": [
    "iVBORw0KGgoAAAANSUhEUgAAA...", 
    "iVBORw0KGgoAAAANSUhEUgAAA..."
  ]
}
```

---

### 🛠️ Requisitos locais (sem Docker)

Se quiser rodar sem Docker:

```bash
sudo apt install poppler-utils
pip install -r requirements.txt
uvicorn main:app --reload --port 9999
```

---

### 📁 Estrutura do projeto

```
.
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml (opcional)
└── README.md
```

---

### ❤️ Feito pra rodar liso em VPS

Simples e direto. Pronto pra mandar ver com OCR depois!
