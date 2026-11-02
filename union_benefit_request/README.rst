===========================
Sindicato - Solicitudes
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

Módulo para la gestión de solicitudes y beneficios gremiales. Permite registrar
solicitudes de subsidios y beneficios escolares, hacer su seguimiento y
gestionar el ciclo de vida completo de cada pedido.

**Tabla de contenidos**

.. contents::
   :local:

Funcionalidades
===============

- Gestión de solicitudes con estados *Borrador*, *Solicitada*, *Autorizada*,
  *Rechazada*, *Finalizada* y *Cancelada*.
- Configuración de tipos de solicitud y de grupos de solicitudes.
- Gestión de beneficios escolares y de sus tipos, vinculados a los hijos del
  afiliado.
- Registro de montos solicitados, autorizados y pagados.
- Datos de seguimiento: fecha de solicitud, expediente/resolución,
  documentación completa, observaciones y responsable.
- Integración con encuestas (``survey``): la solicitud puede vincularse a una
  respuesta de encuesta.
- Importación de solicitudes con el importador estándar de Odoo.
- Grupos de seguridad de lectura, escritura y administración de solicitudes.

Instalación
===========

Para instalar el módulo:

1. Copie el módulo en un directorio de addons de Odoo.
2. Reinicie el servidor.
3. Vaya a **Aplicaciones**, actualice la lista y busque **Sindicato -
   Solicitudes**.
4. Haga clic en **Instalar**.

Dependencias
============

Este módulo depende de los siguientes módulos de Odoo:

- ``base``
- ``mail``
- ``survey``
- ``union_affiliation``

Configuración
=============

1. Navegue a **Sindicato > Solicitudes > Tipos de solicitud** para configurar
   los tipos de solicitud: estados de afiliado habilitados, si aplica a
   cotizantes, quién puede solicitarla, grupos y documentación requerida.
2. Navegue a **Sindicato > Solicitudes > Tipos de beneficios escolares** para
   configurar los tipos de beneficio escolar.

Uso
===

1. Navegue a **Sindicato > Solicitudes > Lista de solicitudes** para gestionar
   las solicitudes.
2. Navegue a **Sindicato > Solicitudes > Beneficios escolares** para gestionar
   en particular las solicitudes de beneficios escolares.
3. Abra una solicitud para registrar el tipo, el afiliado solicitante, el
   responsable, los montos y el expediente, y para avanzar su estado.
4. Para las solicitudes de beneficio escolar, agregue los hijos beneficiarios
   en la pestaña correspondiente; el sistema valida que sean hijos del
   afiliado.

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
