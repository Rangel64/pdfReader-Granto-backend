from datetime import datetime
from typing import Annotated
from fastapi import Depends, FastAPI, Header, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from ollama import Client
from firebase_admin import credentials, auth
import uvicorn
import firebase_admin
import pyrebase
from models import LoginSchema, SignUpSchema
from fastapi.exceptions import HTTPException
from PIL import Image
from docx2pdf import convert as docx2pdf_convert
import pdfkit
from fpdf import FPDF
import io
from starlette.datastructures import UploadFile as StarletteUploadFile
import os
import subprocess

os.system("ollama pull")
os.system("ollama run llama3")
os.system("kill $(pgrep ollama)")

if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")
    firebase_admin.initialize_app(cred)

firebaseConfig = {
    "apiKey": "",
    "authDomain": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": "",
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
fb_storage = firebase.storage()
db = firebase.database()

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://granto-web-client-production.up.railway.app","http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_current_user(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        raise HTTPException(
            status_code=401, detail="Authorization token is missing")

    try:
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token['uid']
        return user_id
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/login")
async def create_access_token(user_data: LoginSchema, response: Response):
    email = user_data.email
    password = user_data.password
    
    try: 
        user = firebase.auth().sign_in_with_email_and_password(
            email=email,
            password=password
        )
        
        token = user["idToken"]
        
        response.set_cookie(key="Authorization", value=token, httponly=True, samesite='Strict')
        
        return JSONResponse(content={"message": "Login successful", "token": token}, status_code=200)
        
    except:
        raise HTTPException(
            status_code=400, detail="Invalid Credentials"
        )


@app.post("/logout")
async def logout(response: Response):
    # Remover o cookie de autenticação
    response.delete_cookie(key="Authorization")
    return JSONResponse(content={"message": "Logout successful"}, status_code=200)

def upload_pdf(file: UploadFile):
    pdf_path = f"pdfs/{file.filename}"
    fb_storage.child(pdf_path).put(file.file)
    return fb_storage.child(pdf_path).get_url(None)

@app.get("/export_user_files/{file_id}")
async def export_user_file(file_id: str):
    try:
        user_file = db.child("user_files").child(file_id).get()
        file_data = user_file.val()
        
        if not file_data:
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        
        pdf_path = f"tmp/{file_data.get('file_name')}"
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=11)

        pdf.set_auto_page_break(auto=True, margin=15)

        pdf.set_text_color(69, 16, 163)
        pdf.cell(200, 10, txt="PDF Reader - Scriptors", ln=True, align="C")

        pdf.cell(200, 10, txt="Nome do arquivo: " + file_data.get("file_name"), ln=True, align="C")
        pdf.cell(200, 10, txt="Data de upload: " + file_data.get("upload_date"), ln=True, align="C")
        
        pdf.set_text_color(0, 0, 255)
        pdf.cell(200, 10, txt="Link do arquivo: clique aqui!", link=file_data.get("file_url"), ln=True, align="C")

        pdf.set_text_color(0, 0, 0)
        pdf.cell(200, 10, txt="Dados extraídos do arquivo", ln=True, align="C")        
        
        for line in file_data.get("extracted_data").split("\n"):
            pdf.multi_cell(0, 10, line)

        pdf.output(pdf_path)
        
        pdf_url = upload_pdf(UploadFile(file=pdf_path, filename=file_data.get("file_name")+"_response.pdf"))
        
        return JSONResponse(content={"pdf_url": pdf_url}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/user_files/{file_id}")
async def get_user_file(file_id: str):
    try:
        user_file = db.child("user_files").child(file_id).get()
        file_data = user_file.val()
        
        if not file_data:
            return JSONResponse(content={"error": "File not found"}, status_code=404)
        
        upload_date_str = file_data.get("upload_date")
        if upload_date_str:
            upload_date = datetime.strptime(upload_date_str, "%Y-%m-%d %H:%M:%S.%f")
            formatted_date = upload_date.strftime("%d/%m/%Y - %H:%M")
        else:
            formatted_date = "Data não encontrada"
        
        return JSONResponse(content={
            "id": file_id,
            "uploadDate": formatted_date,
            "name": file_data.get("file_name"),
            "link": file_data.get("file_url"),
            "extracted_data": file_data.get("extracted_data")
        }, status_code=200)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

@app.get("/user_files")
async def get_user_files(request: Request):
    try:
        user_id = get_current_user(request)
        user_files = db.child("user_files").get()

        if not user_files.each():
            print("No files found in Firebase.")

        files_list = []
        print(f"User ID: {user_id}")

        for file in user_files.each():
            file_data = file.val()
            print(f"Checking file: {file_data}")

            if file_data.get("user_id") == user_id:
                upload_date_str = file_data.get("upload_date")
                if upload_date_str:
                    upload_date = datetime.strptime(
                        upload_date_str, "%Y-%m-%d %H:%M:%S.%f")
                    formatted_date = upload_date.strftime("%d/%m/%Y - %H:%M")
                else:
                    formatted_date = "Data não encontrada"

                files_list.append({
                    "id": file.key(),
                    "uploadDate": formatted_date,
                    "name": file_data.get("file_name"),
                    "link": file_data.get("file_url"),
                    "extracted_data": file_data.get("extracted_data")
                })

        print(f"Files list: {files_list}")

        return JSONResponse(content=files_list[::-1], status_code=200)
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)



@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...), query: str = Form(...)):
    
    command = "ollama serve"
    subprocess.Popen(command, shell=True)

    file_type = file.filename.split(".")[-1].lower()
    original_filename = file.filename.rsplit(".", 1)[0]
    file_path = f"tmp/{file.filename}"
    
    try:
        user_id = get_current_user(request)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        if file_type != "pdf":
            pdf_path = f"tmp/{original_filename}.pdf"

            if file_type in ["jpg", "jpeg", "png"]:
                image = Image.open(file_path)
                image.convert('RGB').save(pdf_path)

            elif file_type == "docx":
                docx2pdf_convert(file_path, pdf_path)

            elif file_type == "html":
                pdfkit.from_file(file_path, pdf_path)

            elif file_type == "txt":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                
                with open(file_path, 'r') as txt_file:
                    for line in txt_file:
                        pdf.cell(200, 10, txt=line, ln=True)
                
                pdf.output(pdf_path)

            else:
                return JSONResponse(content={"error": f"Unsupported file type: {file_type}"}, status_code=400)

            file_path = pdf_path

        with open(file_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            pdf_upload_file = StarletteUploadFile(file=io.BytesIO(pdf_bytes), filename=f"{original_filename}.pdf")

        final_response = await read_pdf_reader(file=file_path, query=query)
        
        pdf_url = upload_pdf(pdf_upload_file)
        
        file_metadata = {
            "user_id": user_id,
            "upload_date": str(datetime.now()),
            "file_name": file.filename,
            "extracted_data": final_response,
            "file_url": pdf_url
        }

        response = db.child("user_files").push(file_metadata)
        file_key = response['name']
        
        file_metadata['file_id'] = file_key

        if os.path.exists(file_path):
            os.remove(file_path)
            
        return JSONResponse(content={"file_id": file_key,
                                     "response": final_response, "pdf_url": pdf_url}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)

class OllamaAssistant():
    def __init__(self):
        self.history = []
    def ask(self, user_input):
        print(user_input)
        self.history.append({"role": "user", "content": user_input})
    def answer(self):
        client = Client(host='http://localhost:11434')
        answer = client.chat(model='llama3', messages=self.history)
        self.history.append(answer['message'])
        return answer['message']['content']

def load_split_pdf(pdf_file):
    pdf_loader = PdfReader(pdf_file)
    pdf_text = ""
    for page_num in range(len(pdf_loader.pages)):
        pdf_page = pdf_loader.pages[page_num]
        pdf_text += pdf_page.extract_text()
    return pdf_text

def split_text_using_RCTS(pdf_text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=8192,
        chunk_overlap=64
    )
    split_texts = text_splitter.split_text(pdf_text)
    paragraphs = []
    for text in split_texts:
        paragraphs.extend(text.split('\n')) 
    return paragraphs

def initialize_sentence_transformer():
    return embeddings_model

def encode_each_paragraph(paragraphs, embeddings):
    responses = []
    for paragraph in paragraphs:
        response = embeddings.encode([paragraph], convert_to_tensor=True)
        responses.append((paragraph, response))
    return responses

def choose_most_relevant_sentence(embeddings, responses, query):
    answers = []

    for paragraph, response in responses:
        answers.append(paragraph)
        
    answer = "\n".join(answers)
    return answer

def query_the_llm(answer, llm_model, query):
    prompt_message = query + "\n" + answer 
    final_response = llm_model.generate(prompt=prompt_message)
    return final_response

async def read_pdf_reader(file: str, query: str = "Retorne os seguinte itens: CNPJs, Valores numéricos que mensuram valor monetário, Empresa Contratante, Empresa Contratada, Vigência do contrato."):
    
    os.system("ollama run llama3")
    
    assistant = OllamaAssistant()
    pdf_text = load_split_pdf(file)
    paragraphs = split_text_using_RCTS(pdf_text)
    embeddings = initialize_sentence_transformer()
    responses = encode_each_paragraph(paragraphs=paragraphs, embeddings=embeddings)
    answer = choose_most_relevant_sentence(embeddings=embeddings, responses=responses, query=query)

    assistant.ask(answer + "\n" + query)
    final_response = assistant.answer()

    os.system("kill $(pgrep ollama)")
    
    return final_response

embeddings_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

@app.post("/signup")
async def create_an_account(user_data: SignUpSchema):
    email = user_data.email
    password = user_data.password
    
    try:
        user = auth.create_user(email=email, password=password)
        return JSONResponse(content={"message": f"User account created successfully for user {user.uid}."}, status_code=201)

    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail=f"User account already exists {email}"
        )

@app.post("/ping")
async def validate_token(request: Request):
    headers = request.headers
    jwt = headers.get("Authorization")
    
    user = auth.verify_id_token(jwt)
    
    return user

@app.get("/")
def read_root():
    return {"message": "Server is running"}
