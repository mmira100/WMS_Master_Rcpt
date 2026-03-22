#main.py
from fastapi  import FastAPI , Request, status, Header, HTTPException, Depends
from fastapi.responses import JSONResponse
import requests
import json
import  os
import datetime
from typing import Annotated
from dotenv import load_dotenv
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

app = FastAPI()

with open("ejemplo1.txt", "w") as archivo:
    archivo.write("Este es un archivo de texto creado con Python.")

#Abrir el archivo de configuración para urls y credenciales
from pathlib import Path
ruta_base = Path(__file__).parent 
archivo_ruta = ruta_base / "config.json"
with open(archivo_ruta, 'r') as f:
    data = json.load(f) # Lee y convierte a diccionario en un solo paso
    url_token_wms             = data["items"][0]["url_token_wms"]
    usr_id_wms                = data["items"][0]["usr_id_wms"]
    password_wms              = data["items"][0]["password_wms"]
    url_wms_inventory         = data["items"][0]["url_wms_inventory"]
    url_wms_orderStatus       = data["items"][0]["url_wms_orderStatus"]	
    url_wms_customers         = data["items"][0]["url_wms_customers"]
    url_wms_order             = data["items"][0]["url_wms_order"]
    url_wms_orderLine         = data["items"][0]["url_wms_orderLine"]  

# La API publica de WMS BY que queremos consumir para el token 
url                = url_token_wms

load_dotenv()
token = os.getenv("SECRET_KEY")
#Las credenciales se pasan por RAW 
raw_data = f'{{"usr_id": "{usr_id_wms}", "password": "{password_wms}"}}'
headers = {"Content-Type": "application/json","Authorization": f"Bearer {token}"}

response = requests.post(url, data=raw_data, headers=headers)    
if response.status_code == 200:
   for cookie in response.cookies:
       if cookie.name == "MOCA-WS-SESSIONKEY": 
             v_token =cookie.value
             cookies_wms = {cookie.name:cookie.value}  
             #print(v_token) 

estatus = "Recibido"

security = HTTPBearer()

@app.post("/test/ordercrate")
async def create_order(request: Request,credentials: HTTPAuthorizationCredentials = Depends(security)):
    # El token llega en credentials.credentials
    token = credentials.credentials
    load_dotenv()
    token2 = os.getenv("SECRET_KEY")

    if token != token2:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )
        
    #load_dotenv()
    #SECRET_KEY = os.getenv("SECRET_KEY")
    # Validar el token
    #if x_token_key != SECRET_KEY:
     #   raise HTTPException(status_code=403, detail="Token no válido o inexistente")
    
    #Leer el stream de bytes      
    raw_body = await request.body()    
    data = json.loads(raw_body)
    wh_id  = data["order"][0]["wh_id"]
    ordnum = data["order"][0]["ordnum"]
    client_id = data["order"][0]["client_id"]
    stcust = data["order"][0]["stcust"]
    btcust = stcust
    rtcust = stcust

    # 3. Armar la url de WMS BY para la info de items        
    body_raw =f"""{{
                            "wh_id": "{wh_id}",
                            "ordnum":"{ordnum}",
                            "ordtyp": "C",
                            "client_id": "{client_id}" ,
                            "stcust": "{stcust}",
                            "btcust ": "{btcust}" ,   
                            "rtcust": "{rtcust}"        
                           }}"""       
   # print(body_raw)

    response_order = requests.post(url_wms_order, data=body_raw, headers=headers  , cookies=cookies_wms)
    dataj = response_order.json()
    mensaje =""

    loc_procesadas    = []
    loc_procesadas_OK = []
    vcuantos  = 0
    vcuantosL = 1      

    if response_order.status_code == 200:     
        
        b_inserta = 1
        data2 = data["orderlines"]
        for line in data2:
            ordlin        = line["ordlin"]
            invsts        = line["invsts"]
            client_id     = line["client_id"]    
            prt_client_id = line["prt_client_id"]             
            ordqty        = line["ordqty"]             
            prtnum        = line["prtnum"]             
            lotnum        = line["lotnum"]             
            expire_dte    = line["expire_dte"]             
            ordsln = 1
            body_raw =f"""{{
                            "wh_id": "{wh_id}",
                             "ordsln": "1",
                             "ordnum": "{ordnum}",
                             "ordlin": "{ordlin}",
                             "ordsln": "{ordsln}",
                             "invsts": "{invsts}",                                      
                             "client_id": "{client_id}",                                      
                             "ordqty": "{ordqty}",                                       
                             "prtnum": "{prtnum}",
                             "prt_client_id": "{prt_client_id}",
                             "lotnum": "{lotnum}",
                             "expdte": "{expire_dte}",
                             "ordtyp": "C"                                       
                                     }}"""
           
            #print(body_raw)
            
            response_orderLine = requests.post(url_wms_orderLine,  headers=headers  , data=body_raw, cookies=cookies_wms)                              
            dataOLD = response_orderLine.json()  
            #print(dataOLD) 
                     
            if response_orderLine.status_code != 200:                            
                 for item in dataOLD["errors"]:
                             nuevo_item = { "ordnum"             : ordnum,
                                             "client_id"         : client_id ,
                                             "ordlin"            : ordlin,
                                             "Procesado"         : "false" ,
                                             "prtnum"            : prtnum,
                                             "ordqty"            : ordqty ,
                                             "errorCode"         : item["errorCode"],
                                             "userMessage"       : item["userMessage"]                             
                                            }
                             loc_procesadas.append(nuevo_item)    
            else:
                           #respuesta correcta  
                           nuevo_item_ok = {  "ordnum"            : ordnum,
                                              "client_id"         : client_id ,
                                              "ordlin"            : ordlin,
                                              "Procesado"         : "true" ,
                                              "prtnum"            : prtnum,                                   
                                              "ordqty"            : ordqty ,                                              
                                              "lotnum"            : lotnum,                                                                                
                                              "expire_dte"        : expire_dte                                               
                                    }
                           loc_procesadas_OK.append(nuevo_item_ok)                  

            resultado = { "Order": ordnum,
                          "Lines_Ok": loc_procesadas_OK,
                           "Lines_Error": loc_procesadas
}
    else:    
        b_inserta = 0
        mensaje = dataj['errors'][0]['userMessage']
        resultado = mensaje
        
    
    
  
    return JSONResponse(
        status_code=response_order.status_code   , 
        content=resultado
    )
                       
if __name__ == "__main__":
   import uvicorn
   port= int(os.getenv("PORT",8000))
   uvicorn.run(app, host="0.0.0.0", port=port)
