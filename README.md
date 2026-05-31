# SIGDEM-ML Backend

## Sistema Inteligente de Gestión Documental, Expedientes y Selección de Personal mediante Machine Learning

Backend desarrollado para el proyecto **SIGDEM-ML**, orientado a la **Municipalidad Provincial de Yau**, con el objetivo de automatizar la gestión de trámites administrativos, documentos, expedientes, notificaciones, reportes y procesos de selección de currículos mediante técnicas de Machine Learning y NLP.

Este repositorio contiene únicamente el **backend** del sistema. Está desarrollado con **FastAPI**, **PostgreSQL**, **SQLAlchemy**, **JWT**, **Machine Learning con Random Forest**, **OCR para documentos**, **NLP para análisis de CVs**, envío de correos SMTP y generación de reportes en PDF.

---

## Autor

**Eduard Fabrizio De La Cruz Alvarez**

---

## Nombre del proyecto

**SIGDEM-ML**

**Sistema Inteligente de Gestión Documental, Expedientes y Selección de Personal mediante Machine Learning**

---

## Descripción general del proyecto

La Municipalidad Provincial de Yau presenta problemas en la gestión manual de trámites administrativos, como tiempos de espera elevados, errores en el procesamiento, falta de seguimiento, poca transparencia y ausencia de herramientas tecnológicas para analizar información.

SIGDEM-ML propone una solución backend que permite:

- Registrar y gestionar trámites municipales.
- Asignar analistas responsables.
- Cambiar estados del trámite.
- Mantener historial de acciones.
- Priorizar trámites usando Machine Learning.
- Subir y gestionar documentos.
- Extraer texto de documentos mediante OCR.
- Notificar automáticamente al ciudadano por correo.
- Gestionar convocatorias laborales.
- Subir y analizar CVs.
- Comparar CVs con convocatorias usando NLP.
- Generar dashboard administrativo.
- Generar reportes JSON y PDF.
- Proteger endpoints mediante autenticación JWT y roles.

---

## Tecnologías utilizadas

- Python
- FastAPI
- Uvicorn
- PostgreSQL
- SQLAlchemy
- Pydantic
- JWT
- Passlib
- Bcrypt
- Scikit-learn
- Pandas
- NumPy
- Joblib
- PyMuPDF
- ReportLab
- SMTP Gmail
- Python Multipart

---

## Arquitectura general

El backend está organizado por módulos funcionales. Cada módulo contiene, según corresponda:

- `model.py`: modelos de base de datos.
- `schema.py`: validaciones y respuestas Pydantic.
- `service.py`: lógica de negocio.
- `routes.py`: endpoints FastAPI.

Estructura principal:

```text
sigdem-ml-backend/
├── app/
│   ├── database/
│   │   ├── __init__.py
│   │   └── connection.py
│   ├── modules/
│   │   ├── auth/
│   │   ├── users/
│   │   ├── tramites/
│   │   ├── documents/
│   │   ├── ml/
│   │   ├── hr/
│   │   ├── cvs/
│   │   ├── dashboard/
│   │   ├── notifications/
│   │   └── reports/
│   ├── utils/
│   │   ├── roles.py
│   │   └── security.py
│   ├── config.py
│   └── main.py
├── uploads/
│   ├── documents/
│   ├── cvs/
│   └── reports/
├── ml_models/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Requisitos previos

Antes de ejecutar el proyecto se necesita tener instalado:

- Python 3.11 o superior.
- PostgreSQL.
- Git.
- Visual Studio Code o editor similar.
- Postman para probar endpoints.

---

## Instalación del proyecto

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd sigdem-ml-backend
```

---

### 2. Crear entorno virtual

En Windows:

```bash
python -m venv venv
```

Activar entorno virtual:

```bash
venv\Scripts\activate
```

En Linux o Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si se agregan nuevas dependencias durante el desarrollo:

```bash
pip freeze > requirements.txt
```

---

### 4. Configurar variables de entorno

Crear un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/sigdem_ml_db

SECRET_KEY=sigdem_ml_secret_key_2026
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
SMTP_FROM_EMAIL=tu_correo@gmail.com
SMTP_USE_TLS=true
```

Importante:

- `DATABASE_URL` debe apuntar a tu base de datos PostgreSQL.
- `SMTP_PASSWORD` debe ser una contraseña de aplicación de Gmail.
- El archivo `.env` no debe subirse a GitHub.

---

### 5. Crear base de datos en PostgreSQL

Desde pgAdmin o consola SQL, crear la base de datos:

```sql
CREATE DATABASE sigdem_ml_db;
```

Las tablas se crean automáticamente al levantar el servidor si el proyecto usa `Base.metadata.create_all()` en `main.py`.

---

### 6. Ejecutar el servidor

```bash
uvicorn app.main:app --reload
```

Servidor disponible en:

```text
http://127.0.0.1:8000
```

Documentación Swagger:

```text
http://127.0.0.1:8000/docs
```

---

## Archivo `.gitignore` recomendado

```gitignore
venv/
__pycache__/
*.pyc
.env

uploads/
ml_models/

*.log
.DS_Store
.vscode/
```

---

# Módulos del sistema

---

## 1. Módulo Auth

Este módulo gestiona autenticación, generación de tokens, refresh token, cierre de sesión y perfil del usuario autenticado.

Incluye:

- Registro del administrador inicial.
- Login.
- Access token.
- Refresh token.
- Logout con blacklist.
- Perfil autenticado.
- Bloqueo de usuarios inactivos.

---

### Registrar administrador inicial

```http
POST /api/auth/register-admin
```

Body:

```json
{
  "nombre": "Administrador Municipal",
  "correo": "admin@muni.gob.pe",
  "password": "123456",
  "rol": "ADMIN"
}
```

Respuesta esperada:

```json
{
  "id": 1,
  "nombre": "Administrador Municipal",
  "correo": "admin@muni.gob.pe",
  "rol": "ADMIN",
  "is_active": true,
  "created_at": "2026-05-31T05:14:39.160351"
}
```

Este endpoint solo se usa una vez. Si ya existe un usuario, no permitirá crear otro administrador inicial.

---

### Login

```http
POST /api/auth/login
```

Body:

```json
{
  "correo": "admin@muni.gob.pe",
  "password": "123456"
}
```

Respuesta:

```json
{
  "access_token": "TOKEN_ACCESS",
  "refresh_token": "TOKEN_REFRESH",
  "token_type": "bearer"
}
```

---

### Refresh token

```http
POST /api/auth/refresh-token
```

Body:

```json
{
  "refresh_token": "TOKEN_REFRESH"
}
```

Respuesta:

```json
{
  "access_token": "NUEVO_ACCESS_TOKEN",
  "refresh_token": "NUEVO_REFRESH_TOKEN",
  "token_type": "bearer"
}
```

---

### Logout

```http
POST /api/auth/logout
```

Authorization:

```text
Bearer ACCESS_TOKEN
```

Body:

```json
{
  "refresh_token": "TOKEN_REFRESH"
}
```

Respuesta:

```json
{
  "message": "Sesión cerrada correctamente"
}
```

Este endpoint invalida tanto el access token como el refresh token.

---

### Perfil del usuario autenticado

```http
GET /api/auth/profile
```

Authorization:

```text
Bearer ACCESS_TOKEN
```

Respuesta:

```json
{
  "id": 1,
  "nombre": "Administrador Municipal",
  "correo": "admin@muni.gob.pe",
  "rol": "ADMIN",
  "is_active": true,
  "created_at": "2026-05-31T05:14:39.160351"
}
```

---

## 2. Módulo Users

Este módulo permite administrar usuarios internos del sistema.

Roles disponibles:

```text
ADMIN
RECEPCIONISTA
ANALISTA
RRHH
```

---

### Listar usuarios

```http
GET /api/users/
```

Authorization:

```text
Bearer ACCESS_TOKEN
```

Respuesta:

```json
[
  {
    "id": 1,
    "nombre": "Administrador Municipal",
    "correo": "admin@muni.gob.pe",
    "rol": "ADMIN",
    "is_active": true,
    "created_at": "2026-05-31T05:14:39.160351"
  }
]
```

---

### Crear usuario

```http
POST /api/users/
```

Authorization:

```text
Bearer ACCESS_TOKEN
```

Body:

```json
{
  "nombre": "Carlos Analista",
  "correo": "analista@muni.gob.pe",
  "password": "123456",
  "rol": "ANALISTA"
}
```

Respuesta:

```json
{
  "id": 3,
  "nombre": "Carlos Analista",
  "correo": "analista@muni.gob.pe",
  "rol": "ANALISTA",
  "is_active": true,
  "created_at": "2026-05-31T05:38:48.007153"
}
```

---

### Ver detalle de usuario

```http
GET /api/users/{user_id}
```

Ejemplo:

```http
GET /api/users/3
```

---

### Editar usuario

```http
PUT /api/users/{user_id}
```

Body:

```json
{
  "nombre": "Carlos Analista Senior",
  "correo": "analista@muni.gob.pe",
  "rol": "ANALISTA",
  "is_active": true
}
```

---

### Desactivar usuario

```http
PATCH /api/users/{user_id}/deactivate
```

Ejemplo:

```http
PATCH /api/users/2/deactivate
```

Respuesta:

```json
{
  "id": 2,
  "nombre": "María Recepcionista",
  "correo": "recepcion@muni.gob.pe",
  "rol": "RECEPCIONISTA",
  "is_active": false,
  "created_at": "2026-05-31T05:38:24.182924"
}
```

---

### Activar usuario

```http
PATCH /api/users/{user_id}/activate
```

Ejemplo:

```http
PATCH /api/users/2/activate
```

---

### Eliminar usuario

```http
DELETE /api/users/{user_id}
```

Respuesta:

```json
{
  "message": "Usuario eliminado correctamente"
}
```

---

## 3. Módulo Trámites

Este módulo gestiona trámites administrativos municipales.

Estados disponibles:

```text
REGISTRADO
EN_REVISION
OBSERVADO
APROBADO
RECHAZADO
FINALIZADO
```

Prioridades disponibles:

```text
BAJA
MEDIA
ALTA
CRITICA
```

---

### Crear trámite

```http
POST /api/tramites/
```

Body:

```json
{
  "tipo_tramite": "Licencia de Funcionamiento",
  "descripcion": "Solicitud para apertura de local comercial en el distrito.",
  "area_responsable": "Desarrollo Económico",
  "correo_solicitante": "ciudadano@gmail.com"
}
```

Respuesta:

```json
{
  "id": 1,
  "codigo": "TRM-000001",
  "tipo_tramite": "Licencia de Funcionamiento",
  "descripcion": "Solicitud para apertura de local comercial en el distrito.",
  "area_responsable": "Desarrollo Económico",
  "correo_solicitante": "ciudadano@gmail.com",
  "estado": "REGISTRADO",
  "prioridad": "MEDIA",
  "recepcionista_id": 1,
  "analista_id": null,
  "fecha_registro": "2026-05-31T05:54:05.165045",
  "fecha_actualizacion": "2026-05-31T05:54:05.165050"
}
```

---

### Listar trámites

```http
GET /api/tramites/
```

Filtros opcionales:

```http
GET /api/tramites/?estado=EN_REVISION
GET /api/tramites/?prioridad=MEDIA
GET /api/tramites/?area=Desarrollo
```

---

### Ver detalle de trámite

```http
GET /api/tramites/{tramite_id}
```

Ejemplo:

```http
GET /api/tramites/1
```

---

### Editar trámite

```http
PUT /api/tramites/{tramite_id}
```

Body:

```json
{
  "tipo_tramite": "Licencia de Funcionamiento Actualizada",
  "descripcion": "Solicitud actualizada.",
  "area_responsable": "Desarrollo Económico",
  "correo_solicitante": "ciudadano@gmail.com",
  "prioridad": "ALTA"
}
```

---

### Cambiar estado del trámite

```http
PATCH /api/tramites/{tramite_id}/status
```

Body:

```json
{
  "estado": "APROBADO",
  "comentario": "El trámite fue aprobado correctamente por el área responsable."
}
```

Este endpoint cambia el estado del trámite y envía una notificación automática al correo del solicitante si existe `correo_solicitante`.

---

### Asignar analista

```http
PATCH /api/tramites/{tramite_id}/assign
```

Body:

```json
{
  "analista_id": 3,
  "comentario": "Asignado al analista responsable del área."
}
```

Solo permite asignar usuarios con rol `ANALISTA`.

---

### Ver historial del trámite

```http
GET /api/tramites/{tramite_id}/history
```

Respuesta:

```json
[
  {
    "id": 18,
    "tramite_id": 1,
    "usuario_id": 1,
    "accion": "NOTIFICACION_AUTOMATICA_ENVIADA",
    "estado_anterior": null,
    "estado_nuevo": null,
    "comentario": "Se notificó automáticamente al correo ciudadano@gmail.com",
    "fecha": "2026-05-31T08:37:36.089551"
  }
]
```

---

## 4. Módulo Machine Learning para Trámites

Este módulo usa **Random Forest Classifier** para priorizar trámites.

---

### Entrenar modelo

```http
POST /api/ml/tramites/train
```

Respuesta:

```json
{
  "message": "Modelo Random Forest entrenado correctamente",
  "accuracy": 0.6,
  "total_samples": 20
}
```

---

### Ver métricas del modelo

```http
GET /api/ml/tramites/metrics
```

Respuesta:

```json
{
  "model_name": "tramite_priority_rf",
  "algorithm": "Random Forest Classifier",
  "accuracy": 0.6,
  "total_samples": 20,
  "labels": [
    "ALTA",
    "BAJA",
    "CRITICA",
    "MEDIA"
  ]
}
```

---

### Clasificar prioridad manualmente

```http
POST /api/ml/tramites/classify
```

Body:

```json
{
  "tipo_tramite": "Denuncia por riesgo estructural",
  "area_responsable": "Defensa Civil",
  "dias_espera": 1,
  "cantidad_documentos": 2,
  "tiene_observaciones": false,
  "es_urgente": true
}
```

Respuesta:

```json
{
  "prioridad": "CRITICA",
  "confidence": 0.8556
}
```

---

### Predecir prioridad de trámite existente

```http
POST /api/ml/tramites/{tramite_id}/predict
```

Ejemplo:

```http
POST /api/ml/tramites/1/predict
```

Respuesta:

```json
{
  "tramite_id": 1,
  "codigo": "TRM-000001",
  "prioridad": "MEDIA",
  "confidence": 0.5792
}
```

---

## 5. Módulo Documents

Este módulo permite subir, listar, descargar, eliminar y procesar documentos mediante extracción de texto.

---

### Subir documento

```http
POST /api/documents/upload
```

Body `form-data`:

```text
file        File    documento.pdf
tramite_id  Text    1
```

Respuesta:

```json
{
  "id": 1,
  "tramite_id": 1,
  "uploaded_by_id": 1,
  "nombre_original": "documento.pdf",
  "nombre_guardado": "70839407-55f6-427b-a420-5c7b5bd9e7ed.pdf",
  "tipo_archivo": "application/pdf",
  "ruta_archivo": "uploads/documents/70839407-55f6-427b-a420-5c7b5bd9e7ed.pdf",
  "texto_extraido": null,
  "ocr_procesado": "NO",
  "fecha_subida": "2026-05-31T07:12:45.622278"
}
```

---

### Listar documentos

```http
GET /api/documents/
```

Filtrar por trámite:

```http
GET /api/documents/?tramite_id=1
```

---

### Ver detalle de documento

```http
GET /api/documents/{document_id}
```

---

### Descargar documento

```http
GET /api/documents/{document_id}/download
```

Ejemplo:

```http
GET /api/documents/1/download
```

---

### Procesar OCR / extraer texto

```http
POST /api/documents/{document_id}/ocr
```

Respuesta:

```json
{
  "document_id": 1,
  "texto_extraido": "Texto extraído del documento...",
  "message": "Texto extraído correctamente"
}
```

---

### Eliminar documento

```http
DELETE /api/documents/{document_id}
```

Respuesta:

```json
{
  "message": "Documento eliminado correctamente"
}
```

---

## 6. Módulo HR / Convocatorias

Este módulo gestiona convocatorias laborales para el proceso de selección de personal.

Estados disponibles:

```text
ABIERTA
PAUSADA
CERRADA
```

---

### Crear convocatoria

```http
POST /api/hr/jobs/
```

Body:

```json
{
  "titulo": "Analista de Sistemas",
  "descripcion": "Responsable del soporte, mantenimiento y mejora de sistemas informáticos municipales.",
  "requisitos": "Python, FastAPI, SQL, PostgreSQL, soporte técnico, gestión documental y conocimientos básicos de machine learning.",
  "area": "Tecnología de la Información",
  "modalidad": "Presencial",
  "ubicacion": "Municipalidad Provincial de Yau"
}
```

Respuesta:

```json
{
  "id": 1,
  "titulo": "Analista de Sistemas",
  "descripcion": "Responsable del soporte, mantenimiento y mejora de sistemas informáticos municipales.",
  "requisitos": "Python, FastAPI, SQL, PostgreSQL, soporte técnico, gestión documental y conocimientos básicos de machine learning.",
  "area": "Tecnología de la Información",
  "modalidad": "Presencial",
  "ubicacion": "Municipalidad Provincial de Yau",
  "estado": "ABIERTA",
  "created_by_id": 1,
  "fecha_creacion": "2026-05-31T07:37:10.828964",
  "fecha_actualizacion": "2026-05-31T07:37:10.828972"
}
```

---

### Listar convocatorias

```http
GET /api/hr/jobs/
```

Filtros:

```http
GET /api/hr/jobs/?estado=ABIERTA
GET /api/hr/jobs/?area=Tecnología
```

---

### Ver detalle de convocatoria

```http
GET /api/hr/jobs/{job_id}
```

---

### Editar convocatoria

```http
PUT /api/hr/jobs/{job_id}
```

Body:

```json
{
  "titulo": "Analista de Sistemas Junior",
  "estado": "ABIERTA"
}
```

---

### Eliminar convocatoria

```http
DELETE /api/hr/jobs/{job_id}
```

Respuesta:

```json
{
  "message": "Convocatoria eliminada correctamente"
}
```

---

## 7. Módulo CVs

Este módulo permite subir CVs, asociarlos a una convocatoria y extraer texto para análisis NLP.

---

### Subir CV

```http
POST /api/cvs/upload
```

Body `form-data`:

```text
file                  File    CV.pdf
nombre_candidato      Text    Eduard De La Cruz
correo_candidato      Text    candidato@gmail.com
telefono_candidato    Text    999888777
job_id                Text    1
```

Respuesta:

```json
{
  "id": 1,
  "job_id": 1,
  "uploaded_by_id": 1,
  "nombre_candidato": "Eduard De La Cruz",
  "correo_candidato": "candidato@gmail.com",
  "telefono_candidato": "999888777",
  "nombre_original": "CV.pdf",
  "nombre_guardado": "56e320f1-5b83-4220-821e-b4834c9b6e29.pdf",
  "tipo_archivo": "application/pdf",
  "ruta_archivo": "uploads/cvs/56e320f1-5b83-4220-821e-b4834c9b6e29.pdf",
  "texto_extraido": null,
  "texto_procesado": "NO",
  "fecha_subida": "2026-05-31T07:45:55.086217"
}
```

---

### Listar CVs

```http
GET /api/cvs/
```

Filtrar por convocatoria:

```http
GET /api/cvs/?job_id=1
```

---

### Ver detalle de CV

```http
GET /api/cvs/{cv_id}
```

---

### Extraer texto del CV

```http
POST /api/cvs/{cv_id}/extract
```

Respuesta:

```json
{
  "cv_id": 1,
  "texto_extraido": "Texto extraído del CV...",
  "message": "Texto del CV extraído correctamente"
}
```

---

### Eliminar CV

```http
DELETE /api/cvs/{cv_id}
```

Respuesta:

```json
{
  "message": "Currículo eliminado correctamente"
}
```

---

## 8. Módulo NLP para CVs

Este módulo compara un CV con una convocatoria usando **TF-IDF** y **Cosine Similarity**.

---

### Comparar CV con convocatoria

```http
POST /api/ml/cv/match
```

Body:

```json
{
  "cv_id": 1,
  "job_id": 1
}
```

Respuesta:

```json
{
  "cv_id": 1,
  "job_id": 1,
  "candidato": "Eduard De La Cruz",
  "convocatoria": "Analista de Sistemas Junior",
  "compatibilidad": 20.86,
  "resultado": "Candidato con baja compatibilidad"
}
```

---

### Ranking de candidatos por convocatoria

```http
GET /api/ml/cv/ranking/{job_id}
```

Ejemplo:

```http
GET /api/ml/cv/ranking/1
```

Respuesta:

```json
{
  "job_id": 1,
  "convocatoria": "Analista de Sistemas Junior",
  "total_candidatos": 1,
  "ranking": [
    {
      "cv_id": 1,
      "candidato": "Eduard De La Cruz",
      "correo": "candidato@gmail.com",
      "telefono": "999888777",
      "compatibilidad": 20.86,
      "resultado": "Candidato con baja compatibilidad"
    }
  ]
}
```

---

## 9. Módulo Dashboard

Este módulo devuelve métricas generales para el frontend.

---

### Resumen general

```http
GET /api/dashboard/summary
```

Respuesta:

```json
{
  "total_usuarios": 3,
  "total_tramites": 1,
  "total_documentos": 1,
  "total_convocatorias": 1,
  "total_cvs": 1
}
```

---

### Trámites por estado

```http
GET /api/dashboard/tramites/status
```

Respuesta:

```json
[
  {
    "estado": "FINALIZADO",
    "total": 1
  }
]
```

---

### Trámites por prioridad

```http
GET /api/dashboard/tramites/priorities
```

Respuesta:

```json
[
  {
    "prioridad": "MEDIA",
    "total": 1
  }
]
```

---

### Dashboard RRHH

```http
GET /api/dashboard/rrhh
```

Respuesta:

```json
{
  "total_convocatorias": 1,
  "total_cvs": 1,
  "cvs_procesados": 1,
  "cvs_pendientes": 0
}
```

---

## 10. Módulo Notifications

Este módulo permite enviar notificaciones por correo y registrar los envíos en base de datos.

El sistema soporta:

- Notificaciones manuales.
- Notificaciones automáticas al cambiar estado de trámite.
- Reenvío.
- Filtros por trámite.
- Estado de envío.

Estados disponibles:

```text
PENDIENTE
ENVIADO
FALLIDO
SIMULADO
```

---

### Enviar notificación manual

```http
POST /api/notifications/email
```

Body:

```json
{
  "destinatario": "ciudadano@gmail.com",
  "asunto": "Actualización de trámite TRM-000001",
  "mensaje": "Su trámite se encuentra actualmente EN REVISIÓN por el área responsable.",
  "tramite_id": 1
}
```

Respuesta:

```json
{
  "id": 1,
  "destinatario": "ciudadano@gmail.com",
  "asunto": "Actualización de trámite TRM-000001",
  "mensaje": "Su trámite se encuentra actualmente EN REVISIÓN por el área responsable.",
  "estado": "ENVIADO",
  "tramite_id": 1,
  "created_by_id": 1,
  "fecha_creacion": "2026-05-31T08:12:03.123078",
  "fecha_envio": "2026-05-31T08:12:06.130891"
}
```

---

### Listar notificaciones

```http
GET /api/notifications/
```

Filtros:

```http
GET /api/notifications/?tramite_id=1
GET /api/notifications/?estado=ENVIADO
```

---

### Ver detalle de notificación

```http
GET /api/notifications/{notification_id}
```

---

### Reenviar notificación

```http
POST /api/notifications/{notification_id}/resend
```

Respuesta:

```json
{
  "id": 2,
  "destinatario": "ciudadano@gmail.com",
  "asunto": "Actualización de trámite TRM-000001",
  "mensaje": "Su trámite se encuentra actualmente EN REVISIÓN por el área responsable.",
  "estado": "ENVIADO",
  "tramite_id": 1,
  "created_by_id": 1,
  "fecha_creacion": "2026-05-31T08:12:37.455765",
  "fecha_envio": "2026-05-31T08:14:44.943232"
}
```

---

## 11. Módulo Reports

Este módulo genera reportes administrativos en formato JSON y PDF.

---

### Reporte de trámites JSON

```http
GET /api/reports/tramites
```

Respuesta:

```json
{
  "total_tramites": 1,
  "registrados": 0,
  "en_revision": 0,
  "observados": 0,
  "aprobados": 0,
  "rechazados": 0,
  "finalizados": 1,
  "prioridades": {
    "BAJA": 0,
    "MEDIA": 1,
    "ALTA": 0,
    "CRITICA": 0
  }
}
```

---

### Reporte de documentos JSON

```http
GET /api/reports/documents
```

Respuesta:

```json
{
  "total_documentos": 1,
  "documentos_con_ocr": 1,
  "documentos_sin_ocr": 0,
  "documentos_asociados_tramite": 1
}
```

---

### Reporte RRHH JSON

```http
GET /api/reports/rrhh
```

Respuesta:

```json
{
  "total_convocatorias": 1,
  "abiertas": 1,
  "pausadas": 0,
  "cerradas": 0,
  "total_cvs": 1,
  "cvs_procesados": 1,
  "cvs_pendientes": 0
}
```

---

### Reporte de notificaciones JSON

```http
GET /api/reports/notifications
```

Respuesta:

```json
{
  "total_notificaciones": 4,
  "enviadas": 4,
  "fallidas": 0,
  "simuladas": 0,
  "pendientes": 0
}
```

---

### Exportar reporte de trámites PDF

```http
GET /api/reports/tramites/pdf
```

Respuesta:

```text
Archivo PDF descargable: reporte_tramites.pdf
```

---

### Exportar reporte documental PDF

```http
GET /api/reports/documents/pdf
```

Respuesta:

```text
Archivo PDF descargable: reporte_documentos.pdf
```

---

### Exportar reporte RRHH PDF

```http
GET /api/reports/rrhh/pdf
```

Respuesta:

```text
Archivo PDF descargable: reporte_rrhh.pdf
```

---

### Exportar reporte de notificaciones PDF

```http
GET /api/reports/notifications/pdf
```

Respuesta:

```text
Archivo PDF descargable: reporte_notificaciones.pdf
```

---

# Flujo recomendado de pruebas en Postman

Para probar el sistema desde cero, seguir este orden:

```text
1. Crear administrador inicial.
2. Iniciar sesión.
3. Copiar access_token.
4. Crear usuarios internos: recepcionista, analista y RRHH.
5. Crear trámite.
6. Asignar trámite a analista.
7. Cambiar estado del trámite.
8. Ver historial del trámite.
9. Entrenar modelo ML de trámites.
10. Predecir prioridad del trámite.
11. Subir documento.
12. Ejecutar OCR del documento.
13. Crear convocatoria laboral.
14. Subir CV.
15. Extraer texto del CV.
16. Comparar CV con convocatoria.
17. Generar ranking de candidatos.
18. Enviar notificación manual.
19. Revisar dashboard.
20. Revisar reportes JSON.
21. Descargar reportes PDF.
22. Cerrar sesión.
```

---

# Roles y permisos generales

| Rol | Descripción |
|---|---|
| ADMIN | Control total del sistema |
| RECEPCIONISTA | Registro y gestión inicial de trámites |
| ANALISTA | Revisión de trámites y predicciones |
| RRHH | Gestión de convocatorias y CVs |

---

# Seguridad implementada

El backend cuenta con:

- Autenticación JWT.
- Access token.
- Refresh token.
- Logout con blacklist.
- Validación de usuario activo.
- Protección por roles.
- Hash de contraseñas con bcrypt.
- Endpoints protegidos mediante `Authorization: Bearer Token`.
- Bloqueo de refresh token revocado.

---

# Machine Learning implementado

## Random Forest para trámites

Se utiliza un modelo `RandomForestClassifier` para clasificar la prioridad de un trámite en:

```text
BAJA
MEDIA
ALTA
CRITICA
```

Variables consideradas:

- Tipo de trámite.
- Área responsable.
- Días de espera.
- Cantidad de documentos.
- Observaciones.
- Urgencia detectada por palabras clave.

---

## NLP para CVs

Se utiliza:

```text
TF-IDF + Cosine Similarity
```

El sistema compara:

```text
Texto extraído del CV
vs
Título, descripción, requisitos y área de la convocatoria
```

Con ello calcula un porcentaje de compatibilidad y genera un resultado como:

```text
Candidato altamente compatible
Candidato compatible
Candidato parcialmente compatible
Candidato con baja compatibilidad
```

---

# OCR implementado

Para documentos y CVs se utiliza extracción de texto desde PDF mediante PyMuPDF.

El sistema permite:

- Leer documentos PDF.
- Extraer texto.
- Guardar texto en base de datos.
- Marcar documento como procesado.
- Usar texto extraído para análisis posterior.

---

# Notificaciones

El sistema puede enviar correos reales usando SMTP Gmail.

También registra cada notificación en la base de datos.

Cuando se cambia el estado de un trámite, el sistema puede notificar automáticamente al ciudadano usando el campo:

```text
correo_solicitante
```

---

# Reportes

El sistema genera reportes en:

- JSON.
- PDF.

Los reportes cubren:

- Trámites.
- Documentos.
- RRHH.
- Notificaciones.

Los archivos PDF se guardan en:

```text
uploads/reports/
```

--


## Configuración de variables de entorno

El proyecto incluye un archivo `.env.example` con las variables necesarias.

Para configurar el entorno local:

```bash
copy .env.example .env
```

Luego, reemplaza las variables de ejemplo con las propias de tu entorno. Por ejemplo:

```text
DATABASE_URL=postgresql://postgres:TU_PASSWORD@localhost:5432/sigdem_ml_db
SECRET_KEY=CAMBIA_ESTA_CLAVE_SECRETA
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_password_de_aplicacion
SMTP_FROM_EMAIL=tu_correo@gmail.com
SMTP_USE_TLS=true
```


# Carpetas generadas automáticamente

Durante el uso del sistema se generan carpetas como:

```text
uploads/documents/
uploads/cvs/
uploads/reports/
ml_models/
```

Estas carpetas almacenan archivos subidos, reportes generados y modelos entrenados.

No se recomienda subir estas carpetas a GitHub.

---

# Comando principal de ejecución

```bash
uvicorn app.main:app --reload
```

---

# URL de documentación automática

```text
http://127.0.0.1:8000/docs
```

---



# Consumo del backend desde el frontend

Este backend está preparado para ser consumido desde un frontend web desarrollado en tecnologías como React, Vue, Angular o cualquier cliente HTTP.

La URL base del backend en entorno local es:

```text
http://127.0.0.1:8000
```

---


# Estado actual del backend

El backend cumple con los objetivos principales del caso práctico:

- Gestión automatizada de trámites.
- Priorización con Machine Learning.
- Gestión documental.
- OCR de documentos.
- Alertas automáticas al ciudadano.
- Gestión de RRHH.
- Selección de CVs con NLP.
- Dashboard administrativo.
- Reportes JSON y PDF.
- Seguridad mediante JWT y roles.

---

# Próximas mejoras sugeridas

Aunque el backend ya cumple con el alcance principal, se pueden agregar mejoras futuras:

- Migraciones con Alembic.
- Exportación Excel.
- Mejor entrenamiento del modelo ML con más datos reales.
- OCR avanzado para imágenes escaneadas.
- Panel web frontend.
- Auditoría avanzada por usuario.
- Logs del sistema.
- Deploy en servidor cloud.
- Integración con servicios oficiales de mesa de partes.
- Integración con WhatsApp Business API.
- Mejora del modelo NLP con extracción de habilidades clave.

---

# Conclusión

SIGDEM-ML Backend es una API REST desarrollada con FastAPI que permite automatizar procesos administrativos municipales, gestionar documentos, procesar trámites, aplicar Machine Learning para priorización, analizar currículos mediante NLP y generar reportes administrativos.

Este backend está preparado para conectarse con un frontend web y ser usado como base funcional para un sistema inteligente de gestión documental y selección de personal en una municipalidad.