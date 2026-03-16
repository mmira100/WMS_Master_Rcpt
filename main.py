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

app = FastAPI()

# Definimos una clave secreta válida
SECRET_KEY = "mi-clave-super-segura-123"

# Modelo para los datos que recibiremos en el POST
class Item(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

#Veririfica que existan el folder para guardar la info recibida
folder_name = "bpo_payloads"
#Comprobar si no existe la carpeta , crearla
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

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

payload = {
    'grant_type': 'client_credentials',
    'client_id': 'addf3efe-1124-443c-aa9d-cb57e8f841a4',
    'client_secret': 'Jh~8Q~szegYVOjEiTIw1oK-pc2cjv3MjB_L6HaS~',
    'scope': 'https://blueyonderus.onmicrosoft.com/69adb04d-658f-4b86-a659-67fe0f23bd1f/.default'
}



headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

estatus = "Recibido"

@app.post("/test/bpo", status_code=status.HTTP_202_ACCEPTED)
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
    # Validar el token
    if x_token_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Token no válido o inexistente")
    
   

    # 1. Leer el stream de bytes
    raw_body = await request.body()
    # 2. Parsear manualmente
    try:
        data      = json.loads(raw_body)
        fecha_str = datetime.now().strftime("%Y%m%d%H%M%S")
        archivo   = folder_name+"/"+fecha_str+".json"

        #with open("bpo_payloads/ejemplo12.json", "w", encoding="utf-8") as f:
        with open(archivo, "w", encoding="utf-8") as f:
             json.dump(data, f, indent=4, ensure_ascii=False)
        resultado = {"Solicitud aceptada e información recibida, muchas gracias BPO.": fecha_str}
        return JSONResponse(
           status_code=200   , 
           content=resultado
            )
    
        #return {access_token }
    except Exception:
        return {"error": "Formato inválido"}, 400
     
    
                       
if __name__ == "__main__":
   import uvicorn
   port= int(os.getenv("PORT",8000))
   uvicorn.run(app, host="0.0.0.0", port=port)
