# Autrum

- [Introducción](#introducción)
- [Instalación](#instalación)
- [Explicación de Componentes](#explicación-de-componentes)
  - [Interfaz Principal](#interfaz-principal)
  - [Analizador](#analizador)
  - [Reproductor](#reproductor)
  - [Comparador](#comparador)
- [Ejecución](#ejecución)

## Introducción

**Autrum** es una aplicación desarrollada en Python que permite analizar, reproducir y comparar señales de audio a través de una interfaz gráfica intuitiva. La aplicación está estructurada en tres componentes principales: **Analizador**, **Reproductor** y **Comparador**, y utiliza una ventana principal para gestionar la navegación entre ellos. Autrum permite realizar operaciones avanzadas como la transformación de Fourier, reducción de ruido, eliminación de silencios y comparación de señales.  

## Instalación

Para correr este proyecto se necesita crear un **ambiente virtual de python**. Siga los siguiente pasos:

1. **Cree el ambiente virtual**

```bash
python -m venv .env
```

2. **Active el ambiente virtual**

**Windows:**

```powershell
.env/Scripts/activate
```

**Mac o Linux:**

```bash
source .env/bin/activate
```

3. **Instale las dependencias**

```bash
pip install -r requirements.txt
```

4. **Si desea desactivarlo**

```bash
deactivate
```

## Explicación de Componentes

A continuación se detallan las funcionalidades de cada componente que tiene la aplicación Autrum. 

### Interfaz Principal

La aplicación comienza en una ventana principal denominada **Autrum**, desde la cual el usuario puede acceder a los tres modos de operación: **Analizador**, **Reproductor** y **Comparador**. Esta ventana principal permanece abierta en todo momento, y permite cambiar entre los diferentes modos sin necesidad de cerrar la aplicación.

### Analizador

El Analizador, le permite al usuario grabar o cargar archivos de audio para realizar un análisis en tiempo real. Las principales características de este modo incluyen:

- Grabación de Audio en Streaming: El usuario puede iniciar, detener, pausar o continuar la grabación mediante el micrófono.

- Visualización Gráfica:

  - Se muestra la señal en el dominio del tiempo (amplitud del audio vs. tiempo).
- Se calcula la transformada de Fourier para visualizar la señal en el dominio de frecuencia (componentes de frecuencia del audio).
  - Los gráficos se actualizan en tiempo real mientras se graba o analiza el audio.
  
- Generación de Archivos: El audio y sus datos de frecuencia se guardan en un archivo personalizado con extensión `.atm`, que contiene tanto el audio original como su información de frecuencia.

### Reproductor

En el Reproductor, el usuario puede cargar y reproducir archivos `.atm`. Las características principales incluyen:

- Reproducción de Audio: Se reproduce el audio mientras se visualizan los gráficos tanto en el dominio del tiempo como en el de la frecuencia.
- Control de la Reproducción: El usuario puede reproducir, pausar, reanudar o cancelar la reproducción, y ajustar dinámicamente la posición de la reproducción.
- Interacción con los Gráficos: El usuario puede hacer zoom in y zoom out en los gráficos para un análisis más detallado de la señal.

### Comparador

El Comparador permite al usuario comparar un archivo `.atm` pregrabado con una nueva entrada de audio grabada a través del micrófono. Este modo es útil para detectar coincidencias de palabras o frases. Las características clave incluyen:

- Comparación entre Archivos y Audio en Vivo: El usuario puede cargar un archivo `.atm` y grabar un nuevo segmento de audio para compararlo.

- Coincidencia de Señales:

  - Comparación de Armónicos: Compara los componentes armónicos de ambas señales usando sus transformadas de Fourier.
- Comparación del Espectro de Potencia: Compara la potencia de las señales a través de las frecuencias.
  
- Detección de Coincidencias Aproximadas: El sistema calcula el punto donde la nueva entrada de audio coincide con la grabación original y proporciona un nivel de confianza (0-100%) sobre la coincidencia.

- Reproducción de Audio: Una vez encontrada la coincidencia, el audio se reproduce desde el punto identificado, permitiendo al usuario escuchar los resultados.

## Ejecución

Para ejecutar **Autrum**, debe realizar los siguientes pasos:

1. Activar el ambiente virtual de python si no lo ha hecho. 
2. Ejecutar desde la consola, el archivo Autrum. Para esto, debe ejecutar: `cd src`y luego `python Autrum.py`. 
3. Observará la interfaz principal, a partir de ahí puede interactuar con todos los componentes. Si desea terminar el programa, simplemente cierre la ventaja principal. 