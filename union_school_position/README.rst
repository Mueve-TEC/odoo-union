===========================
Sindicato - Cargos
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

Módulo para la gestión de cargos de los afiliados. Registra los cargos
ocupados, su tipo, carácter, cantidad de horas, lugar de trabajo y fechas de
vigencia, y permite importarlos desde archivos.

**Tabla de contenidos**

.. contents::
   :local:

Funcionalidades
===============

- Gestión de cargos por afiliado.
- Configuración de tipos de cargo, con código, descripción y control por horas.
- Configuración de caracteres de cargo.
- Registro de número de cargo, cantidad de horas, sector, dedicación y
  observaciones.
- Fechas de vigencia del cargo (**Desde** y **Hasta**) y fecha de registro.
- Marcas de cargo destacado y etiquetas de cargo.
- Datos del lugar de trabajo por niveles, heredados del afiliado.
- Importación de cargos desde archivos CSV/XLSX con el importador estándar de
  Odoo, resolviendo el afiliado por legajo/UID, CUIT o documento.
- Grupos de seguridad de lectura, escritura y administración de cargos.

Instalación
===========

Para instalar el módulo:

1. Copie el módulo en un directorio de addons de Odoo.
2. Reinicie el servidor.
3. Vaya a **Aplicaciones**, actualice la lista y busque **Sindicato -
   Cargos**.
4. Haga clic en **Instalar**.

Dependencias
============

Este módulo depende de los siguientes módulos de Odoo:

- ``base``
- ``union_affiliation``

Configuración
=============

1. Navegue a **Sindicato > Cargos > Tipos de cargos** para configurar los
   tipos de cargo.
2. Navegue a **Sindicato > Cargos > Caracteres de cargos** para configurar los
   caracteres de cargo.

Uso
===

1. Navegue a **Sindicato > Cargos > Lista de cargos** para gestionar los
   cargos.
2. Cree un cargo indicando el afiliado, el tipo, el carácter, el número, las
   horas, el lugar de trabajo y las fechas de vigencia.
3. Para importar cargos, use **Favoritos > Importar registros** en la lista de
   cargos, mapee las columnas y valide con **Prueba** antes de **Importar**.

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
