# Revisión de almacenamiento de navegadores

Revisión de solo lectura: se midieron nombres, tamaños y estructura de archivos. No se abrió el contenido de contraseñas, cookies, historial ni bases de datos de sitios. No se eliminó ningún dato del navegador.

Los tamaños corresponden a datos de usuario, no a los ejecutables instalados. Las cachés cambian mientras se usan los navegadores.

| Navegador / ubicación | Total GiB | Caché web y de código MiB | Almacenamiento de sitios MiB |
|---|---:|---:|---:|
| Chrome | 1.96 | 797.9 | 107.6 |
| Brave | 4.53 | 1098.1 | 2710.8 |
| Edge | 2.07 | 566.8 | 559.1 |
| Opera GX (perfil) | 0.19 | 11.3 | 5.8 |
| Opera GX (local) | 0.03 | 23.0 | 0.0 |

Total de datos medidos: 8.77 GiB.
Candidato conservador de limpieza (solo Cache y Code Cache): 2.44 GiB.

## Interpretación

- Cache y Code Cache: copias descargadas y código procesado para acelerar las páginas. Son el candidato inicial de limpieza.
- Service Worker, IndexedDB, File System y almacenamiento local: pueden incluir datos persistentes y contenido para uso sin conexión. Requieren revisión aparte.
- Extensiones: son programas instalados en el navegador; no se consideran caché.
- Cookies, contraseñas, marcadores, historial, sesiones y configuraciones quedan fuera de la propuesta.
- Las cachés gráficas también quedan fuera de la propuesta. No se modifica NVIDIA.

En Brave, Service Worker/CacheStorage ocupa unos 1852 MiB y ScriptCache unos 65 MiB. Ambos quedan fuera del candidato conservador de 2,44 GiB para no confundir almacenamiento de aplicaciones web con caché convencional.

## Chrome

Ruta: `C:\Users\fabi7\AppData\Local\Google\Chrome\User Data`

### Cachés candidatas

| Ruta relativa | MiB |
|---|---:|
| System Profile/Code Cache | 0.0 |
| Profile 2/Code Cache | 45.0 |
| Profile 2/Cache | 163.9 |
| Profile 1/Code Cache | 46.0 |
| Profile 1/Cache | 104.5 |
| Default/Code Cache | 89.8 |
| Default/Cache | 348.6 |

### Distribución por carpetas y perfiles

| Ruta relativa | MiB |
|---|---:|
| Default/Extensions | 699.0 |
| Default/Cache | 348.6 |
| Profile 2/Cache | 163.9 |
| Profile 1/Cache | 104.5 |
| Default/Code Cache | 89.8 |
| extensions_crx_cache | 85.9 |
| Default/Service Worker | 71.1 |
| optimization_guide_model_store | 48.7 |
| Profile 1/Code Cache | 46.0 |
| Profile 2/Code Cache | 45.0 |
| Profile 2/Extensions | 41.0 |
| Profile 1/Extensions | 39.8 |
| Safe Browsing | 37.7 |
| component_crx_cache | 37.2 |
| WasmTtsEngine | 22.3 |
| Default/IndexedDB | 16.7 |
| GrShaderCache | 15.6 |
| Profile 2/Service Worker | 14.5 |
| OnDeviceHeadSuggestModel | 7.6 |
| Default/GPUCache | 5.6 |
| (archivos raíz) | 5.3 |
| Default/Sessions_Encrypted | 4.0 |
| Default/Sessions | 4.0 |
| BrowserMetrics | 4.0 |
| Default/Local Extension Settings | 3.9 |
| Default | 2.6 |
| Profile 2/IndexedDB | 2.6 |
| ActorSafetyLists | 2.5 |
| Default/Shared Dictionary | 2.5 |
| Profile 2/Storage | 1.7 |
| Profile 1/Storage | 1.7 |
| Default/Storage | 1.7 |
| hyphen-data | 1.7 |
| ZxcvbnData | 1.6 |
| ShaderCache | 1.6 |
| Profile 2/GPUCache | 1.6 |
| Profile 1/GPUCache | 1.6 |
| Profile 1 | 1.4 |
| CertificateRevocation | 1.3 |
| Profile 2 | 1.1 |
| OptimizationHints | 1.1 |
| Profile 1/IndexedDB | 1.1 |

## Brave

Ruta: `C:\Users\fabi7\AppData\Local\BraveSoftware\Brave-Browser\User Data`

### Cachés candidatas

| Ruta relativa | MiB |
|---|---:|
| Default/Code Cache | 715.8 |
| Default/Cache | 382.3 |

### Distribución por carpetas y perfiles

| Ruta relativa | MiB |
|---|---:|
| Default/Service Worker | 1917.4 |
| Default/Code Cache | 715.8 |
| Default/File System | 607.0 |
| Default/Cache | 382.3 |
| component_crx_cache | 172.2 |
| Default/Extensions | 157.4 |
| Default/IndexedDB | 149.9 |
| screen_ai | 116.2 |
| Default/Shared Dictionary | 89.5 |
| extensions_crx_cache | 78.4 |
| Default | 40.5 |
| Safe Browsing | 36.5 |
| Default/Local Storage | 30.6 |
| WidevineCdm | 21.9 |
| aoojcmojmmcbpfgoecoadbdpnagfchel | 18.7 |
| Default/GPUCache | 13.6 |
| GrShaderCache | 11.5 |
| Default/adblock_cache | 10.5 |
| OnDeviceHeadSuggestModel | 7.6 |
| Default/DawnWebGPUCache | 6.3 |
| (archivos raíz) | 6.1 |
| Default/Network | 5.1 |
| Default/Local Extension Settings | 5.1 |
| iodkpdagapdfkphljnddpjlldadblomo | 5.1 |
| Default/Sessions | 5.0 |
| Crashpad | 4.4 |
| Default/WebStorage | 3.4 |
| Default/Session Storage | 2.5 |
| Default/Sync Extension Settings | 2.3 |
| hyphen-data | 1.7 |
| fcggndnjiecfkiomngolonakcmagfomn | 1.7 |
| kihnoaefogbkmblfimmibknnmkllbhlf | 1.6 |
| ZxcvbnData | 1.6 |
| ShaderCache | 1.6 |
| cdbbhgbmjhfnhnmgeddbliobbofkgdhe | 1.5 |
| CertificateRevocation | 1.2 |

## Edge

Ruta: `C:\Users\fabi7\AppData\Local\Microsoft\Edge\User Data`

### Cachés candidatas

| Ruta relativa | MiB |
|---|---:|
| Default/Code Cache | 516.6 |
| Default/Cache | 50.2 |

### Distribución por carpetas y perfiles

| Ruta relativa | MiB |
|---|---:|
| Default/Code Cache | 516.6 |
| Default/Service Worker | 473.4 |
| Default/Extensions | 387.8 |
| component_crx_cache | 200.7 |
| ProvenanceData | 168.6 |
| Default/IndexedDB | 77.8 |
| Default/Cache | 50.2 |
| Default | 48.5 |
| Default/Shared Dictionary | 42.3 |
| Edge Entity Extraction | 19.5 |
| GrShaderCache | 15.6 |
| Edge Wallet | 14.1 |
| Subresource Filter | 11.3 |
| Default/EntityExtraction | 10.7 |
| Default/Local Storage | 6.6 |
| Default/DawnWebGPUCache | 5.9 |
| Default/GPUCache | 5.6 |
| Edge Shopping | 5.3 |
| Default/Local Extension Settings | 5.1 |
| (archivos raíz) | 5.0 |
| BrowserMetrics | 4.0 |
| EdgeLanguageDetectionModel | 3.2 |
| Default/Extension State | 2.8 |
| Default/EdgeCoupons | 2.6 |
| Speech Recognition | 2.6 |
| Default/Asset Store | 2.3 |
| Default/Network | 2.1 |
| Safe Browsing | 2.1 |
| Default/Sync Data | 1.7 |
| hyphen-data | 1.7 |
| Default/Storage | 1.7 |
| Default/Workspaces | 1.7 |
| ZxcvbnData | 1.6 |
| ShaderCache | 1.6 |
| Typosquatting | 1.4 |
| ProvenanceDataTensors | 1.4 |
| Default/WebStorage | 1.2 |
| Edge Sidebar | 1.2 |
| Default/Sessions | 1.2 |
| Edge Signal Triggers | 1.1 |

## Opera GX (perfil)

Ruta: `C:\Users\fabi7\AppData\Roaming\Opera Software\Opera GX Stable`

### Cachés candidatas

| Ruta relativa | MiB |
|---|---:|
| Default/Code Cache | 11.3 |

### Distribución por carpetas y perfiles

| Ruta relativa | MiB |
|---|---:|
| WidevineCdm | 43.5 |
| Safe Browsing | 36.5 |
| Default/Extensions | 25.4 |
| component_crx_cache | 24.8 |
| Default/Code Cache | 11.3 |
| (archivos raíz) | 10.9 |
| GrShaderCache | 7.9 |
| Default/Local Extension Settings | 6.1 |
| adblocker_data | 5.7 |
| Default/Service Worker | 4.7 |
| themes | 2.8 |
| MediaFoundationWidevineCdm | 2.7 |
| CertificateRevocation | 2.5 |
| Default | 2.1 |
| hyphen-data | 1.7 |

## Opera GX (local)

Ruta: `C:\Users\fabi7\AppData\Local\Opera Software\Opera GX Stable`

### Cachés candidatas

| Ruta relativa | MiB |
|---|---:|
| Default/Cache | 23.0 |

### Distribución por carpetas y perfiles

| Ruta relativa | MiB |
|---|---:|
| Default/Cache | 23.0 |
| Default/System Cache | 5.9 |

## Limpieza realizada posteriormente

Por autorización del usuario se eliminaron 18.641 archivos de las carpetas Cache y Code Cache inventariadas. No se omitieron archivos durante la eliminación. Se recuperaron aproximadamente 2,44 GiB netos. Se conservaron perfiles, datos de sitios, cookies, historial, credenciales, extensiones y cachés gráficas. Los tamaños del inventario anterior corresponden al estado previo a la limpieza.
