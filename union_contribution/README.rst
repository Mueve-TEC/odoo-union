===========================
Sindicato - Aportes
===========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Production%2FStable-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable
.. |badge2| image:: https://img.shields.io/badge/license-GPL--3-blue.png
    :target: http://www.gnu.org/licenses/gpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-union-lightgray.png?logo=github
    :target: https://github.com/Mueve-TEC
    :alt: Mueve

|badge1| |badge2| |badge3|

Módulo para gestión de aportes/contribuciones de afiliados.

Características
===============

- Gestión de aportes.
- Importación de aportes desde archivos csv.
- Creación de afiliados a partir de la importación de aportes.
- Busqueda de inconsistencias en los aportes de afiliados.

Instalación
===========

Para instalar este módulo, debe seguir los siguientes pasos:

1. Descargue el módulo y colóquelo en el directorio de addons de Odoo.
2. Reinicie el servidor de Odoo.
3. Vaya a **Apps** en el menú de Odoo.
4. Busque `union_contribution`.
5. Haga clic en **Instalar**.

Dependencias
============

Este módulo depende de los siguientes módulos de Odoo:

- `base`
- `union_affiliation`

Uso
===

1. Navega a **Sindicato > Aportes > Códigos de aportes** para configurar los códigos de aportes.
2. Navega a **Sindicato > Solicitudes > Lista de aportes** para gestionar los aportes.

Importación
-----------

1. Navega a **Sindicato > Configuración > Configuración de afiliación** para seleccionar si crear nuevos afiliados o no al importar.
2. Navega a **Sindicato > Aportes > Lista de aportes**, luego presiona en **Favoritos** y selecciona **Importar registros**.
3. Sube el archivo csv con los aportes.
4. Completa bien los campos de Odoo "Código", "Fecha", "Legajo (importación)", "Monto" y los necesarios para corresponder las columnas de tu archivo .csv de aportes.
5. Completa el formato de la fecha, separador de miles y de decimales utilizados en el .csv en la pestaña de la izquierda de **Formato**.
6. Presiona **Prueba** para chequear que todo esté configurado correctamente.
7. Presiona **Importar** para importar los aportes.

inconsistencias
---------------

1. Presiona en **Sindicato > Aportes > Consulta de inconsistencias** para realizar una búsqueda de inconsistencias en los aportes de los afiliados.
2. Añade una descripción para identificar la búsqueda.
3. Configura los filtros de búsqueda, el período, el tipo de relación laboral.
4. Selecciona si la búsqueda es sobre los que tienen aportes o los que no tienen.
5. Presiona **CONSULTA DE INCONSISTENCIAS** para realizar la búsqueda.
6. Observa los resultados de todas las búsquedas en **Sindicato > Aportes > Lista de inconsistencias**.

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
