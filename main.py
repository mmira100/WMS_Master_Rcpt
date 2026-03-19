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
import smtplib
from email.message import EmailMessage

app = FastAPI()



# Modelo para los datos que recibiremos en el POST
class Item(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float

#Veririfica que existan el folder para guardar la info recibida
folder_name = "wms_payloads"
#Comprobar si no existe la carpeta , crearla
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

#Veririfica que existan el folder para guardar la info recibida
folder_excel = "excel"
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
    load_dotenv()
    SECRET_KEY = os.getenv("SECRET_KEY")
    # Validar el token
    if x_token_key != SECRET_KEY:
        raise HTTPException(status_code=403, detail="Token no válido o inexistente")
    
   

    # 1. Leer el stream de bytes
    raw_body = await request.body()
    
    data = json.loads(raw_body)
    trknum =  data["MASTER_RCPT_COMPLETE_OUB_IFD"]["RCV_TRLR_OUB_IFD"]["MASTER_RCPT_OUB_IFD"]["TRKNUM"]
    trknum_limpio = trknum.replace("/", "_")
    print(trknum_limpio)
    # 2. Parsear manualmente
    try:
        data      = json.loads(raw_body)
        fecha_str = datetime.now().strftime("%Y%m%d%H%M%S")
        archivo   = folder_name+"/"+trknum_limpio+'_'+fecha_str+".json"
        
        with open(archivo, "w", encoding="utf-8") as f:
             json.dump(data, f, indent=4, ensure_ascii=False)
###asincrono###   
        
        dataF = [("Cliente",	"Número de Entrada","Proveedor","No. Factura","No. De producto","SKU","Cajas Solicitadas a Recibir","Flips Solicitados a Recibir","Cajas Recibidas","Flips Recibidos","Estilo",	"Batch","Pack Code","Fecha de caducidad","Contenedor","Estado de Calidad","Referencia"),
                ]   
              
        lineas = data["MASTER_RCPT_COMPLETE_OUB_IFD"]["RCV_TRLR_OUB_IFD"]["MASTER_RCPT_OUB_IFD"]["RCPT_INVOICE_OUB_IFD"]["RCPT_INVOICE_LINE_OUB_IFD"]  
        SUPNUM = data["MASTER_RCPT_COMPLETE_OUB_IFD"]["RCV_TRLR_OUB_IFD"]["MASTER_RCPT_OUB_IFD"]["RCPT_INVOICE_OUB_IFD"]["SUPNUM"]
        for linea in lineas:
             EXPQTY = linea.get("EXPQTY")
             if EXPQTY != 0:
                load_dotenv()                
                val_env = os.getenv(linea.get("PRTNUM"), "0")
                CAJASEXP = float(val_env)
                print(f"Valor de CAJASEXP: {CAJASEXP}")   

                EXPQTY2 = linea.get("EXPQTY")
                print(f"Valor de EXPQTY2: {EXPQTY2}")   

                CAJASR = float(EXPQTY2)/CAJASEXP
                print(f"Valor de CAJASR: {CAJASR}")   

                PACK_CODE = linea.get("INV_ATTR_STR2")
                print(f"Valor de PACK_CODE: {PACK_CODE}")   
                REFERENCIA = linea.get("INV_ATTR_STR3")
                print(f"Valor de REFERENCIA: {REFERENCIA}")
                PEDIMENTO = linea.get("INV_ATTR_STR4")
                print(f"Valor de PEDIMENTO: {PEDIMENTO}")
              
                ###
                NUM_FACTURA  = linea.get("INV_ATTR_STR5")
                print(f"Valor de NUM_FACTURA: {NUM_FACTURA}")
                EAN  = linea.get("INV_ATTR_STR6")
                print(f"Valor de EAN: {EAN}")
                expire_dte  = linea.get("INV_ATTR_STR7")
                print(f"Valor de expire_dte: {expire_dte}")
             
             if EXPQTY == 0:
                                
                invsln = linea.get("INVSLN")
                print(f"Valor de INVSLN: {invsln}")

                CLIENT_ID = linea.get("CLIENT_ID")
                print(f"Valor de CLIENT_ID: {CLIENT_ID}")
                print(f"Valor de trknum: {trknum}")
                print(f"Valor de SUPNUM: {SUPNUM}")                
                PRTNUM = linea.get("PRTNUM")
                print(f"Valor de PRTNUM: {PRTNUM}")
                QTYCS = 0
                print(f"Valor de QTYCS: {QTYCS}")
                qtyFlips = linea.get("RCVQTY")
                print(f"Valor de Flips: {qtyFlips}")
                
                CAJASRR = float(qtyFlips)/CAJASEXP
                print(f"Valor de CAJASR: {CAJASRR}")   

                LOTNUM = linea.get("LOTNUM")
                print(f"Valor de ESTILO: {LOTNUM}")
                SUP_LOTNUM = linea.get("SUP_LOTNUM")
                print(f"Valor de SUP_LOTNUM: {SUP_LOTNUM}")
                RCVSTS = linea.get("RCVSTS")
                match RCVSTS:                 
                    case 'A':
                        rcvsts ="DISPONIBLE"
                    case 'RESV':
                        rcvsts = "RESERVA"
                    case 'OBSE':
                        rcvsts ="OBSOLETO"
                    case 'EXP':
                        rcvsts ="EXPIRED"
                    case 'RESG':
                        rcvsts ="RESGUARDO"
                print(f"Valor de RCVSTS: { rcvsts }")
         
                nuevos_datos = [(CLIENT_ID, trknum, SUPNUM, NUM_FACTURA, EAN, PRTNUM,CAJASR,EXPQTY2,CAJASRR,qtyFlips,LOTNUM,SUP_LOTNUM,PACK_CODE, expire_dte,PEDIMENTO,rcvsts,REFERENCIA  )
                               ]
                dataF.extend(nuevos_datos)	
                
        #crear el excel        
        excel_book = openpyxl.Workbook()        
        sheet      = excel_book.active
        sheet.title = trknum_limpio
        
        for index, row in enumerate(dataF):
            sheet[f'A{index+1}'] = row[0]
            sheet[f'B{index+1}'] = row[1]
            sheet[f'C{index+1}'] = row[2]
            sheet[f'D{index+1}'] = row[3]
            sheet[f'E{index+1}'] = row[4]
            sheet[f'F{index+1}'] = row[5]
            sheet[f'G{index+1}'] = row[6]
            sheet[f'H{index+1}'] = row[7]
            sheet[f'I{index+1}'] = row[8]
            sheet[f'J{index+1}'] = row[9]
            sheet[f'K{index+1}'] = row[10]
            sheet[f'L{index+1}'] = row[11]
            sheet[f'M{index+1}'] = row[12]
            sheet[f'N{index+1}'] = row[13]
            sheet[f'N{index+1}'] = row[14]
            sheet[f'N{index+1}'] = row[15]
            sheet[f'N{index+1}'] = row[15]
         
            
          
        header_fill = PatternFill(start_color='DCE6F1', end_color='DCE6F1', fill_type='solid')
        header_font = Font(bold=True)
        
        #Aplicar a la primera fila (ajusta el rango según tus columnas, ej: A a N)
        for cell in sheet[1]: 
           cell.fill = header_fill
           cell.font = header_font
        
        #Definir cómo será la línea del borde (delgada y negra)
        thin_border = Border(
                             left=Side(style='thin'),  
                             right=Side(style='thin'), 
                             top=Side(style='thin'), 
                             bottom=Side(style='thin')
                             )
        #Recorrer todas las celdas que tienen datos y aplicar el borde
        for row in sheet.iter_rows(min_row=1, max_row=sheet.max_row, min_col=1, max_col=sheet.max_column):
          for cell in row:
             cell.border = thin_border



        #Recorrer cada columna de la hoja
        for col in sheet.columns:
             max_length = 0
             column_letter = get_column_letter(col[0].column) # Obtiene 'A', 'B', etc.

             #Medir el texto más largo en esa columna
             for cell in col:
                try:
                   if cell.value:
                    # Comparamos la longitud actual con la del valor de la celda
                     if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
    
             #Ajustar el ancho (agregamos 2 unidades de margen)
             adjusted_width = (max_length + 2)
             sheet.column_dimensions[column_letter].width = adjusted_width


        excel_book.save(f"{folder_excel}\{trknum_limpio}.xlsx")

        #Enviar correo
        #login credential
        load_dotenv()    
        imap_server =os.getenv("imap_server")
        impap_port  =os.getenv("impap_port")
        username= os.getenv("username2")
        password= os.getenv("password2")
        print(imap_server)
        print(impap_port)
        print(username)
        print(password)

        #Conexion al servidor de correo
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(username,password)

        
        original_subject = "-Confirmación de Recibo Envío entrante:"+trknum
        original_to    = "Olga.Bohorquez@jti.com"
        original_cc      = "garcia.miguel@dickalogistics.com.mx,Liliana.Cervantes@jti.com,Arturo.Olivares@jti.com,Uriel.Sanchez@jti.com,c06.jefeoperaciones@dickalogistics.com.mx,Sup.tepotzotlan@dickalogistics.com.mx,sup.tepotzotlan@dickalogistics.com.mx,hernandez.guadalupe@dickalogistics.com.mx,galindo.jose@dickalogistics.com.mx"
        




        
        #Crear el nuevo mensaje de respuesta
        reply = EmailMessage()
        reply['Subject'] = f"{original_subject}"
        reply['To'] = original_to  # Respondemos al remitente
        reply['Cc'] = original_cc
       
        reply['From'] = "dickainterfaces@gmail.com"
        msg_compartido = f"Saludos,\n\nSe comparte la confirmación de recibido para el  envío entrante identificado como:{trknum}\n\nFavor de revisar el excel adjunto con los detalles de cada línea recibida."
        reply.set_content(f"{msg_compartido} \n\nMuchas Gracias.\n\nBuen día.")

        # Ruta de tu archivo Excel
        nombre_archivo = f"{folder_excel}\{trknum_limpio}.xlsx" 
        archivo        = f"Confirmación {trknum_limpio}.xlsx" 
        # 1. Leer el archivo en binario
        with open(nombre_archivo, 'rb') as f:
           file_data = f.read()
        # Para Excel suele ser: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
        maintype, subtype = "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        reply.add_attachment(file_data, maintype=maintype, subtype=subtype,filename=archivo)  
	    
        #Enviar la respuesta
        try:
          with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
             smtp.login(username,password)
             smtp.send_message(reply)             
             print(f"Respuesta enviada a {original_to }")
        except Exception as e:
             print(f"Error al responder: {e}")  
        
        ###asincrono###
        
        
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
