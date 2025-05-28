# Sistema de Controle de Acesso para Academia (Jiu-Jitsu)

Este projeto é um sistema de controle de acesso com reconhecimento facial, cadastro de alunos, cálculo automático de categoria de idade e peso conforme IBJJF, desenvolvido em Python para rodar localmente (Mac ou Raspberry Pi 4).

## Funcionalidades
- Cadastro de alunos com foto (webcam ou upload)
- Reconhecimento facial para controle de presença
- Reconhecimento facial em tempo real (streaming)
- Cálculo automático de categoria de idade e peso
- Cadastro de faixa, endereço, etc.
- Banco de dados local DuckDB
- Interface web com Streamlit
- Gerenciamento de alunos (editar/remover)

## Requisitos
- Python 3.12+
- Webcam HD
- Raspberry Pi 4 (ou Mac para desenvolvimento)

## Instalação do Ambiente

### 1. Clone o repositório e acesse a pasta
```bash
cd /Users/Anselmo/Documentos/MikeSoft/controle_acesso
```

### 2. Crie e ative o ambiente virtual
```bash
python3.12 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
pip install streamlit-webrtc
```

### 4. Instale dependências do sistema para reconhecimento facial
No macOS, é necessário instalar o CMake, Boost e Boost-Python3:

```bash
# Instale o Homebrew se não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instale CMake, Boost e Boost-Python3
brew install cmake boost boost-python3
```

Se der erro ao instalar o dlib, verifique se o CMake está instalado corretamente:
```bash
cmake --version
```

### 5. Inicialize o banco de dados
```bash
python init_db.py
```

### 6. Rode o sistema
```bash
streamlit run app.py
```

## Uso do Sistema

- **Cadastro de Aluno:** Cadastre novos alunos com foto (webcam ou upload), dados pessoais e faixa. O sistema calcula automaticamente a categoria de idade e peso.
- **Reconhecimento Facial:** Tire uma foto e o sistema reconhece o aluno, desenhando um retângulo no rosto.
- **Reconhecimento Facial (Streaming):** Use a webcam em tempo real para reconhecimento automático, com bounding box e nome do aluno na tela (requer `streamlit-webrtc`).
- **Gerenciar Alunos:** Edite ou remova alunos cadastrados.

## Observações
- O reconhecimento facial em streaming pode exigir mais processamento, principalmente no Raspberry Pi.
- Para melhor desempenho, use uma webcam de boa qualidade e ambiente bem iluminado.
- O sistema permite nomes duplicados, mas cada aluno tem um ID único.

---

Desenvolvido por Anselmo Borges de Moraes Junior
```bash
cmake --version
```

### 5. Inicialize o banco de dados
```bash
python init_db.py
```

### 6. Rode o sistema
```bash
streamlit run app.py
```

## Uso do Sistema

- **Cadastro de Aluno:** Cadastre novos alunos com foto (webcam ou upload), dados pessoais e faixa. O sistema calcula automaticamente a categoria de idade e peso.
- **Reconhecimento Facial:** Tire uma foto e o sistema reconhece o aluno, desenhando um retângulo no rosto.
- **Reconhecimento Facial (Streaming):** Use a webcam em tempo real para reconhecimento automático, com bounding box e nome do aluno na tela (requer `streamlit-webrtc`).
- **Gerenciar Alunos:** Edite ou remova alunos cadastrados.

## Observações
- O reconhecimento facial em streaming pode exigir mais processamento, principalmente no Raspberry Pi.
- Para melhor desempenho, use uma webcam de boa qualidade e ambiente bem iluminado.
- O sistema permite nomes duplicados, mas cada aluno tem um ID único.

---

Desenvolvido por Anselmo Borges de Moraes Junior
