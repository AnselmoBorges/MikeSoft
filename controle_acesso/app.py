import streamlit as st
import duckdb
import datetime
import os
from PIL import Image
import numpy as np
import cv2
import face_recognition
import io
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

# Funções auxiliares

def calcular_idade(data_nascimento):
    hoje = datetime.date.today()
    return hoje.year - data_nascimento.year - ((hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day))

def obter_categoria_idade(idade, con):
    result = con.execute("SELECT nome FROM categorias_idade WHERE ? BETWEEN idade_min AND idade_max", [idade]).fetchone()
    return result[0] if result else "Desconhecida"

def obter_categoria_peso(peso, sexo, con):
    result = con.execute("SELECT nome FROM categorias_peso WHERE ? BETWEEN peso_min AND peso_max AND sexo = ?", [peso, sexo]).fetchone()
    return result[0] if result else "Desconhecida"

def salvar_foto(foto, nome):
    imagem = foto.convert("RGB")
    caminho = f"alunos/{nome}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    imagem.save(caminho)
    return caminho

def gerar_encoding(imagem_pil):
    # Converte PIL para array numpy RGB
    img = np.array(imagem_pil.convert("RGB"))
    # face_recognition espera formato (H, W, 3) RGB
    faces = face_recognition.face_encodings(img)
    if len(faces) == 0:
        return None
    return faces[0].tobytes()

# Conexão com o banco
con = duckdb.connect('academia.duckdb')

st.set_page_config(page_title="Controle de Acesso Academia", layout="centered")
st.sidebar.title("Menu")
opcao = st.sidebar.radio("Escolha uma opção:", ["Cadastro de Aluno", "Reconhecimento Facial", "Reconhecimento Facial (Streaming)", "Gerenciar Alunos"])

if opcao == "Cadastro de Aluno":
    st.title("Cadastro de Aluno")
    with st.form(key="form_cadastro"):
        nome = st.text_input("Nome completo")
        data_nascimento = st.date_input("Data de nascimento", min_value=datetime.date(1900,1,1), max_value=datetime.date.today())
        sexo = st.selectbox("Sexo", ["Masculino", "Feminino"])
        faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Marrom", "Preta"])
        peso = st.number_input("Peso (kg)", min_value=10.0, max_value=200.0, step=0.1)
        endereco = st.text_input("Endereço")
        st.markdown("**Foto do aluno:**")
        foto_webcam = st.camera_input("Tirar foto com webcam")
        foto_upload = st.file_uploader("Ou envie uma foto (jpg/png)", type=["jpg", "jpeg", "png"])
        if foto_webcam:
            st.image(foto_webcam, caption="Pré-visualização da foto (webcam)", width=200)
        elif foto_upload:
            st.image(foto_upload, caption="Pré-visualização da foto (upload)", width=200)
        submit = st.form_submit_button("Cadastrar")

    if submit:
        foto = foto_webcam if foto_webcam else foto_upload
        if not (nome and data_nascimento and sexo and faixa and peso and endereco and foto):
            st.error("Preencha todos os campos e envie ou tire uma foto!")
        else:
            idade = calcular_idade(data_nascimento)
            categoria_idade = obter_categoria_idade(idade, con)
            categoria_peso = obter_categoria_peso(peso, sexo, con)
            imagem = Image.open(foto)
            caminho_foto = salvar_foto(imagem, nome.replace(" ", "_"))
            encoding = gerar_encoding(imagem)
            if encoding is None:
                st.error("Nenhum rosto detectado na foto. Tente outra imagem!")
            else:
                con.execute("INSERT INTO alunos (nome, data_nascimento, sexo, faixa, peso, categoria_idade, categoria_peso, endereco, foto_path, encoding) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                            (nome, data_nascimento, sexo, faixa, peso, categoria_idade, categoria_peso, endereco, caminho_foto, encoding))
                st.success(f"Aluno {nome} cadastrado com sucesso! Categoria: {categoria_idade} / {categoria_peso}")

elif opcao == "Reconhecimento Facial":
    st.title("Reconhecimento Facial")
    st.info("Aponte seu rosto para a webcam e clique em 'Reconhecer'.")

    # Captura da webcam
    img_file = st.camera_input("Tirar foto")

    if img_file is not None:
        # Carregar imagem capturada
        img = Image.open(img_file)
        img_np = np.array(img.convert('RGB'))

        # Detectar localização dos rostos
        face_locations = face_recognition.face_locations(img_np)
        face_encodings = face_recognition.face_encodings(img_np, face_locations)

        # Desenhar bounding box
        if len(face_locations) > 0:
            img_box = img_np.copy()
            for top, right, bottom, left in face_locations:
                cv2.rectangle(img_box, (left, top), (right, bottom), (0,255,0), 2)
            st.image(img_box, caption="Rosto(s) detectado(s)", channels="RGB")
        else:
            st.image(img_np, caption="Nenhum rosto detectado", channels="RGB")

        if len(face_encodings) == 0:
            st.error("Nenhum rosto detectado na imagem. Tente novamente.")
        else:
            encoding_capturado = face_encodings[0]
            # Carregar encodings dos alunos
            alunos = con.execute("SELECT nome, encoding FROM alunos WHERE encoding IS NOT NULL").fetchall()
            nomes = []
            encodings = []
            for nome, enc in alunos:
                if enc is not None:
                    enc_np = np.frombuffer(enc, dtype=np.float64)
                    encodings.append(enc_np)
                    nomes.append(nome)
            if len(encodings) == 0:
                st.warning("Nenhum aluno cadastrado com encoding facial.")
            else:
                # Comparar
                resultados = face_recognition.compare_faces(encodings, encoding_capturado, tolerance=0.5)
                if any(resultados):
                    idx = resultados.index(True)
                    st.success(f"Aluno reconhecido: {nomes[idx]}")
                else:
                    st.warning("Rosto não reconhecido.")

elif opcao == "Reconhecimento Facial (Streaming)":
    st.title("Reconhecimento Facial (Streaming)")
    st.info("Aponte seu rosto para a webcam. O reconhecimento será feito automaticamente em tempo real.")

    if 'nome_reconhecido' not in st.session_state:
        st.session_state['nome_reconhecido'] = ''

    class FaceRecognitionProcessor(VideoTransformerBase):
        def __init__(self):
            self.alunos = con.execute("SELECT nome, encoding FROM alunos WHERE encoding IS NOT NULL").fetchall()
            self.nomes = []
            self.encodings = []
            for nome, enc in self.alunos:
                if enc is not None:
                    enc_np = np.frombuffer(enc, dtype=np.float64)
                    self.encodings.append(enc_np)
                    self.nomes.append(nome)

        def recv(self, frame):
            img = frame.to_ndarray(format="bgr24")
            face_locations = face_recognition.face_locations(img)
            face_encodings = face_recognition.face_encodings(img, face_locations)
            nome_exibido = None
            reconhecido = False
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                resultados = face_recognition.compare_faces(self.encodings, encoding, tolerance=0.5)
                if any(resultados):
                    idx = resultados.index(True)
                    nome_exibido = self.nomes[idx]
                    reconhecido = True
                    cv2.rectangle(img, (left, top), (right, bottom), (0,255,0), 2)
                    cv2.putText(img, nome_exibido, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,0), 2)
                else:
                    cv2.rectangle(img, (left, top), (right, bottom), (0,0,255), 2)
                    cv2.putText(img, "Desconhecido", (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,0,255), 2)
            # Atualiza o nome reconhecido no estado
            if reconhecido and nome_exibido:
                st.session_state['nome_reconhecido'] = f"Aluno reconhecido: {nome_exibido}"
            elif len(face_locations) > 0:
                st.session_state['nome_reconhecido'] = "Rosto não reconhecido."
            else:
                st.session_state['nome_reconhecido'] = "Nenhum rosto detectado."
            return av.VideoFrame.from_ndarray(img, format="bgr24")

    ctx = webrtc_streamer(
        key="reconhecimento-facial-streaming",
        video_processor_factory=FaceRecognitionProcessor
    )
    st.markdown(f"**{st.session_state['nome_reconhecido']}**")

elif opcao == "Gerenciar Alunos":
    st.title("Gerenciar Alunos")
    alunos = con.execute("SELECT id, nome, faixa, categoria_idade, categoria_peso, endereco, data_nascimento, sexo, peso, foto_path FROM alunos").fetchall()
    if not alunos:
        st.info("Nenhum aluno cadastrado.")
    else:
        for idx, aluno in enumerate(alunos):
            col1, col2, col3, col4, col5, col6, col7 = st.columns([2,2,2,2,2,1,1])
            with col1:
                st.write(aluno[1])  # nome
            with col2:
                st.write(aluno[2])  # faixa
            with col3:
                st.write(aluno[3])  # categoria_idade
            with col4:
                st.write(aluno[4])  # categoria_peso
            with col5:
                st.write(aluno[5])  # endereco
            with col6:
                if st.button("Editar", key=f"editar_{aluno[0]}_{idx}"):
                    st.session_state['editando'] = aluno[0]
            with col7:
                if st.button("Remover", key=f"remover_{aluno[0]}_{idx}"):
                    st.session_state['remover'] = aluno[0]
                    st.rerun()

    # Edição
    if 'editando' in st.session_state:
        aluno_id = st.session_state['editando']
        dados = con.execute("SELECT nome, data_nascimento, sexo, faixa, peso, categoria_idade, categoria_peso, endereco, foto_path FROM alunos WHERE id = ?", [aluno_id]).fetchone()
        st.subheader(f"Editar Aluno: {dados[0]}")
        with st.form(key="form_editar"):
            nome = st.text_input("Nome completo", value=dados[0])
            data_nascimento = st.date_input("Data de nascimento", value=dados[1])
            sexo = st.selectbox("Sexo", ["Masculino", "Feminino"], index=0 if dados[2]=="Masculino" else 1)
            faixa = st.selectbox("Faixa", ["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Marrom", "Preta"], index=["Branca", "Cinza", "Amarela", "Laranja", "Verde", "Azul", "Roxa", "Marrom", "Preta"].index(dados[3]))
            peso = st.number_input("Peso (kg)", min_value=10.0, max_value=200.0, step=0.1, value=float(dados[4]))
            endereco = st.text_input("Endereço", value=dados[7])
            st.markdown("**Foto do aluno:**")
            foto_webcam = st.camera_input("Tirar nova foto com webcam (opcional)")
            foto_upload = st.file_uploader("Ou envie nova foto (opcional)", type=["jpg", "jpeg", "png"])
            if foto_webcam:
                st.image(foto_webcam, caption="Pré-visualização da foto (webcam)", width=200)
            elif foto_upload:
                st.image(foto_upload, caption="Pré-visualização da foto (upload)", width=200)
            submit = st.form_submit_button("Salvar alterações")
        if submit:
            foto = foto_webcam if foto_webcam else foto_upload
            if foto:
                imagem = Image.open(foto)
                caminho_foto = salvar_foto(imagem, nome.replace(" ", "_"))
                encoding = gerar_encoding(imagem)
                if encoding is None:
                    st.error("Nenhum rosto detectado na foto. Tente outra imagem!")
                    st.stop()
            else:
                caminho_foto = dados[8]
                encoding = None
            idade = calcular_idade(data_nascimento)
            categoria_idade = obter_categoria_idade(idade, con)
            categoria_peso = obter_categoria_peso(peso, sexo, con)
            if encoding:
                con.execute("UPDATE alunos SET nome=?, data_nascimento=?, sexo=?, faixa=?, peso=?, categoria_idade=?, categoria_peso=?, endereco=?, foto_path=?, encoding=? WHERE id=?",
                            (nome, data_nascimento, sexo, faixa, peso, categoria_idade, categoria_peso, endereco, caminho_foto, encoding, aluno_id))
            else:
                con.execute("UPDATE alunos SET nome=?, data_nascimento=?, sexo=?, faixa=?, peso=?, categoria_idade=?, categoria_peso=?, endereco=?, foto_path=? WHERE id=?",
                            (nome, data_nascimento, sexo, faixa, peso, categoria_idade, categoria_peso, endereco, caminho_foto, aluno_id))
            st.success("Alterações salvas!")
            del st.session_state['editando']
            st.rerun()

    # Bloco de confirmação de remoção (fora do loop)
    if 'remover' in st.session_state:
        aluno_id = st.session_state['remover']
        dados = con.execute("SELECT nome FROM alunos WHERE id = ?", [aluno_id]).fetchone()
        if dados is None:
            del st.session_state['remover']
            st.rerun()
        else:
            st.warning(f"Tem certeza que deseja remover o aluno '{dados[0]}'?")
            col_confirma, col_cancela = st.columns(2)
            with col_confirma:
                if st.button("Confirmar remoção", key=f"confirma_remover_{aluno_id}"):
                    con.execute("DELETE FROM alunos WHERE id = ?", [aluno_id])
                    st.success("Aluno removido com sucesso!")
                    del st.session_state['remover']
                    st.rerun()
            with col_cancela:
                if st.button("Cancelar", key=f"cancela_remover_{aluno_id}"):
                    del st.session_state['remover']
                    st.rerun() 