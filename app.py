import setting
import requests
from db_conection.db_conf import Database
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi_mail import FastMail, ConnectionConfig, MessageSchema
import secrets
import string

app = FastAPI()

# Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates/")

db = Database(
    setting.DB_HOST,
    setting.DB_NAME,
    setting.DB_USER,
    setting.DB_PASSWORD
)

conf = ConnectionConfig(
    MAIL_USERNAME=setting.MAIL_USERNAME,
    MAIL_PASSWORD=setting.MAIL_PASSWORD,
    MAIL_FROM=setting.MAIL_FROM,
    MAIL_PORT=setting.MAIL_PORT,
    MAIL_SERVER=setting.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

@app.get("/recovery")
async def form_recovery_get(request: Request):
    return templates.TemplateResponse("recovery_template.html", {"request": request})

@app.post("/recovery")
async def form_recovery_post(request: Request, email: str = Form(...)):
    exist = db.checkEmail(email)
    if exist:
        user=db.getUser(email)
        password=generate_password()
        response=requests.post(f"{setting.URL_COMPANY}/api/auth/ResetPassword",json={"username":str(user[0]),"newPassword":password})
        if response.status_code == 200:
            message = await sendigMail(password, email,str(user[0]))
            return {"message": message}
        else:
            return {"message": "Error when attempting to change the password."}
    else:
        return templates.TemplateResponse("recovery_template.html", {"request": request,"error_message": "Invalid email"})

async def sendigMail(password, email,user):
    fm = FastMail(conf)
    with open("templates/email_template.html", "r", encoding='utf-8') as f:
        template = f.read()

    body = template.replace('{{password}}', password).replace('{{user}}',user)

    message = MessageSchema(
        subject="Clinic App Notification",
        recipients=[email],
        body=body,
        subtype="html"
    )

    try:
        await fm.send_message(message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return "El correo electrónico ha sido enviado exitosamente"

def generate_password(length=8):
    alphabet = string.ascii_letters + string.digits + "*.,"
    while True:
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        if (any(c.islower() for c in password)
                and any(c.isupper() for c in password)
                and any(c.isdigit() for c in password)
                and any(c in "*.," for c in password)):
            return password

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='localhost', port=8000)
