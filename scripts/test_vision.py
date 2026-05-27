import cv2
from security import JarvisVision
import time

def iniciar_sesion_biometrica():
    vision = JarvisVision()
    cap = cv2.VideoCapture(0)
    print("--- ESCÁNER BIOMÉTRICO ACTIVO ---")
    print("Buscando al Creador...")

    confirmaciones = 0 # Contador para evitar falsos positivos

    while True:
        ret, frame = cap.read()
        if not ret: break

        user = vision.identify_user(frame)
        
        if user == "Creador":
            confirmaciones += 1
            color = (0, 255, 0) # Verde si es usted
        else:
            confirmaciones = 0
            color = (0, 0, 255) # Rojo si es desconocido

        cv2.putText(frame, f"Identidad: {user}", (50, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        cv2.imshow('J.A.R.V.I.S. Vision', frame)

        # Si lo reconoce durante 10 frames seguidos, cerramos el acceso
        if confirmaciones >= 10:
            print("\n[ACCESO CONCEDIDO]")
            # Aquí es donde J.A.R.V.I.S. le hablaría
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    if iniciar_sesion_biometrica():
        print("Bienvenido, Señor David. Iniciando sistemas principales...")