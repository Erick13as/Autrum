---
title: Documentación-TC1

---

Tarea Corta I - Autrum
Redes-IC7602
Grupo 2
II Semestre 2024
Entrega: 08/09/2024

---
<u>Integrantes:</u>
Sofía Vega Chavarría - 2021571216
Gerald Núñez Chavarría - 2021023226
Sebastián Arroniz Rojas - 2021108521
Erick Alvarado Solano - 2020091055
Kevin Córdoba Chevez - 2020100920

---

Tabla de Contenidos <!-- omit in toc --> 


[TOC]

## Guía de Instalación
### Pre Requisitos
Se debe clonar el repositorio [Autrum](https://github.com/Erick13as/Autrum) a la máquina local.
Se debe tener instalado [Python](https://www.python.org/downloads/) versión 3.7 o superior.
Se Recomienda instalar [Visual Studio Code](https://code.visualstudio.com/).
Se recomienda instalar la extensión Python en Visual Studio Code.

### Instalación
Para poder ejecutar este proyecto sugerimos elegir uno de los siguientes dos métodos, el primero consiste en crear un ambiente virtual y el segundo en realizar la instalación de las librerías en la propia máquina.

#### Método 1: Ambiente Virtual
En este método para poder ejecutar este proyecto se necesita crear un **ambiente virtual de python**. Para esto siga los siguiente pasos:

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

#### Método 2: Instalación de Librerías

En este segundo método, para poder hacer uso de los tres componentes principales del presente trabajo, se deben instalar en la máquina donde se desee probar el código, una serie de librerías que permiten trabajar con audio en Python y realizar gráficas.

Para realizar la instalación de dichas librerías se debe abrir una ventana del *Command Prompt* (CMD) en modo administrador para contar con los permisos necesarios para la instalación.

Las librerías se instalan mediante el comando pip. La lista de comandos necesarios es las siguiente.

```
pip install pyaudio
pip install --upgrade scipy
pip install soundfile librosa
pip install pydub
pip install sounddevice
pip install noisereduce
pip install librosa
```

## Guía de Uso
Autrum cuenta con 3 funciones principales, la primera es un analizador de audio el cual permite grabar audio de un micrófono o cargar un archivo con extensión .wav, grafica su señal en el dominio del tiempo y grafica la transformada de Fourier correspondiente. Además, este componente genera un archivo con extensión .atm, el cual contiene el audio junto con los datos utilizados para generar lso gráficos.
El segundo componente corresponde a un reproductor de audio, el cual toma los archivos con extensión .atm generados por el analizador y permite reproducirlos así como observar los gráficos correspondientes a dicho audio.
El tercer componente es una herramienta que permite comparar el audio incluido en un archivo .atm con una frase que se graba por medio del micrófono, posteriormente reproduce el audio a partir del punto en el cual encuentra una coincidencia e indica el porcentaje de confianza con el que se encontró una similitud entre ambos audios.

Estas 3 funcionalidades son accesibles desde el archivo Autrum.py, el cual permite ejecutar los archivos de las funcionalidades correspondientes.

Es importante recalcar que para un correcto funcionamiento del código presente en esta tarea corta, se debe acceder a la carpeta src por medio de la línea de comandos y ejecutar el archivo Autrum.py, ejecutando los siguientes comandos en el siguiente orden.

```
cd src
pyton Autrum.py
```

En caso de utilizar la herramienta Visual Studio Code, se puede abrir directamente la carpeta src del repositorio Autrum previamente clonado, una vez dentro de esta carpeta se puede seleccionar el archivo Autrum.py y ejecutarlo con el botón *Run* localizado en la esquina superior derecha.
![aa](https://hackmd.io/_uploads/S1X_ORihA.png)


### Main
El archivo llamado Autrum despliega la ventana *Main*, la cual muestra 3 opciones, correspondientes a las funcionalidades anteriormente mencionadas.
Se debe seleccionar el botón de la funcionalidad deseada para pasar a ejecutar dicha función.
![main](https://hackmd.io/_uploads/rkKDOCo3A.png)


### Analizador
Luego de seleccionar la opción Analizador, se procede a ejecutar Analizador.py, el cual despliega 2 ventanas, la primera muestra las opciones del analizador, las cuales permiten inciar una grabación, detenerla, reanudarla, guardarla y graficarla, además permite cargar un archivo WAV y graficarlo también.

![Analizador](https://hackmd.io/_uploads/Ske-TRj2C.png)

La segunda ventana del analizador corresponde a la señal ene el dominio del tiempo y la transformada de Fourier de las señales, al incio están vaías, sin embargo al seleccionar graficar los audios o al realizar una grabación, se mostrarán aquí los detalles correspondientes.

![image](https://hackmd.io/_uploads/S1geaRs30.png)

![image](https://hackmd.io/_uploads/Sy2Q0Aj20.png)

El proceso para realizar la grabación es muy simple, primero de debe seleccionar la opción "Iniciar Grabación", esto comenzará a grabar utilizando el micrófono de la computadora, a continuación la opción "Parar Grabación" será la única activa para que el usuario tenga la opción de terminar de grabar el audio cuando guste. Una vez se detiene la grabación se activan las opciones "Continuar Grabación" y "Guardar Grabación", la primera permite continuar grabando y el proceso se repite, mientras que la segunda permite guardar el audio, esto genera 2 archivos, el audio por sí solo en un archivo con extensión .wav y un archivo con extensión .atm el cual contiene los datos necesarios para los gráficos de señal en el dominio del tiempo y la transformada de Fourier, junto al audio grabado. Estos archivos se almacenan con el nombre de la fecha y hora de la grabación, en una carpeta llamada audio.

![image](https://hackmd.io/_uploads/ryL0kyhh0.png)

Si la opción seleccionada es la de "Cargar un archivo WAV", se abre una ventana del explorador de archivos para que el usario pueda buscar en la ruta donde tenga almacenado un archivo con extensión .wav, lo seleccione y se cargue.

![image](https://hackmd.io/_uploads/B1FKfJ3hR.png)

Después de cargar el archivo WAV, se puede seleccionar la opción "Graficar Señal" y esto generará los gráficos correspondientes para el audio seleccionado.

![image](https://hackmd.io/_uploads/rygeGk23R.png)

La función "Graficar Señal" funciona tanto para las grabaciones realizadas con el programa Analizador.py como para los archivos.wav cargados por la función "Cargar un archivo WAV"

### Reproductor
Si en la ventana principal se selecciona la opción del Reproducto, se ejecutan las funcionalidades del archivo Reproductor.py, y se despliega la siguiene ventana.

![image](https://hackmd.io/_uploads/BkO6Q12h0.png)

Dado que la intención del reproductor es reproducir el audio y mostrar los gráficos de los archivos grabados por el analizador, este necesita acceder a un archivo con extensión .atm, los cuales son generados el analizador.

Al seleccionar "Cargar Archivo ATM", se muestra un explorador de archivos el cual permite seleccionar la ubicación de los archivos .atm para poder poder acceder a su contenido.

![image](https://hackmd.io/_uploads/rJ1-4k22C.png)

Luego de seleccionar un archivo, el programa indica el nombre del archivo abierto y se habilita la opción de reproducirlo con "Reproducir Audio"

![image](https://hackmd.io/_uploads/ry_rN1h3A.png)

Luego seleccionar esta opción, se reproduce el audio y se muestra la señal en el dominio del tiempo junto a la transormada de Fourier.

![image](https://hackmd.io/_uploads/rymoNyn30.png)

Durante la reproducción del audio se puede detener el mismo seleccionando la opción "Detener Reproducción", si se detiene la reproducción se habilita "Reanudar Reproducción" y dicha función permite reproducir el audio a partir del momento en el que fue pausado.

Finalmente se cuenta con la opción "Cancelar Reproducción" la cual detiene la reproducción del audio, cierra las gráficas y desactiva las funciones a excepción de "Cargar archivo ATM" y "Reproducir Audio", para que el usario tenga la opción de reproducir el audio desde cero nuevamente y ver los gráficos, o bien, seleccionar un nuevo archivo.

El usuario puede seleccionar un nuevo archivo sin la necesidad de cancelar la reproducción si así lo prefiere.

### Comparador
Si en el menú principal se selecciona la opción "Comparador", se despliega la ventana con las funcionalidades del archivo Comparator.py.

![image](https://hackmd.io/_uploads/rkT4OyhhC.png)

Dado que el objetio de esta función de Autrum es comparar una palabra con una grabación, y determinar el grado de similitud, se cuenta con opciones para grabar una audio que será la palabra a buscar dentro del audio y cargar un archivo de extensión .atm que contiene el audio en el cual se buscará la palabra. Además de una opción para reproducir el audio a partir del punto de comparación.

Cuando se selecciona la opción "Cargar Archivo ATM", se abre un explorador de archivos para seleccionar el archivo correspondiente.

![image](https://hackmd.io/_uploads/rJ9Fu133C.png)

Una vez cargado, se muestra una ventana indicando que se ha logrado cargar el archivo con éxito.

![image](https://hackmd.io/_uploads/rJi2Oknn0.png)

Después de seleccionar la opción "Grabar Palabra", se activa el micrófono permitiendo grabar la palabra deseada, una vez se quiera terminar la grabación se selecciona la opción "Detener Grabación" dicha opción solo se habilita después de comenzar a grabar un audio. Igual que en el paso anterior, una vez finalizada la grabación se muestra un mensaje de éxito.

![image](https://hackmd.io/_uploads/B1foKkn2A.png)

Cuando se selecciona la opción "Comparar Audio", se despliega una venana mostrando el grado de similitud entre ambos.

![image](https://hackmd.io/_uploads/BJkki133A.png)

Una vez se ha realizado la comparación se puede seleccionar en la opción "Reproducir Audio" y el audio se reproduce a partir del punto en el cual se hizo "*match*" entre el audio y la palabra que se grabó.

## Referencias

python-sounddevice. (s.f.). API Documentation. Recuperado de https://python-sounddevice.readthedocs.io/en/0.3.12/api.html

python-sounddevice. (s.f.). Usage. Recuperado de https://python-sounddevice.readthedocs.io/en/0.3.14/usage.html

TutorialsPoint. (s.f.). Tkinter place() Method. Recuperado de https://www.tutorialspoint.com/python/tk_place.htm

TutorialsPoint. (s.f.). Tkinter Button. Recuperado de https://www.tutorialspoint.com/python/tk_button.htm

Rajukumar. (2024). Python Tkinter – Label. Recuperado de https://www.geeksforgeeks.org/python-tkinter-label/