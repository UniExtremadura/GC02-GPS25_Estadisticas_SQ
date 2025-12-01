# 📊 Microservicio de Estadísticas

Este es el microservicio encargado de gestionar las estadísticas (oyentes, valoraciones, visualizaciones) de la plataforma. Está construido con **FastAPI** y utiliza **PostgreSQL** como base de datos.

El proyecto está totalmente **dockerizado** para facilitar su despliegue y desarrollo.

Existe un **.json** en la ruta inicial que se puede exportar en **Postman** para probar todos los endpoints.

---

## 📋 Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado en tu ordenador:

* **Docker Desktop** (asegúrate de que esté abierto y corriendo).
* **Git**.

> **⚠️ Nota importante:** Este microservicio se conecta con los servicios de **Usuarios (Puerto 3000)**, **Contenido (Puerto 8083)**, **Comunidades (Puerto 8084)** y **Frontend (Puerto 3001)**. Para que la sincronización funcione correctamente, asegúrate de tener esos servicios levantados en tu máquina local.

---

## 🚀 Cómo levantar el proyecto (Paso a Paso)

Sigue estos pasos para tener el microservicio funcionando en menos de 2 minutos:

### 1. Clonar el repositorio
Descarga el proyecto en tu carpeta de preferencia:

```bash
git clone <URL_DEL_REPOSITORIO_AQUI>
cd <NOMBRE_DE_LA_CARPETA_DEL_PROYECTO>
````

### 2\. Levantar el entorno Docker

No necesitas crear entornos virtuales ni instalar PostgreSQL manualmente. Ejecuta el siguiente comando en la raíz del proyecto:

```bash
docker-compose up --build
```

  * ⏳ **Espera:** La primera vez tardará unos minutos descargando las imágenes.
  * ⚙️ **Automático:** Verás que la base de datos se inicia y crea las tablas automáticamente gracias al script `init.sql`.
  * ✅ **Listo:** Cuando veas el mensaje `Application startup complete` en la terminal, estará funcionando.

-----

## 🔗 Acceso a la Aplicación

Una vez levantado, tienes disponibles los siguientes recursos:

| Recurso | URL | Descripción |
| :--- | :--- | :--- |
| **Swagger UI** | [http://localhost:8000/docs](https://www.google.com/search?q=http://localhost:8000/docs) | Documentación interactiva para probar endpoints. |
| **API Root** | [http://localhost:8000](https://www.google.com/search?q=http://localhost:8000) | Raíz de la API. |

-----

## 🗄️ Acceso a la Base de Datos (DBeaver / pgAdmin)

La base de datos corre dentro de un contenedor Docker. Hemos expuesto el puerto **5434** para evitar conflictos con otros Postgres que tengas instalados en local.

Para conectarte desde **DBeaver** o cualquier cliente SQL, usa estas credenciales:

| Parámetro | Valor |
| :--- | :--- |
| **Host** | `localhost` |
| **Puerto** | `5434` (⚠️ Ojo, no es el 5432 estándar) |
| **Base de Datos** | `estadisticas` |
| **Usuario** | `postgres` |
| **Contraseña** | `password123` |

-----

## 🛠️ Comandos Útiles

**Detener los contenedores:**
Presiona `Ctrl + C` en la terminal donde corren los logs.

**Detener y borrar todo (limpieza total):**
Si quieres reiniciar la base de datos desde cero (borrando los datos guardados):

```bash
docker-compose down -v
```

-----

## 🧩 Arquitectura y Puertos

| Servicio | Puerto Local | Puerto Docker | Descripción |
| :--- | :--- | :--- | :--- |
| **API (FastAPI)** | `8000` | `8000` | Servidor de la aplicación. |
| **Base de Datos** | `5434` | `5432` | PostgreSQL 16 con persistencia de datos. |

-----

## ❓ Solución de problemas comunes

### ❌ Error: "Port is already allocated"

Si al levantar el docker te dice que el puerto 5434 (u otro) está ocupado, asegúrate de no tener una instancia antigua de este proyecto corriendo "zombi" en segundo plano:

```bash
docker-compose down
```

### ❌ Error de conexión con Usuarios/Contenido

Si la API da error al intentar sincronizar oyentes (`Connection refused`), verifica que tienes los **otros microservicios encendidos** en tu ordenador (fuera de Docker) en los puertos `3000` y `8083` respectivamente.
