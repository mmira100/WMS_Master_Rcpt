#main.py
from fastapi import FastAPI , Request, status, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import requests
import json
import  os
from typing import Annotated
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv
import openpyxl 
import email 
import imaplib
import smtplib
from email.message import EmailMessage
from openpyxl.styles import PatternFill, Font
from openpyxl.styles import Border, Side
from openpyxl.utils import get_column_letter

app = FastAPI()



# Modelo para los datos que recibiremos en el POST
class Item(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

#Veririfica que existan el folder para guardar la info recibida
folder_name = "wms_payloads2"
#Comprobar si no existe la carpeta , crearla
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

#Veririfica que existan el folder para guardar la info recibida
folder_excel = "excel2"
#Comprobar si no existe la carpeta , crearla
if not os.path.exists(folder_excel):
    os.makedirs(folder_excel)

#Abrir el archivo de configuración para urls y credenciales
from pathlib import Path
ruta_base = Path(__file__).parent 
archivo_ruta = ruta_base / "config.json"
with open(archivo_ruta, 'r') as f:
    data = json.load(f) # Lee y convierte a diccionario en un solo paso
    url_token_tms   = data["items"][0]["url_token_tms"]
    c_id            = data["items"][0]["c_id"]
    c_sec           = data["items"][0]["c_sec"]
    scope           = data["items"][0]["scope"]

#Arma la url del TMS BY token
url = url_token_tms

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

estatus = "Recibido"

@app.post("/test/wms/rc", status_code=status.HTTP_202_ACCEPTED)
async def get_json_raw(request: Request,x_token_key: str = Header(...)):
    #Consumir la API externa TMS BY token usando requests    
    #response = requests.post(url, data=payload, headers=headers)
    #Procesar y obtener el token de TMS BY
    #if response.status_code == 200:
     #   token_data = response.json()
      #  access_token = token_data.get('access_token')
    
    """
    Endpoint POST que requiere 'x-token-key' en el encabezado.
    """
    #load_dotenv()
    #SECRET_KEY = os.getenv("SECRET_KEY")
    SECRET_KEY = "e1d0a6ab396345b699455c953dbb165c"
    # Validar el token
    if x_token_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Token no válido o inexistente")
    
   

    # 1. Leer el stream de bytes
    raw_body = await request.body()
    
    data = json.loads(raw_body)
    trknum =  data["MASTER_RCPT_COMPLETE_OUB_IFD"]["RCV_TRLR_OUB_IFD"]["MASTER_RCPT_OUB_IFD"]["TRKNUM"]
    print(trknum)
    # 2. Parsear manualmente
    try:
        data      = json.loads(raw_body)
        fecha_str = datetime.now().strftime("%Y%m%d%H%M%S")
        archivo   = folder_name+"/"+trknum+'_'+fecha_str+".json"
        #with open("bpo_payloads/ejemplo12.json", "w", encoding="utf-8") as f:
        with open(archivo, "w", encoding="utf-8") as f:
             json.dump(data, f, indent=4, ensure_ascii=False)

        print(trknum ) 
        
        resultado = {"Confirmación recibida,MASTER_RCPT_COMPLETE_OUB_IFD, muchas gracias.": trknum }
        return JSONResponse(
           status_code=200   , 
           content=resultado
            )
    
        #return {access_token }
    except Exception as e:
         return {"error": "Formato inválido", "detalle": str(e)}, 400
     
    
                       
if __name__ == "__main__":
   import uvicorn
   port= int(os.getenv("PORT",8000))
   uvicorn.run(app, host="0.0.0.0", port=port)
