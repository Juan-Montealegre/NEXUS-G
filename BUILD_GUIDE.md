
# 🏗️ JARVIS OS: Guía de Instalación desde Cero (Tauri v2)

Sigue estos pasos en orden estricto para una instalación limpia y exitosa.

## 1. Requisitos de Sistema (Hardware/OS)
Antes de tocar el código, asegúrate de tener instaladas las herramientas de compilación:

1. **Rust**: Descarga e instala desde [rustup.rs](https://rustup.rs/). Selecciona la instalación por defecto (opción 1).
2. **C++ Build Tools**: Durante la instalación de Rust o mediante el instalador de Visual Studio, asegúrate de marcar "Desarrollo para el escritorio con C++".
3. **WebView2**: Windows 10/11 suelen traerlo, si no, descárgalo (Evergreen Bootstrapper).

## 2. Limpieza del Proyecto (The Nuclear Option)
Abre una terminal en la raíz de `jarvis-os` y ejecuta:

```powershell
# Eliminar todo rastro de instalaciones previas
rmdir /s /q node_modules
rmdir /s /q dist
rmdir /s /q src-tauri
```

## 3. Inicialización Limpia de Tauri
En lugar de intentar arreglar la carpeta vieja, vamos a generar una nueva compatible con v2:

```powershell
# Instalar dependencias de Node
npm install

# Inicializar el núcleo de Rust (Tauri v2)
npx tauri init
```

**Al ejecutar `init`, responde así:**
- **App name:** `JarvisOS`
- **Window title:** `JARVIS - Neural Link`
- **Frontend dist:** `../dist`
- **Dev URL:** `http://localhost:3000`
- **Recipe:** `Vite` (o el que uses)

## 4. Aplicar Configuración de JARVIS
Una vez creada la carpeta `src-tauri`, reemplaza el contenido de `tauri.conf.json` con el código proporcionado abajo para activar la transparencia y los permisos de seguridad.

## 5. Primer Lanzamiento
Para probar que el "Neural Link" está activo:

```powershell
npx tauri dev
```

## 6. Compilación del Instalador (.exe)
Cuando estés listo para el despliegue final:

```powershell
npx tauri build
```
