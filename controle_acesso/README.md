# Sistema de Controle de Acesso para Academia (Jiu-Jitsu)

Este projeto é um sistema de controle de acesso com reconhecimento facial, cadastro de alunos, cálculo automático de categoria de idade e peso conforme IBJJF, desenvolvido em Python para rodar localmente (Mac ou Raspberry Pi 4).

## Funcionalidades
- Cadastro de alunos com foto (webcam)
- Reconhecimento facial para controle de presença
- Cálculo automático de categoria de idade e peso
- Cadastro de faixa, endereço, etc.
- Banco de dados local DuckDB
- Interface web com Streamlit

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

### 3. Instale as dependências do sistema
```bash
pip install --upgrade pip
pip install -r requirements.txt
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

## Estrutura do Projeto
```
controle_acesso/
├── alunos/                # Fotos dos alunos
├── academia.duckdb        # Banco de dados DuckDB
├── app.py                 # Código principal Streamlit
├── init_db.py             # Script de inicialização do banco
├── requirements.txt       # Dependências Python
└── README.md              # Este arquivo
```

## Observações
- O sistema foi pensado para rodar localmente, sem custos de nuvem.
- O reconhecimento facial utiliza a biblioteca `face_recognition` (dlib), que pode demorar para instalar na primeira vez.
- O banco DuckDB pode ser copiado entre Mac e Raspberry Pi sem problemas.

## Próximos Passos
- Após instalar tudo, rode o app com:
```bash
streamlit run app.py
```

- Siga as instruções na interface para cadastrar alunos e registrar presenças.

---

Se tiver dúvidas ou problemas na instalação, envie a mensagem de erro para suporte!
