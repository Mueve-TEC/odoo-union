# odoo-union

Repositorio de módulos de *Odoo* para la gestión y administración de sindicatos.
Desarrollados y mantenidos por [Mueve](https://www.mueve.org.ar/).

## Módulos

### Afiliados

Módulo base para la gestión de afiliados gremiales. Para más información ver
[union_affiliation/README.rst](union_affiliation/README.rst).

### Aportes

Módulo para la gestión de aportes y contribuciones de afiliados, con
importación y consulta de inconsistencias. Para más información ver
[union_contribution/README.rst](union_contribution/README.rst).

### Solicitudes

Módulo para la gestión de solicitudes y beneficios gremiales. Para más
información ver
[union_benefit_request/README.rst](union_benefit_request/README.rst).

### Cargos

Módulo para la gestión de cargos de afiliados y jerarquía laboral. Para más
información ver
[union_school_position/README.rst](union_school_position/README.rst).

## Requisitos

- Odoo Community 19.0.

## Instalación y desarrollo

### Clonar el repositorio localmente

```bash
git clone -b 19.0 git@github.com:Mueve-TEC/odoo-union.git
```

### Instalación de módulos para desarrollo

Seguir el procedimiento detallado en el
[repositorio del entorno de desarrollo](https://github.com/Mueve-TEC/soltec-localdev/).

## Documentación

- [MIGRATION_NOTES.md](MIGRATION_NOTES.md): notas de migración.
- [AUDIT.md](AUDIT.md): auditoría del repositorio.
- [TESTING.md](TESTING.md): guía de pruebas.

## Licencia

Consulte el campo `license` de cada módulo en su `__manifest__.py`
(`union_affiliation` es AGPL-3; el resto es GPL-3).

## Autores

- [Mueve](https://www.mueve.org.ar/)
