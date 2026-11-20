# Tus extensiones de VS Code: catálogo explicado

> Limpieza autorizada realizada posteriormente: las siete carpetas candidatas ya no existen. Se eliminaron seis durante la ejecución; otra ya estaba ausente al procesarla. La operación recuperó aproximadamente 1,74 GiB netos. Ambos registros de extensiones quedaron sin cambios, ninguna carpeta registrada desapareció y CodeLLDB 1.12.2 se conservó. Los tamaños y estados del inventario original que siguen son históricos.

> Comprobación posterior de carpetas adicionales: CodeLLDB 1.12.2 (aprox. 136 MiB) sí está referenciado por el perfil adicional y debe conservarse. Varias versiones antiguas desaparecieron entre revisiones, sin intervención de esta revisión. Actualmente quedan unos 2,69 GiB adicionales, de los cuales unos 2,55 GiB no están referenciados en ninguno de los dos registros revisados. No se ha borrado ninguna carpeta. La carpeta antes no identificada .d42170a1-3020-40c1-89f3-7af9cc4f0e13 contiene un manifiesto de Pylance 2025.12.100.

**144 extensiones registradas. Revisión de solo lectura: no se desinstaló, deshabilitó ni modificó ninguna extensión.**

Se tomó como referencia la lista de extensiones registradas en `.vscode/extensions/extensions.json`, los manifiestos `package.json`, sus traducciones y los README instalados. No se cuentan por separado versiones antiguas del mismo complemento.

También se encontró un perfil adicional con **128 extensiones registradas**, todas incluidas en las 144 del inventario general. Esto puede explicar que la vista Extensiones muestre cantidades diferentes al cambiar de perfil. No se determinó qué perfil estaba activo.

**Instalada no significa activa:** este catálogo no determina qué extensiones están habilitadas en cada perfil, cuáles se han cargado en la sesión ni cuánto consumen de RAM. Tampoco enumera las extensiones integradas de fábrica en VS Code.

Los tamaños son aproximados y corresponden a los archivos de instalación; no incluyen datos que una extensión descargue en otras ubicaciones.

## Para entender la lista

- **Snippet:** plantilla que se expande al escribir una abreviatura; por ejemplo, una estructura de función.
- **Autocompletado / IntelliSense:** sugerencias de nombres, métodos y parámetros mientras escribes.
- **Formateador:** ordena espacios, sangría y estilo del código; no garantiza que su lógica sea correcta.
- **Analizador / linter:** identifica posibles problemas o reglas de estilo.
- **Depurador:** permite pausar el programa y observar valores para entender errores.
- **Servidor de lenguaje:** analiza un lenguaje para ofrecer navegación, sugerencias y diagnósticos.
- **Paquete de extensiones:** reúne otros complementos; instalarlo puede incorporar varios a la vez.
- **Dependencia:** extensión que otra necesita o utiliza como apoyo.
- **Tema / iconos:** cambia el aspecto del editor; no añade soporte de programación.
- **Cython:** lenguaje y herramientas para combinar código de estilo Python con C/C++; no es necesario para aprender Python básico.

## Resumen por área

| Área | Cantidad |
|---|---:|
| Python | 15 |
| Cython y Python con C++ | 9 |
| Java | 8 |
| C y C++ | 7 |
| Web y JavaScript | 26 |
| PHP | 4 |
| Bases de datos | 15 |
| R | 2 |
| LaTeX y referencias | 8 |
| Asistentes y completado | 7 |
| Edición y productividad | 12 |
| Contenedores y acceso remoto | 7 |
| Imágenes y documentos | 6 |
| Apariencia y entretenimiento | 18 |

Instalaciones registradas: **4.45 GiB**. Carpetas adicionales no registradas en esa lista: **3.21 GiB**.

## Funciones parecidas que conviene reconocer

- **Java:** tienes soporte del lenguaje de Oracle y de Red Hat. Son implementaciones distintas para un propósito parecido; no se ha comprobado que causen conflictos en tu configuración.
- **Python:** Python, Pylance, Python Debugger y Python Environments se complementan. No son cuatro copias de la misma función.
- **Entornos Python:** Python Environment Manager se marca como deprecated en el nombre instalado; también tienes Python Environments de Microsoft.
- **Cython:** hay varias extensiones de resaltado y análisis que cubren funciones similares. Algunas llegaron o pueden llegar mediante CPython Extension Pack.
- **SQLite:** SQLite (alexcvzz), SQLite Viewer (qwtel) y SQLTools con su controlador SQLite ofrecen formas distintas de consultar o visualizar estas bases.
- **Vista web:** Live Server y Live Preview tienen propósitos similares. El identificador de Live Preview es ms-vscode.live-server, aunque su nombre visible sea distinto.
- **React:** ES7+ React/Redux/React-Native snippets y Simple React Snippets son colecciones diferentes de plantillas.
- **Bootstrap:** conviven herramientas para Bootstrap 4, Bootstrap 5 y autocompletado de clases.
- **LaTeX:** LaTeX Workshop es la herramienta amplia; LaTeX Utilities declara ser un complemento suyo. Los snippets, formato, símbolos, Zotero y calculadora tienen funciones más concretas.
- **IntelliCode:** tienes IntelliCode, Completions, Insiders y ejemplos de API; no todos hacen exactamente lo mismo.
- **Docker:** el README instalado indica que el antiguo Docker se convirtió en paquete y Container Tools concentra sus funciones.
- **Apariencia:** tienes varios temas y varios conjuntos de iconos. Estar instalados no implica que todos se estén aplicando.

## Python — 15

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [AREPL for python](https://marketplace.visualstudio.com/items?itemName=almenon.arepl) | Espacio de pruebas que ejecuta Python y muestra resultados conforme editas. | 3.0.0 | 16.6 MiB |
| [autoDocstring - Python Docstring Generator](https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring) | Genera plantillas de docstrings, es decir, textos de documentación dentro de funciones y clases. | 0.6.1 | 0.6 MiB |
| [Black Formatter](https://marketplace.visualstudio.com/items?itemName=ms-python.black-formatter) | Aplica el formateador Black al código Python. | 2026.6.0 | 15.5 MiB |
| [Django](https://marketplace.visualstudio.com/items?itemName=batisteo.vscode-django) | Reconoce sintaxis y ofrece plantillas para trabajar con Django y sus plantillas HTML. | 1.15.0 | 0.8 MiB |
| [Jinja](https://marketplace.visualstudio.com/items?itemName=wholroyd.jinja) | Reconoce la sintaxis de plantillas Jinja, utilizadas por herramientas como Flask. | 0.0.10 | 0.1 MiB |
| [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance) | Analiza Python para ofrecer autocompletado, navegación y comprobación de tipos. | 2026.4.101 | 153.3 MiB |
| [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) | Integración principal de Python: selección del intérprete y acceso a ejecución, pruebas, análisis y depuración mediante complementos. | 2026.10.0 | 29.7 MiB |
| [Python Debugger](https://marketplace.visualstudio.com/items?itemName=ms-python.debugpy) | Permite detener y recorrer la ejecución Python, inspeccionando variables mediante debugpy. | 2026.6.0 | 35.2 MiB |
| [Python Environment Manager (deprecated)](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-environment-manager) | Administrador de entornos y paquetes Python. Su nombre instalado lo marca como deprecated: herramienta descontinuada. | 1.2.7 | 21.1 MiB |
| [Python Environments](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs) | Ayuda a crear, seleccionar y administrar entornos de Python. | 1.40.0 | 11.1 MiB |
| [Python Extended](https://marketplace.visualstudio.com/items?itemName=tushortz.python-extended-snippets) | Plantillas de código Python y opciones de completado de argumentos. | 0.0.1 | 1.4 MiB |
| [Python Extension Pack](https://marketplace.visualstudio.com/items?itemName=donjayamanne.python-extension-pack) | Paquete que reúne extensiones para Python, documentación, plantillas y entornos. | 1.7.0 | 0.1 MiB |
| [Python Indent](https://marketplace.visualstudio.com/items?itemName=kevinrose.vsc-python-indent) | Ayuda a insertar la sangría correcta al escribir código Python. | 1.21.0 | 2.1 MiB |
| [Python Path](https://marketplace.visualstudio.com/items?itemName=mgesbert.python-path) | Copia rutas de módulos Python y genera instrucciones import para archivos o símbolos seleccionados. | 0.0.14 | 0.4 MiB |
| [python snippets](https://marketplace.visualstudio.com/items?itemName=frhtylcn.pythonsnippets) | Colección de plantillas para escribir código Python con abreviaturas. | 1.0.2 | 6.6 MiB |

## Cython y Python con C++ — 9

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [CPython Extension Pack](https://marketplace.visualstudio.com/items?itemName=franneck94.vscode-cpython-extension-pack) | Paquete orientado al desarrollo CPython/Cython; incluye herramientas de Cython y depuración mixta. | 0.1.0 | 0.1 MiB |
| [Cython](https://marketplace.visualstudio.com/items?itemName=tcwalther.cython) | Resaltado de sintaxis para archivos Cython. | 0.1.0 | 0.1 MiB |
| [Cython Enhanced](https://marketplace.visualstudio.com/items?itemName=whoami730.cython-enhanced) | Otra herramienta de Cython con resaltado, comprobación y navegación de código. | 1.0.5 | 13.4 MiB |
| [Cython Forge](https://marketplace.visualstudio.com/items?itemName=sheiksshajeenahamed.cython-forge) | Ayuda a construir o compilar archivos Cython. | 0.0.3 | 1.5 MiB |
| [Cython Syntax Highlighting Fixed](https://marketplace.visualstudio.com/items?itemName=ecostadelle.cython-syntax-fixed) | Variante corregida de una extensión de resaltado de sintaxis Cython. | 1.0.1 | 0.2 MiB |
| [Cython VSCode](https://marketplace.visualstudio.com/items?itemName=ktnrg45.vscode-cython) | Reconoce sintaxis Cython y añade comprobación, navegación a definiciones y análisis de tipos. | 1.0.3 | 11.7 MiB |
| [Language-Cython](https://marketplace.visualstudio.com/items?itemName=guyskk.language-cython) | Otra extensión de resaltado de sintaxis Cython. | 0.0.8 | 0.4 MiB |
| [Python C++ Debugger](https://marketplace.visualstudio.com/items?itemName=benjamin-simmonds.pythoncpp-debug) | Ayuda a iniciar depuradores de Python y C++ sobre el mismo proceso. | 0.3.0 | 1.0 MiB |
| [vscode-cython-annotate](https://marketplace.visualstudio.com/items?itemName=itaiin.vscode-cython-annotate) | Muestra anotaciones del código Cython para examinar su traducción y comportamiento. | 0.1.6 | 1.2 MiB |

## Java — 8

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Debugger for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-debug) | Permite ejecutar Java paso a paso e inspeccionar variables mediante un depurador. | 0.60.0 | 3.8 MiB |
| [Extension Pack for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-pack) | Paquete de herramientas Java: soporte del lenguaje, depuración, pruebas, proyectos, Maven y Gradle. | 0.31.2 | 6.4 MiB |
| [Gradle for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-gradle) | Administra proyectos Gradle y permite ejecutar sus tareas desde el editor. | 3.18.1 | 35.5 MiB |
| [Java](https://marketplace.visualstudio.com/items?itemName=oracle.oracle-java) | Soporte Java de Oracle: otra implementación de las herramientas del lenguaje Java. | 27.0.0 | 301.1 MiB |
| [Language Support for Java(TM) by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.java) | Soporte Java de Red Hat: análisis, autocompletado, formato, navegación y refactorización. | 1.57.0 | 178.2 MiB |
| [Maven for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-maven) | Administra proyectos Maven y ejecuta sus tareas de construcción y dependencias. | 0.46.0 | 17.8 MiB |
| [Project Manager for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-dependency) | Panel para organizar proyectos Java, dependencias y archivos del proyecto. | 0.27.7 | 0.9 MiB |
| [Test Runner for Java](https://marketplace.visualstudio.com/items?itemName=vscjava.vscode-java-test) | Ejecuta y depura pruebas automáticas Java de JUnit o TestNG. | 0.47.0 | 5.8 MiB |

## C y C++ — 7

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [C/C++](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools) | Autocompletado, navegación y depuración para C/C++ de Microsoft. | 1.35.4 | 269.7 MiB |
| [C/C++ Config](https://marketplace.visualstudio.com/items?itemName=franneck94.vscode-c-cpp-config) | Ayuda a generar archivos de configuración de proyectos C/C++. | 6.3.0 | 0.7 MiB |
| [C/C++ DevTools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpp-devtools) | Herramientas adicionales de desarrollo C/C++, incluidas por otros paquetes del ecosistema. | 0.6.18 | 0.5 MiB |
| [C/C++ Extension Pack](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools-extension-pack) | Paquete que reúne soporte C/C++, herramientas de desarrollo y CMake. | 1.5.1 | 0.0 MiB |
| [CMake](https://marketplace.visualstudio.com/items?itemName=twxs.cmake) | Reconoce y colorea archivos del lenguaje de configuración CMake. | 0.0.17 | 8.1 MiB |
| [CMake Tools](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools) | Configura, construye y ayuda a depurar proyectos que utilizan CMake. | 1.24.42 | 26.4 MiB |
| [CodeLLDB](https://marketplace.visualstudio.com/items?itemName=vadimcn.vscode-lldb) | Depurador basado en LLDB para C++, Rust y otros lenguajes compilados. | 1.12.3 | 135.1 MiB |

## Web y JavaScript — 26

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Angular Language Service](https://marketplace.visualstudio.com/items?itemName=angular.ng-template) | Analiza plantillas Angular para ofrecer sugerencias, navegación y diagnóstico. | 22.2.0 | 60.9 MiB |
| [Angular Snippets (Version 22)](https://marketplace.visualstudio.com/items?itemName=johnpapa.angular2) | Plantillas para escribir componentes y otras estructuras Angular. | 22.0.0 | 2.4 MiB |
| [Auto Close Tag](https://marketplace.visualstudio.com/items?itemName=formulahendry.auto-close-tag) | Inserta automáticamente la etiqueta de cierre en HTML y XML. | 0.5.15 | 0.9 MiB |
| [Auto Rename Tag](https://marketplace.visualstudio.com/items?itemName=formulahendry.auto-rename-tag) | Al cambiar una etiqueta HTML/XML, actualiza también su pareja de apertura o cierre. | 0.1.10 | 2.6 MiB |
| [Bootstrap 4, Font awesome 4, Font Awesome 5 Free & Pro snippets](https://marketplace.visualstudio.com/items?itemName=thekalinga.bootstrap4-vscode) | Plantillas de Bootstrap 4 y de iconos Font Awesome. | 6.1.0 | 1.2 MiB |
| [Bootstrap 5 Quick Snippets](https://marketplace.visualstudio.com/items?itemName=anbuselvanrocky.bootstrap5-vscode) | Plantillas de componentes y estructuras Bootstrap 5. | 0.5.0 | 0.2 MiB |
| [Bootstrap IntelliSense](https://marketplace.visualstudio.com/items?itemName=hossaini.bootstrap-intellisense) | Sugiere clases CSS de Bootstrap mientras escribes. | 3.2.0 | 0.8 MiB |
| [Color Highlight](https://marketplace.visualstudio.com/items?itemName=naumovs.color-highlight) | Resalta visualmente los colores escritos en el código. | 2.8.0 | 1.1 MiB |
| [Color Info](https://marketplace.visualstudio.com/items?itemName=bierner.color-info) | Muestra información y representaciones de colores escritos en CSS. | 0.7.2 | 0.2 MiB |
| [CSS Peek](https://marketplace.visualstudio.com/items?itemName=pranaygp.vscode-css-peek) | Permite saltar desde una clase o identificador HTML a su definición CSS. | 4.4.3 | 24.8 MiB |
| [ES7+ React/Redux/React-Native snippets](https://marketplace.visualstudio.com/items?itemName=dsznajder.es7-react-js-snippets) | Plantillas para React, Redux y React Native en JavaScript y TypeScript. | 4.4.3 | 20.3 MiB |
| [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) | Muestra reglas y avisos de ESLint para detectar problemas y mantener convenciones en JavaScript/TypeScript. | 3.0.34 | 0.9 MiB |
| [HTML CSS Support](https://marketplace.visualstudio.com/items?itemName=ecmel.vscode-html-css) | Añade sugerencias de CSS al editar HTML. | 2.0.14 | 0.0 MiB |
| [Import Cost](https://marketplace.visualstudio.com/items?itemName=wix.vscode-import-cost) | Estima y muestra el tamaño que aportan paquetes importados en JavaScript/TypeScript. | 3.3.0 | 44.5 MiB |
| [IntelliSense for CSS class names in HTML](https://marketplace.visualstudio.com/items?itemName=zignd.html-css-class-completion) | Sugiere clases CSS al escribir el atributo class en HTML, a partir de los archivos del proyecto. | 1.20.0 | 7.3 MiB |
| [JavaScript (ES6) code snippets](https://marketplace.visualstudio.com/items?itemName=xabikos.javascriptsnippets) | Plantillas breves para escribir estructuras habituales de JavaScript moderno. | 1.8.0 | 0.0 MiB |
| [JavaScript Debugger (Nightly)](https://marketplace.visualstudio.com/items?itemName=ms-vscode.js-debug-nightly) | Versión de pruebas del depurador JavaScript para Node.js y Chrome. | 2026.10.1417 | 3.5 MiB |
| [Live Preview](https://marketplace.visualstudio.com/items?itemName=ms-vscode.live-server) | Previsualiza páginas del proyecto con un servidor local; cumple una función parecida a Live Server. | 0.4.20 | 1.2 MiB |
| [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.liveserver) | Sirve páginas del proyecto mediante un servidor local y recarga el navegador al guardar cambios. | 5.7.10 | 15.1 MiB |
| [Next JS/TS Snippets](https://marketplace.visualstudio.com/items?itemName=loczek.next-js-ts-snippets) | Plantillas de JavaScript y TypeScript para proyectos Next.js. | 2.0.3 | 0.1 MiB |
| [NPM](https://marketplace.visualstudio.com/items?itemName=idered.npm) | Administra dependencias de proyectos desde una barra lateral; contempla npm, yarn, pnpm y bun. | 1.7.4 | 0.6 MiB |
| [npm Intellisense](https://marketplace.visualstudio.com/items?itemName=christian-kohler.npm-intellisense) | Sugiere nombres de paquetes npm al escribir instrucciones import. | 1.4.5 | 1.7 MiB |
| [Quokka.js](https://marketplace.visualstudio.com/items?itemName=wallabyjs.quokka-vscode) | Entorno de pruebas que ejecuta JavaScript/TypeScript y muestra valores mientras editas. | 1.0.769 | 86.9 MiB |
| [Simple React Snippets](https://marketplace.visualstudio.com/items?itemName=burkeholland.simple-react-snippets) | Otra colección de plantillas para React, más enfocada en estructuras frecuentes. | 1.2.8 | 5.9 MiB |
| [Tailwind CSS IntelliSense](https://marketplace.visualstudio.com/items?itemName=bradlc.vscode-tailwindcss) | Autocompleta clases Tailwind CSS y muestra información sobre sus estilos. | 0.16.0 | 6.8 MiB |
| [Version Lens](https://marketplace.visualstudio.com/items?itemName=pflannery.vscode-versionlens) | Muestra información de versiones de dependencias junto al código o manifiesto del proyecto. | 1.28.0 | 2.7 MiB |

## PHP — 4

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [PHP Awesome Snippets](https://marketplace.visualstudio.com/items?itemName=hakcorp.php-awesome-snippets) | Plantillas de código para tareas habituales de PHP. | 1.1.3 | 0.7 MiB |
| [PHP Debug](https://marketplace.visualstudio.com/items?itemName=xdebug.php-debug) | Integra la depuración PHP mediante Xdebug; permite pausas y revisión de variables. | 1.40.2 | 5.6 MiB |
| [PHP Intelephense](https://marketplace.visualstudio.com/items?itemName=bmewburn.vscode-intelephense-client) | Autocompletado, navegación y análisis del código PHP mediante Intelephense. | 1.18.5 | 25.2 MiB |
| [PHP XAMPP Runner](https://marketplace.visualstudio.com/items?itemName=daryoushalipourtirotir.php-xampp-runner) | Ejecuta archivos PHP mediante un servidor local XAMPP ya disponible. | 0.0.1 | 0.1 MiB |

## Bases de datos — 15

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Data Workspace](https://marketplace.visualstudio.com/items?itemName=ms-mssql.data-workspace-vscode) | Funciones compartidas que sirven de apoyo a las herramientas de proyectos de bases de datos. | 0.7.0 | 0.0 MiB |
| [DBML Entity-Relationship Diagrams visualizer](https://marketplace.visualstudio.com/items?itemName=bocovo.dbml-erd-visualizer) | Visualiza diagramas de entidades y relaciones a partir de archivos DBML, un lenguaje para describir tablas. | 0.8.0 | 5.7 MiB |
| [DBML Formatter - The best and only DBML formatter](https://marketplace.visualstudio.com/items?itemName=aflalo.dbml-formatter) | Da formato a archivos DBML para mantener ordenada la descripción de tablas y relaciones. | 0.0.8 | 45.7 MiB |
| [MySQL](https://marketplace.visualstudio.com/items?itemName=formulahendry.vscode-mysql) | Permite conectarse a MySQL y administrar consultas desde VS Code. | 0.5.0 | 1.7 MiB |
| [MySQL Syntax](https://marketplace.visualstudio.com/items?itemName=jakebathman.mysql-syntax) | Colorea y reconoce la sintaxis de consultas MySQL; no instala un servidor MySQL. | 1.3.1 | 0.0 MiB |
| [Prettier SQL VSCode](https://marketplace.visualstudio.com/items?itemName=inferrinizzard.prettier-sql-vscode) | Formatea consultas y archivos SQL; no administra el servidor de base de datos. | 1.6.0 | 1.5 MiB |
| [Rainbow CSV](https://marketplace.visualstudio.com/items?itemName=mechatroner.rainbow-csv) | Colorea columnas de CSV/TSV y permite consultas similares a SQL sobre esos archivos. | 3.24.1 | 2.9 MiB |
| [SQL Bindings](https://marketplace.visualstudio.com/items?itemName=ms-mssql.sql-bindings-vscode) | Ayuda a desarrollar Azure Functions conectadas a Azure SQL mediante bindings; es una herramienta especializada. | 0.4.1 | 3.5 MiB |
| [SQL Database Projects](https://marketplace.visualstudio.com/items?itemName=ms-mssql.sql-database-projects-vscode) | Ayuda a desarrollar y publicar esquemas de bases SQL Server mediante proyectos de base de datos. | 1.8.0 | 0.4 MiB |
| [SQL Server (mssql)](https://marketplace.visualstudio.com/items?itemName=ms-mssql.mssql) | Herramientas para conectarse, consultar y trabajar con SQL Server y Azure SQL. | 1.46.0 | 369.5 MiB |
| [SQL Viewer](https://marketplace.visualstudio.com/items?itemName=nei.sql-viewer) | Visor y herramienta de consultas SQL según su descripción instalada. | 0.0.6 | 30.4 MiB |
| [SQLite](https://marketplace.visualstudio.com/items?itemName=alexcvzz.vscode-sqlite) | Explora bases SQLite y permite ejecutar consultas. | 0.14.1 | 5.1 MiB |
| [SQLite Viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer) | Otra extensión para visualizar bases SQLite dentro de VS Code. | 26.9.1 | 14.9 MiB |
| [SQLTools](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools) | Cliente para conectar y consultar distintos motores de bases de datos mediante controladores. | 0.28.6 | 3.4 MiB |
| [SQLTools SQLite](https://marketplace.visualstudio.com/items?itemName=mtxr.sqltools-driver-sqlite) | Controlador que permite a SQLTools conectarse a bases SQLite; complementa SQLTools. | 0.5.4 | 0.7 MiB |

## R — 2

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [R](https://marketplace.visualstudio.com/items?itemName=reditorsupport.r) | Soporte para trabajar con el lenguaje R dentro de VS Code. | 3.0.1 | 6.1 MiB |
| [R Syntax](https://marketplace.visualstudio.com/items?itemName=reditorsupport.r-syntax) | Resaltado de sintaxis para archivos del lenguaje R. | 0.1.4 | 0.2 MiB |

## LaTeX y referencias — 8

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [LaTeX](https://marketplace.visualstudio.com/items?itemName=mathematic.vscode-latex) | Soporte adicional del lenguaje LaTeX; se solapa en parte con LaTeX Workshop. | 2.2.3 | 1.1 MiB |
| [LaTeX Snippets](https://marketplace.visualstudio.com/items?itemName=jeffersonqin.latex-snippets-jeff) | Plantillas para escribir comandos y estructuras LaTeX. | 1.2.3 | 2.6 MiB |
| [Latex Sympy Calculator](https://marketplace.visualstudio.com/items?itemName=orangex4.latex-sympy-calculator) | Usa expresiones LaTeX y SymPy para realizar cálculos en documentos LaTeX o Markdown. | 1.6.0 | 0.6 MiB |
| [LaTeX Utilities](https://marketplace.visualstudio.com/items?itemName=tecosaur.latex-utilities) | Complemento de LaTeX Workshop con utilidades adicionales de edición. | 0.4.14 | 0.8 MiB |
| [LaTeX Workshop](https://marketplace.visualstudio.com/items?itemName=james-yu.latex-workshop) | Entorno principal de edición LaTeX: compilación, vista previa, autocompletado y navegación. | 10.19.0 | 27.6 MiB |
| [latex-formatter](https://marketplace.visualstudio.com/items?itemName=nickfode.latex-formatter) | Da formato al código fuente LaTeX para ordenarlo. | 1.0.5 | 0.5 MiB |
| [Unicode Latex](https://marketplace.visualstudio.com/items?itemName=oijaz.unicode-latex) | Convierte nombres de símbolos de estilo LaTeX en caracteres Unicode. | 1.2.0 | 0.1 MiB |
| [Zotero LaTeX](https://marketplace.visualstudio.com/items?itemName=bnavetta.zoterolatex) | Integra funciones de Zotero para insertar o manejar referencias al escribir LaTeX. | 0.4.1 | 0.1 MiB |

## Asistentes y completado — 7

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Claude Code for VS Code](https://marketplace.visualstudio.com/items?itemName=anthropic.claude-code) | Integra el asistente Claude Code en VS Code. | 2.1.300 | 269.7 MiB |
| [Codex Audio](https://marketplace.visualstudio.com/items?itemName=openai.codex-audio) | Soporte local de micrófono para el dictado de Codex, incluidos espacios de trabajo remotos. | 26.1007.21434 | 4.4 MiB |
| [Codex – OpenAI’s coding agent](https://marketplace.visualstudio.com/items?itemName=openai.chatgpt) | Asistente Codex para trabajar con código desde VS Code. Su identificador interno sigue siendo openai.chatgpt. | 26.51007.21434 | 1384.9 MiB |
| [Ejemplos de uso de la API de IntelliCode](https://marketplace.visualstudio.com/items?itemName=visualstudioexptteam.intellicode-api-usage-examples) | Muestra ejemplos de uso de funciones y API a partir de código público de GitHub. | 0.2.9 | 7.4 MiB |
| [Finalizaciones de IntelliCode](https://marketplace.visualstudio.com/items?itemName=visualstudioexptteam.vscodeintellicode-completions) | Completado de código asistido por inteligencia artificial de la familia IntelliCode. | 2.0.1 | 182.7 MiB |
| [IntelliCode](https://marketplace.visualstudio.com/items?itemName=visualstudioexptteam.vscodeintellicode) | Asistencia para sugerencias de código mediante IntelliCode. | 1.3.2 | 65.5 MiB |
| [IntelliCode Insiders](https://marketplace.visualstudio.com/items?itemName=visualstudioexptteam.vscodeintellicode-insiders) | Variante de pruebas de IntelliCode que incorpora su extensión de completado. | 1.1.10 | 12.1 MiB |

## Edición y productividad — 12

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Better Comments](https://marketplace.visualstudio.com/items?itemName=aaron-bond.better-comments) | Distingue visualmente comentarios informativos, advertencias y pendientes TODO. | 3.0.2 | 0.3 MiB |
| [Bracket Pair Color DLW](https://marketplace.visualstudio.com/items?itemName=bracketpaircolordlw.bracket-pair-color-dlw) | Añade un comando para activar o desactivar el coloreado de pares de paréntesis y llaves que ofrece VS Code. | 0.0.6 | 0.0 MiB |
| [Code Runner](https://marketplace.visualstudio.com/items?itemName=formulahendry.code-runner) | Ejecuta archivos o fragmentos de varios lenguajes usando las herramientas correspondientes que tengas instaladas. | 0.12.2 | 1.4 MiB |
| [Error Lens](https://marketplace.visualstudio.com/items?itemName=usernamehw.errorlens) | Muestra errores y advertencias junto a la línea correspondiente de forma más visible. | 3.29.0 | 0.2 MiB |
| [indent-rainbow](https://marketplace.visualstudio.com/items?itemName=oderwat.indent-rainbow) | Colorea la sangría por niveles para ver mejor la estructura de los bloques. | 8.3.1 | 8.5 MiB |
| [Indenticator](https://marketplace.visualstudio.com/items?itemName=sirtori.indenticator) | Resalta el nivel de sangría del bloque donde está el cursor. | 0.7.0 | 0.2 MiB |
| [Path Intellisense](https://marketplace.visualstudio.com/items?itemName=christian-kohler.path-intellisense) | Autocompleta nombres de archivos y carpetas mientras escribes rutas. | 2.10.0 | 0.4 MiB |
| [PowerShell](https://marketplace.visualstudio.com/items?itemName=ms-vscode.powershell) | Soporte de edición, comandos y depuración para scripts PowerShell. | 2025.4.0 | 300.9 MiB |
| [Prettier - Code formatter](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) | Ordena automáticamente el formato de código de lenguajes compatibles, como JavaScript, HTML y CSS. | 12.4.0 | 14.0 MiB |
| [Spanish Language Pack for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=ms-ceintl.vscode-language-pack-es) | Traduce la interfaz de VS Code al español. | 1.131.2026090407 | 2.8 MiB |
| [Spell Right](https://marketplace.visualstudio.com/items?itemName=ban.spellright) | Corrector ortográfico multilingüe para textos y comentarios. | 3.0.156 | 25.1 MiB |
| [Trailing Spaces](https://marketplace.visualstudio.com/items?itemName=shardulm94.trailing-spaces) | Resalta y permite quitar espacios sobrantes al final de las líneas. | 0.4.4 | 0.1 MiB |

## Contenedores y acceso remoto — 7

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [.NET Install Tool](https://marketplace.visualstudio.com/items?itemName=ms-dotnettools.vscode-dotnet-runtime) | Instala y administra versiones de .NET que pueden necesitar otras extensiones; no significa que programes en C#. | 3.2.0 | 5.8 MiB |
| [Container Tools](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-containers) | Crea y administra imágenes, contenedores y otros recursos de Docker/Podman. | 2.5.2 | 4.3 MiB |
| [Docker](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker) | Entrada de compatibilidad del antiguo Docker: su README explica que ahora es un paquete asociado a Container Tools. | 2.0.0 | 0.1 MiB |
| [Explorador remoto](https://marketplace.visualstudio.com/items?itemName=ms-vscode.remote-explorer) | Panel para explorar conexiones a equipos remotos mediante SSH y túneles. | 0.5.0 | 0.1 MiB |
| [Live Share](https://marketplace.visualstudio.com/items?itemName=ms-vsliveshare.vsliveshare) | Permite colaborar con otras personas en una sesión de edición compartida. | 1.1.122 | 25.4 MiB |
| [Remote - SSH](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh) | Permite abrir carpetas y trabajar en otro equipo por una conexión SSH. | 0.128.0 | 2.7 MiB |
| [Remote - SSH: Editing Configuration Files](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-ssh-edit) | Ayuda a editar archivos de configuración de conexiones SSH. | 0.87.0 | 0.1 MiB |

## Imágenes y documentos — 6

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Better SVG](https://marketplace.visualstudio.com/items?itemName=midudev.better-svg) | Previsualiza SVG y ofrece controles de zoom, selección de color y optimización mediante SVGO. | 0.5.1 | 0.7 MiB |
| [Docx/ODT Viewer](https://marketplace.visualstudio.com/items?itemName=shahilkumar.docxreader) | Permite visualizar documentos DOCX y ODT dentro del editor. | 1.4.3 | 10.1 MiB |
| [Image preview](https://marketplace.visualstudio.com/items?itemName=kisstkondoros.vscode-gutter-preview) | Muestra miniaturas de imágenes al pasar el cursor y en el margen del editor. | 0.32.2 | 1.7 MiB |
| [Snapcode](https://marketplace.visualstudio.com/items?itemName=moyu.snapcode) | Genera imágenes de fragmentos de código para compartirlos; deriva de Polacode. | 1.1.0 | 0.1 MiB |
| [SVG-Viewer](https://marketplace.visualstudio.com/items?itemName=dheovani.svg-viewer) | Permite previsualizar imágenes vectoriales SVG dentro del editor. | 1.1.2 | 0.0 MiB |
| [vscode-pdf](https://marketplace.visualstudio.com/items?itemName=tomoki1207.pdf) | Abre archivos PDF dentro de VS Code. | 1.2.2 | 8.5 MiB |

## Apariencia y entretenimiento — 18

| Extensión | Para qué sirve | Versión | Tamaño |
|---|---|---|---:|
| [Atom One Dark Theme](https://marketplace.visualstudio.com/items?itemName=akamud.vscode-theme-onedark) | Tema de colores inspirado en One Dark de Atom. | 2.3.0 | 0.1 MiB |
| [Ayu](https://marketplace.visualstudio.com/items?itemName=teabyii.ayu) | Tema Ayu con variantes clara, oscura y mirage. | 1.4.1 | 5.9 MiB |
| [Background](https://marketplace.visualstudio.com/items?itemName=katsute.code-background) | Añade imágenes de fondo al editor. | 6.1.1 | 0.3 MiB |
| [Bearded Icons](https://marketplace.visualstudio.com/items?itemName=beardedbear.beardedicons) | Cambia los iconos de archivos y carpetas del explorador. | 1.22.0 | 0.5 MiB |
| [Bearded Theme](https://marketplace.visualstudio.com/items?itemName=beardedbear.beardedtheme) | Colección de temas de colores Bearded Theme. | 10.1.0 | 2.7 MiB |
| [Best Themes Redefined 🚀](https://marketplace.visualstudio.com/items?itemName=lakshits11.best-themes-redefined) | Colección de numerosos temas de colores; no son herramientas de programación distintas. | 0.4.6 | 5.7 MiB |
| [Dark Horizon](https://marketplace.visualstudio.com/items?itemName=mcagampan.dark-horizon) | Tema oscuro con colores de texto vivos. | 0.4.2 | 0.2 MiB |
| [Doki Theme](https://marketplace.visualstudio.com/items?itemName=unthrottled.doki-theme) | Colección de temas inspirados en personajes de anime. | 88.1.18 | 2.0 MiB |
| [Easy Eyes Theme](https://marketplace.visualstudio.com/items?itemName=vvhg1.theme-easy-eyes) | Tema con una paleta pensada para facilitar la lectura. | 1.2.1 | 0.4 MiB |
| [Material Icon Theme](https://marketplace.visualstudio.com/items?itemName=pkief.material-icon-theme) | Tema de iconos para reconocer tipos de archivos y carpetas. | 5.39.0 | 1.9 MiB |
| [Nord](https://marketplace.visualstudio.com/items?itemName=arcticicestudio.nord-visual-studio-code) | Tema de colores fríos y azulados. | 0.19.0 | 0.2 MiB |
| [One Dark Pro Monokai Darker Theme](https://marketplace.visualstudio.com/items?itemName=eserozvataf.one-dark-pro-monokai-darker) | Tema oscuro que combina variantes de One Dark y Monokai. | 1.1.0 | 1.8 MiB |
| [Palenight Theme](https://marketplace.visualstudio.com/items?itemName=whizkydee.material-palenight-theme) | Tema de colores Palenight inspirado en Material Design. | 2.0.5 | 0.2 MiB |
| [ReUI](https://marketplace.visualstudio.com/items?itemName=barrsan.reui) | Tema de colores inspirado en la web de React; no añade herramientas de React. | 1.2.5 | 1.6 MiB |
| [Scepter Theme](https://marketplace.visualstudio.com/items?itemName=isaacwilson.scepter) | Tema oscuro Scepter, inspirado en Halcyon. | 1.1.7 | 0.7 MiB |
| [vscode-icons-iconify](https://marketplace.visualstudio.com/items?itemName=lqyld.vscode-icons-iconify) | Tema de iconos de archivos basado en vscode-icons e Iconify. | 0.1.2 | 7.4 MiB |
| [vscode-pokemon](https://marketplace.visualstudio.com/items?itemName=jakobhoeg.vscode-pokemon) | Muestra Pokémon interactivos en el editor; es una personalización recreativa. | 5.0.2 | 13.3 MiB |
| [vscode-spotify](https://marketplace.visualstudio.com/items?itemName=shyykoserhiy.vscode-spotify) | Integra controles o funciones de Spotify en VS Code. | 3.2.1 | 8.8 MiB |

## Paquetes y dependencias que explican parte de la cantidad

Estas relaciones se leen de los manifiestos instalados. No prueban qué instalaste primero ni por qué se instaló cada extensión.

### Python Extension Pack

Identificador: `donjayamanne.python-extension-pack`.

**Incluye como paquete:**

- autoDocstring - Python Docstring Generator — `njpwerner.autodocstring` (registrada)
- Python — `ms-python.python` (registrada)
- Jinja — `wholroyd.jinja` (registrada)
- Django — `batisteo.vscode-django` (registrada)
- IntelliCode — `VisualStudioExptTeam.vscodeintellicode` (registrada)
- Python Indent — `KevinRose.vsc-python-indent` (registrada)
- Python Environment Manager (deprecated) — `donjayamanne.python-environment-manager` (registrada)

### Docker

Identificador: `ms-azuretools.vscode-docker`.

**Dependencias declaradas:**

- Container Tools — `ms-azuretools.vscode-containers` (registrada)

### C/C++ Config

Identificador: `franneck94.vscode-c-cpp-config`.

**Dependencias declaradas:**

- C/C++ — `ms-vscode.cpptools` (registrada)
- CodeLLDB — `vadimcn.vscode-lldb` (registrada)

### SQL Bindings

Identificador: `ms-mssql.sql-bindings-vscode`.

**Dependencias declaradas:**

- SQL Server (mssql) — `ms-mssql.mssql` (registrada)

### IntelliCode Insiders

Identificador: `visualstudioexptteam.vscodeintellicode-insiders`.

**Incluye como paquete:**

- Finalizaciones de IntelliCode — `visualstudioexptteam.vscodeintellicode-completions` (registrada)

**Dependencias declaradas:**

- .NET Install Tool — `ms-dotnettools.vscode-dotnet-runtime` (registrada)

### IntelliCode

Identificador: `visualstudioexptteam.vscodeintellicode`.

**Incluye como paquete:**

- Ejemplos de uso de la API de IntelliCode — `visualstudioexptteam.intellicode-api-usage-examples` (registrada)

### CPython Extension Pack

Identificador: `franneck94.vscode-cpython-extension-pack`.

**Incluye como paquete:**

- Cython — `tcwalther.cython` (registrada)
- Python C++ Debugger — `benjamin-simmonds.pythoncpp-debug` (registrada)

### Python C++ Debugger

Identificador: `benjamin-simmonds.pythoncpp-debug`.

**Dependencias declaradas:**

- Python — `ms-python.python` (registrada)
- C/C++ — `ms-vscode.cpptools` (registrada)

### C/C++ Extension Pack

Identificador: `ms-vscode.cpptools-extension-pack`.

**Incluye como paquete:**

- C/C++ — `ms-vscode.cpptools` (registrada)
- ms-vscode.cpptools-themes — `ms-vscode.cpptools-themes` (no aparece en la lista principal examinada)
- C/C++ DevTools — `ms-vscode.cpp-devtools` (registrada)
- CMake Tools — `ms-vscode.cmake-tools` (registrada)

### Python Debugger

Identificador: `ms-python.debugpy`.

**Dependencias declaradas:**

- Python — `ms-python.python` (registrada)

### Black Formatter

Identificador: `ms-python.black-formatter`.

**Dependencias declaradas:**

- Python — `ms-python.python` (registrada)

### SQLTools SQLite

Identificador: `mtxr.sqltools-driver-sqlite`.

**Dependencias declaradas:**

- SQLTools — `mtxr.sqltools` (registrada)

### Remote - SSH

Identificador: `ms-vscode-remote.remote-ssh`.

**Incluye como paquete:**

- Remote - SSH: Editing Configuration Files — `ms-vscode-remote.remote-ssh-edit` (registrada)
- Explorador remoto — `ms-vscode.remote-explorer` (registrada)

### CMake Tools

Identificador: `ms-vscode.cmake-tools`.

**Incluye como paquete:**

- C/C++ DevTools — `ms-vscode.cpp-devtools` (registrada)

### Container Tools

Identificador: `ms-azuretools.vscode-containers`.

**Dependencias declaradas:**

- vscode.docker — `vscode.docker` (no aparece en la lista principal examinada)
- vscode.yaml — `vscode.yaml` (no aparece en la lista principal examinada)

### SQL Database Projects

Identificador: `ms-mssql.sql-database-projects-vscode`.

**Dependencias declaradas:**

- SQL Server (mssql) — `ms-mssql.mssql` (registrada)
- Data Workspace — `ms-mssql.data-workspace-vscode` (registrada)

### Data Workspace

Identificador: `ms-mssql.data-workspace-vscode`.

**Dependencias declaradas:**

- SQL Server (mssql) — `ms-mssql.mssql` (registrada)

### SQL Server (mssql)

Identificador: `ms-mssql.mssql`.

**Incluye como paquete:**

- Data Workspace — `ms-mssql.data-workspace-vscode` (registrada)
- SQL Database Projects — `ms-mssql.sql-database-projects-vscode` (registrada)
- SQL Bindings — `ms-mssql.sql-bindings-vscode` (registrada)
- .NET Install Tool — `ms-dotnettools.vscode-dotnet-runtime` (registrada)

**Dependencias declaradas:**

- vscode.sql — `vscode.sql` (no aparece en la lista principal examinada)

### PowerShell

Identificador: `ms-vscode.powershell`.

**Dependencias declaradas:**

- vscode.powershell — `vscode.powershell` (no aparece en la lista principal examinada)

### R

Identificador: `reditorsupport.r`.

**Dependencias declaradas:**

- R Syntax — `REditorSupport.r-syntax` (registrada)

### Codex – OpenAI’s coding agent

Identificador: `openai.chatgpt`.

**Incluye como paquete:**

- Codex Audio — `openai.codex-audio` (registrada)

### Extension Pack for Java

Identificador: `vscjava.vscode-java-pack`.

**Incluye como paquete:**

- Language Support for Java(TM) by Red Hat — `redhat.java` (registrada)
- Debugger for Java — `vscjava.vscode-java-debug` (registrada)
- Test Runner for Java — `vscjava.vscode-java-test` (registrada)
- Maven for Java — `vscjava.vscode-maven` (registrada)
- Gradle for Java — `vscjava.vscode-gradle` (registrada)
- Project Manager for Java — `vscjava.vscode-java-dependency` (registrada)

### Test Runner for Java

Identificador: `vscjava.vscode-java-test`.

**Dependencias declaradas:**

- Language Support for Java(TM) by Red Hat — `redhat.java` (registrada)
- Debugger for Java — `vscjava.vscode-java-debug` (registrada)

### Python

Identificador: `ms-python.python`.

**Incluye como paquete:**

- Pylance — `ms-python.vscode-pylance` (registrada)
- Python Debugger — `ms-python.debugpy` (registrada)
- Python Environments — `ms-python.vscode-python-envs` (registrada)

## Las 15 instalaciones registradas que más ocupan

| Extensión | Tamaño |
|---|---:|
| Codex – OpenAI’s coding agent | 1384.9 MiB |
| SQL Server (mssql) | 369.5 MiB |
| Java | 301.1 MiB |
| PowerShell | 300.9 MiB |
| C/C++ | 269.7 MiB |
| Claude Code for VS Code | 269.7 MiB |
| Finalizaciones de IntelliCode | 182.7 MiB |
| Language Support for Java(TM) by Red Hat | 178.2 MiB |
| Pylance | 153.3 MiB |
| CodeLLDB | 135.1 MiB |
| Quokka.js | 86.9 MiB |
| IntelliCode | 65.5 MiB |
| Angular Language Service | 60.9 MiB |
| DBML Formatter - The best and only DBML formatter | 45.7 MiB |
| Import Cost | 44.5 MiB |

## Carpetas adicionales: no son extensiones distintas

Existen 13 carpetas fuera de las ubicaciones registradas en la lista principal. Varias contienen versiones previas del mismo producto. Las carpetas ocultas con identificador aleatorio podrían ser restos de instalación o actualización; no se ha confirmado su uso y no se eliminaron.

| Carpeta | Producto identificado en manifiesto | Versión | Tamaño |
|---|---|---|---:|
| .82436d2c-690f-4325-93b3-7fa473f161e1 | openai.chatgpt | 26.5715.61943 | 869.8 MiB |
| .11e78cc6-eaca-40fe-8dfa-c5b15e362d18 | openai.chatgpt | 26.5825.51511 | 835.7 MiB |
| .32f786eb-cc9f-4a67-a64e-7fa946da03a3 | openai.chatgpt | 26.5818.31338 | 730.1 MiB |
| anthropic.claude-code-2.1.299-win32-x64 | Anthropic.claude-code | 2.1.299 | 268.1 MiB |
| ms-python.vscode-pylance-2026.4.100 | ms-python.vscode-pylance | 2026.4.100 | 209.6 MiB |
| vadimcn.vscode-lldb-1.12.2 | vadimcn.vscode-lldb | 1.12.2 | 135.7 MiB |
| .fdb02d3d-3e91-44e2-95e6-08c24c22cfa5 | ms-python.vscode-pylance | 2025.12.100 | 77.1 MiB |
| .d42170a1-3020-40c1-89f3-7af9cc4f0e13 | No identificado |  | 64.3 MiB |
| vscjava.vscode-gradle-3.18.0 | vscjava.vscode-gradle | 3.18.0 | 35.6 MiB |
| .46ae1072-14da-44e8-9e86-f2d3b80b0f02 | ms-mssql.sql-database-projects-vscode | 1.6.2 | 34.3 MiB |
| ban.spellright-3.0.154 | ban.spellright | 3.0.154 | 22.8 MiB |
| .dfb6976f-ae30-4723-8e45-ec7890de799f | ms-mssql.mssql | 1.44.0 | 3.5 MiB |
| vscjava.vscode-java-dependency-0.27.6 | vscjava.vscode-java-dependency | 0.27.6 | 1.2 MiB |

## Cómo ubicar una extensión sin cambiar nada

1. Abre Extensiones con **Ctrl+Shift+X**.
2. Escribe **@installed** para ver las instaladas.
3. Para localizar una exacta, busca **@id:publicador.extension**. Los identificadores están en la tabla siguiente.
4. Abre su ficha para consultar detalles; esto no la desinstala ni cambia su estado.

Para estudiar tu configuración, empieza por reconocer las extensiones del lenguaje que estás practicando. Un grupo razonable para entender primero en Python es Python, Pylance, Python Debugger y Python Environments; después identifica qué aporta Black Formatter.

## Índice de identificadores

| Extensión | Identificador |
|---|---|
| .NET Install Tool | `ms-dotnettools.vscode-dotnet-runtime` |
| Angular Language Service | `angular.ng-template` |
| Angular Snippets (Version 22) | `johnpapa.angular2` |
| AREPL for python | `almenon.arepl` |
| Atom One Dark Theme | `akamud.vscode-theme-onedark` |
| Auto Close Tag | `formulahendry.auto-close-tag` |
| Auto Rename Tag | `formulahendry.auto-rename-tag` |
| autoDocstring - Python Docstring Generator | `njpwerner.autodocstring` |
| Ayu | `teabyii.ayu` |
| Background | `katsute.code-background` |
| Bearded Icons | `beardedbear.beardedicons` |
| Bearded Theme | `beardedbear.beardedtheme` |
| Best Themes Redefined 🚀 | `lakshits11.best-themes-redefined` |
| Better Comments | `aaron-bond.better-comments` |
| Better SVG | `midudev.better-svg` |
| Black Formatter | `ms-python.black-formatter` |
| Bootstrap 4, Font awesome 4, Font Awesome 5 Free & Pro snippets | `thekalinga.bootstrap4-vscode` |
| Bootstrap 5 Quick Snippets | `anbuselvanrocky.bootstrap5-vscode` |
| Bootstrap IntelliSense | `hossaini.bootstrap-intellisense` |
| Bracket Pair Color DLW | `bracketpaircolordlw.bracket-pair-color-dlw` |
| C/C++ | `ms-vscode.cpptools` |
| C/C++ Config | `franneck94.vscode-c-cpp-config` |
| C/C++ DevTools | `ms-vscode.cpp-devtools` |
| C/C++ Extension Pack | `ms-vscode.cpptools-extension-pack` |
| Claude Code for VS Code | `anthropic.claude-code` |
| CMake | `twxs.cmake` |
| CMake Tools | `ms-vscode.cmake-tools` |
| Code Runner | `formulahendry.code-runner` |
| CodeLLDB | `vadimcn.vscode-lldb` |
| Codex Audio | `openai.codex-audio` |
| Codex – OpenAI’s coding agent | `openai.chatgpt` |
| Color Highlight | `naumovs.color-highlight` |
| Color Info | `bierner.color-info` |
| Container Tools | `ms-azuretools.vscode-containers` |
| CPython Extension Pack | `franneck94.vscode-cpython-extension-pack` |
| CSS Peek | `pranaygp.vscode-css-peek` |
| Cython | `tcwalther.cython` |
| Cython Enhanced | `whoami730.cython-enhanced` |
| Cython Forge | `sheiksshajeenahamed.cython-forge` |
| Cython Syntax Highlighting Fixed | `ecostadelle.cython-syntax-fixed` |
| Cython VSCode | `ktnrg45.vscode-cython` |
| Dark Horizon | `mcagampan.dark-horizon` |
| Data Workspace | `ms-mssql.data-workspace-vscode` |
| DBML Entity-Relationship Diagrams visualizer | `bocovo.dbml-erd-visualizer` |
| DBML Formatter - The best and only DBML formatter | `aflalo.dbml-formatter` |
| Debugger for Java | `vscjava.vscode-java-debug` |
| Django | `batisteo.vscode-django` |
| Docker | `ms-azuretools.vscode-docker` |
| Docx/ODT Viewer | `shahilkumar.docxreader` |
| Doki Theme | `unthrottled.doki-theme` |
| Easy Eyes Theme | `vvhg1.theme-easy-eyes` |
| Ejemplos de uso de la API de IntelliCode | `visualstudioexptteam.intellicode-api-usage-examples` |
| Error Lens | `usernamehw.errorlens` |
| ES7+ React/Redux/React-Native snippets | `dsznajder.es7-react-js-snippets` |
| ESLint | `dbaeumer.vscode-eslint` |
| Explorador remoto | `ms-vscode.remote-explorer` |
| Extension Pack for Java | `vscjava.vscode-java-pack` |
| Finalizaciones de IntelliCode | `visualstudioexptteam.vscodeintellicode-completions` |
| Gradle for Java | `vscjava.vscode-gradle` |
| HTML CSS Support | `ecmel.vscode-html-css` |
| Image preview | `kisstkondoros.vscode-gutter-preview` |
| Import Cost | `wix.vscode-import-cost` |
| indent-rainbow | `oderwat.indent-rainbow` |
| Indenticator | `sirtori.indenticator` |
| IntelliCode | `visualstudioexptteam.vscodeintellicode` |
| IntelliCode Insiders | `visualstudioexptteam.vscodeintellicode-insiders` |
| IntelliSense for CSS class names in HTML | `zignd.html-css-class-completion` |
| Java | `oracle.oracle-java` |
| JavaScript (ES6) code snippets | `xabikos.javascriptsnippets` |
| JavaScript Debugger (Nightly) | `ms-vscode.js-debug-nightly` |
| Jinja | `wholroyd.jinja` |
| Language Support for Java(TM) by Red Hat | `redhat.java` |
| Language-Cython | `guyskk.language-cython` |
| LaTeX | `mathematic.vscode-latex` |
| LaTeX Snippets | `jeffersonqin.latex-snippets-jeff` |
| Latex Sympy Calculator | `orangex4.latex-sympy-calculator` |
| LaTeX Utilities | `tecosaur.latex-utilities` |
| LaTeX Workshop | `james-yu.latex-workshop` |
| latex-formatter | `nickfode.latex-formatter` |
| Live Preview | `ms-vscode.live-server` |
| Live Server | `ritwickdey.liveserver` |
| Live Share | `ms-vsliveshare.vsliveshare` |
| Material Icon Theme | `pkief.material-icon-theme` |
| Maven for Java | `vscjava.vscode-maven` |
| MySQL | `formulahendry.vscode-mysql` |
| MySQL Syntax | `jakebathman.mysql-syntax` |
| Next JS/TS Snippets | `loczek.next-js-ts-snippets` |
| Nord | `arcticicestudio.nord-visual-studio-code` |
| NPM | `idered.npm` |
| npm Intellisense | `christian-kohler.npm-intellisense` |
| One Dark Pro Monokai Darker Theme | `eserozvataf.one-dark-pro-monokai-darker` |
| Palenight Theme | `whizkydee.material-palenight-theme` |
| Path Intellisense | `christian-kohler.path-intellisense` |
| PHP Awesome Snippets | `hakcorp.php-awesome-snippets` |
| PHP Debug | `xdebug.php-debug` |
| PHP Intelephense | `bmewburn.vscode-intelephense-client` |
| PHP XAMPP Runner | `daryoushalipourtirotir.php-xampp-runner` |
| PowerShell | `ms-vscode.powershell` |
| Prettier - Code formatter | `esbenp.prettier-vscode` |
| Prettier SQL VSCode | `inferrinizzard.prettier-sql-vscode` |
| Project Manager for Java | `vscjava.vscode-java-dependency` |
| Pylance | `ms-python.vscode-pylance` |
| Python | `ms-python.python` |
| Python C++ Debugger | `benjamin-simmonds.pythoncpp-debug` |
| Python Debugger | `ms-python.debugpy` |
| Python Environment Manager (deprecated) | `donjayamanne.python-environment-manager` |
| Python Environments | `ms-python.vscode-python-envs` |
| Python Extended | `tushortz.python-extended-snippets` |
| Python Extension Pack | `donjayamanne.python-extension-pack` |
| Python Indent | `kevinrose.vsc-python-indent` |
| Python Path | `mgesbert.python-path` |
| python snippets | `frhtylcn.pythonsnippets` |
| Quokka.js | `wallabyjs.quokka-vscode` |
| R | `reditorsupport.r` |
| R Syntax | `reditorsupport.r-syntax` |
| Rainbow CSV | `mechatroner.rainbow-csv` |
| Remote - SSH | `ms-vscode-remote.remote-ssh` |
| Remote - SSH: Editing Configuration Files | `ms-vscode-remote.remote-ssh-edit` |
| ReUI | `barrsan.reui` |
| Scepter Theme | `isaacwilson.scepter` |
| Simple React Snippets | `burkeholland.simple-react-snippets` |
| Snapcode | `moyu.snapcode` |
| Spanish Language Pack for Visual Studio Code | `ms-ceintl.vscode-language-pack-es` |
| Spell Right | `ban.spellright` |
| SQL Bindings | `ms-mssql.sql-bindings-vscode` |
| SQL Database Projects | `ms-mssql.sql-database-projects-vscode` |
| SQL Server (mssql) | `ms-mssql.mssql` |
| SQL Viewer | `nei.sql-viewer` |
| SQLite | `alexcvzz.vscode-sqlite` |
| SQLite Viewer | `qwtel.sqlite-viewer` |
| SQLTools | `mtxr.sqltools` |
| SQLTools SQLite | `mtxr.sqltools-driver-sqlite` |
| SVG-Viewer | `dheovani.svg-viewer` |
| Tailwind CSS IntelliSense | `bradlc.vscode-tailwindcss` |
| Test Runner for Java | `vscjava.vscode-java-test` |
| Trailing Spaces | `shardulm94.trailing-spaces` |
| Unicode Latex | `oijaz.unicode-latex` |
| Version Lens | `pflannery.vscode-versionlens` |
| vscode-cython-annotate | `itaiin.vscode-cython-annotate` |
| vscode-icons-iconify | `lqyld.vscode-icons-iconify` |
| vscode-pdf | `tomoki1207.pdf` |
| vscode-pokemon | `jakobhoeg.vscode-pokemon` |
| vscode-spotify | `shyykoserhiy.vscode-spotify` |
| Zotero LaTeX | `bnavetta.zoterolatex` |

## Fuentes

- Manifiestos, traducciones y README de las extensiones instaladas en este equipo; los enlaces de cada fila abren su ficha del Marketplace.
- [Administración de extensiones de VS Code](https://code.visualstudio.com/docs/configure/extensions/extension-marketplace).
- [Perfiles de VS Code](https://code.visualstudio.com/docs/configure/profiles).
