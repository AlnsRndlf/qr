from fastapi import FastAPI
from fastapi.responses import JSONResponse
import cv2
import time

app = FastAPI(title="API Lector de QR con Webcam")

# Inicializamos el detector de OpenCV
detector = cv2.QRCodeDetector()

@app.get("/leer-qr/")
async def leer_qr_camara():
    try:
        # 1. Encender la cámara web principal (0)
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return JSONResponse(status_code=500, content={"error": "No se pudo acceder a la webcam."})

        # Damos un límite de 10 segundos para encontrar el QR y que la API no se quede pegada
        tiempo_limite = 10 
        tiempo_inicio = time.time()
        texto_encontrado = None

        while (time.time() - tiempo_inicio) < tiempo_limite:
            exito, frame = cap.read()
            if not exito:
                continue

            # Mostramos la ventana para que sepas a dónde estás apuntando
            cv2.imshow("Apunta el QR a la camara... (10s max)", frame)
            cv2.waitKey(1) # Necesario para que OpenCV actualice la ventana de video

            # 2. Decodificar el QR en tiempo real
            data, bbox, _ = detector.detectAndDecode(frame)
            
            # Si encuentra texto, lo guardamos y rompemos el ciclo
            if data:
                texto_encontrado = data
                break

        # 3. Limpieza: Apagar la cámara y destruir la ventana de video
        cap.release()
        cv2.destroyAllWindows()

        # 4. Devolver la respuesta
        if texto_encontrado:
            return {"qr_data": [texto_encontrado]}
        else:
            return JSONResponse(
                status_code=400, 
                content={"error": "Tiempo agotado. No se detectó ningún código QR."}
            )

    except Exception as e:
        return JSONResponse(
            status_code=500, 
            content={"error": f"Error interno: {str(e)}"}
        )