from fastapi_mail import ConnectionConfig  
conf = ConnectionConfig(MAIL_USERNAME='', MAIL_PASSWORD='', MAIL_FROM='test@test.com', MAIL_PORT=587, MAIL_SERVER='', MAIL_STARTTLS=True, MAIL_SSL_TLS=False, USE_CREDENTIALS=True, VALIDATE_CERTS=True)  
