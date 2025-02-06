# odoo-union

Repositorio de módulos de *Odoo* para gestión y administración de sindicatos.

## Módulos

### Afiliados

Módulo dirigido a la gestión de afiliados gremiales. Para más información ver [union_affiliation/README.rst](/union_affiliation/README.rst).

### Aportes

Módulo para gestión de aportes/contribuciones de afiliados. Para más información ver [union_contribution/README.rst](/union_contribution/README.rst).

### Solicitudes

Módulo para la gestion de solicitudes y beneficios gremiales. Para más información ver [union_benefit_request/README.rst](/union_benefit_request/README.rst).

### Cargos

Módulo para la gestión de cargos de afiliados y jeraquía laboral. Para más información ver [union_school_position/README.rst](/union_school_position/README.rst)

## Instalación y desarrollo

### Clonar el repo localmente

```bash
git clone -b 16.0 git@gitlab.mueve.net.ar:odoo-mueve/odoo-union.git
```

### Instalación de módulos para desarrollo

Seguir el procedimiento detallado en el [repositorio](https://github.com/Mueve-TEC/soltec-localdev/) del entorno de desarrollo.

### Dependendencia de módulos complementarios

El módulo `contribution`, para la gestión de aportes, necesita de los módulos `import_ignore_error` y `web_notify` para su instalación y uso.

Estos módulos fueron descargados de los siguientes links:

- [import_ignore_error](https://apps.odoo.com/apps/modules/16.0/import_ignore_error)
- [web_notify](<https://apps.odoo.com/apps/modules/16.0/web_notify>)
