===========================
Sindicato - Aportes
===========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Production%2FStable-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable
.. |badge2| image:: https://img.shields.io/badge/license-GPL--3-blue.png
    :target: https://www.gnu.org/licenses/gpl-3.0-standalone.html
    :alt: License: GPL-3
.. |badge3| image:: https://img.shields.io/badge/github-odoo--union-lightgray.png?logo=github
    :target: https://github.com/Mueve-TEC/odoo-union
    :alt: Mueve

|badge1| |badge2| |badge3|

Módulo para la gestión de aportes y contribuciones de los afiliados. Permite
registrar aportes, importarlos desde archivos y detectar inconsistencias entre
los afiliados que deberían aportar y los aportes efectivamente registrados.

**Tabla de contenidos**

.. contents::
   :local:

Funcionalidades
===============

- Gestión de aportes por afiliado, fecha, código y monto.
- Configuración de códigos de aportes.
- Importación de aportes desde archivos CSV/XLSX con el importador estándar de
  Odoo, incluyendo la resolución del afiliado por legajo/UID, CUIT o documento.
- Opción para crear afiliados automáticamente durante la importación de
  aportes.
- Consulta de inconsistencias: detecta afiliados cotizantes sin aportes y no
  cotizantes con aportes en un período.
- Filtros de la consulta por período, tipo de relación laboral y código de
  aporte.
- Resultados de las consultas con historial y asistente para cambiar el estado
  del afiliado.
- Grupos de seguridad de lectura, escritura y administración de aportes e
  inconsistencias.

Instalación
===========

Para instalar el módulo:

1. Copie el módulo en un directorio de addons de Odoo.
2. Reinicie el servidor.
3. Vaya a **Aplicaciones**, actualice la lista y busque **Sindicato -
   Aportes**.
4. Haga clic en **Instalar**.

Dependencias
============

Este módulo depende de los siguientes módulos de Odoo:

- ``base``
- ``union_affiliation``

Configuración
=============

1. Navegue a **Sindicato > Aportes > Códigos de aportes** para configurar los
   códigos de aportes.
2. Navegue a **Sindicato > Configuración > Configuración de afiliación** y
   active la opción para crear afiliados al importar aportes, si corresponde.

Uso
===

Aportes
-------

1. Navegue a **Sindicato > Aportes > Lista de aportes** para gestionar los
   aportes.

Importación
-----------

1. Navegue a **Sindicato > Aportes > Lista de aportes**, abra **Favoritos** y
   seleccione **Importar registros**.
2. Suba el archivo CSV/XLSX con los aportes.
3. Mapee las columnas del archivo a los campos de Odoo: **Código**, **Fecha**,
   **Legajo (importación)**, **Monto** y los campos de identificación que
   correspondan (UID, CUIT o documento).
4. Configure el formato de fecha, separador de miles y de decimales del archivo
   en la pestaña **Formato**.
5. Presione **Prueba** para validar la configuración y luego **Importar**.

Inconsistencias
---------------

1. Navegue a **Sindicato > Aportes > Consulta de inconsistencias**.
2. Ingrese una descripción para identificar la consulta.
3. Configure el período, el tipo de relación laboral y el código de aporte.
4. Seleccione si la consulta busca aportantes sin aportes, no aportantes con
   aportes, o ambos.
5. Presione **CONSULTA DE INCONSISTENCIAS**.
6. Consulte los resultados en **Sindicato > Aportes > Lista de
   inconsistencias**.

Créditos
========

Autor
-----

Este módulo fue desarrollado por:

- Mueve (https://www.mueve.org.ar/)

Mantenedores
------------

Este módulo es mantenido por:

- Mueve (https://www.mueve.org.ar/)

Para contribuir a este módulo, visite https://github.com/Mueve-TEC/odoo-union.
