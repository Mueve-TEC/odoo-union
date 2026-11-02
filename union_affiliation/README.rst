===========================
Sindicato - Afiliaciones
===========================

.. |badge1| image:: https://img.shields.io/badge/maturity-Production%2FStable-green.png
    :target: https://odoo-community.org/page/development-status
    :alt: Production/Stable
.. |badge2| image:: https://img.shields.io/badge/license-AGPL--3-blue.png
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-odoo--union-lightgray.png?logo=github
    :target: https://github.com/Mueve-TEC/odoo-union
    :alt: Mueve

|badge1| |badge2| |badge3|

Módulo base para la gestión de afiliados gremiales. Administra los datos
personales, de contacto y laborales de los afiliados, sus periodos de
afiliación, los lugares de trabajo y los tipos de relación laboral.

Este módulo es la base de los demás módulos del repositorio
(`union_contribution`, `union_benefit_request` y `union_school_position`).

**Tabla de contenidos**

.. contents::
   :local:

Funcionalidades
===============

- Gestión de afiliados:
    - Datos personales (tipo y número de documento, género, estado civil,
      fecha y país de nacimiento).
    - Datos de contacto y domicilio (hereda de contactos de Odoo).
    - Datos laborales y lugar de trabajo.
    - Legajo/UID del afiliado, con control de unicidad y validación de valores
      positivos.
    - Estado del afiliado y marca de *Cotizante* (contribuyente).
- Gestión de periodos de afiliación y bajas, con control de fechas.
- Lugares de trabajo jerárquicos (con nombre completo por nivel).
- Tipos de relación laboral.
- Hijos u otros familiares a cargo del afiliado.
- Listado de correos electrónicos de afiliados.
- Importación de afiliados desde archivos CSV/XLSX con el importador estándar
  de Odoo, incluyendo el manejo permisivo de fechas de versiones anteriores.
- Baja de lugares de trabajo con un asistente que advierte los afiliados y
  lugares dependientes afectados antes de eliminar.
- Grupos de seguridad de lectura, escritura, administración, cambio de estado,
  cambio de cotización y acceso a correos.

Instalación
===========

Para instalar el módulo:

1. Copie el módulo en un directorio de addons de Odoo.
2. Reinicie el servidor.
3. Vaya a **Aplicaciones**, actualice la lista y busque **Sindicato -
   Afiliaciones**.
4. Haga clic en **Instalar**.

Dependencias
============

Este módulo depende de los siguientes módulos de Odoo:

- ``base``
- ``mail``
- ``base_import``

Configuración
=============

Ir a **Sindicato > Configuración > Configuración de afiliación** para definir:

- **Habilitar secuencia de número de afiliado** y el próximo número.
- **Permitir editar el número de afiliado** en la vista de alta.
- **Inicio de la afiliación**: al afiliar o al confirmar la afiliación.
- **Fin de la afiliación**: al desafiliar o al confirmar la desafiliación.

Los tipos de relación laboral se configuran en **Sindicato > Afiliados > Tipos
de relación laboral**.

Uso
===

1. Navegue a **Sindicato > Afiliados > Lista de afiliados** para gestionar los
   afiliados.
2. Use **Sindicato > Afiliados > Correos de afiliados** para consultar el
   listado de correos.
3. Use **Sindicato > Afiliados > Hijos de afiliados** para gestionar los
   familiares a cargo.
4. Use **Sindicato > Afiliados > Lugares de trabajo** para administrar los
   lugares de trabajo.
5. Para importar afiliados, use **Favoritos > Importar registros** en la lista
   de afiliados y siga el asistente del importador estándar.

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
