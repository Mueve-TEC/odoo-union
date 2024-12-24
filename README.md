
# clonar el repo localmente

git clone -b 16.0 git@gitlab.mueve.net.ar:odoo-mueve/odoo-union.git



# copiar los módulos 

cp -R odoo-union/affiliation soltec-localdev/custom-addons/

cp -R odoo-union/benefit_request soltec-localdev/custom-addons/

cp -R odoo-union/school_position soltec-localdev/custom-addons/

cp -R odoo-union/contribution soltec-localdev/custom-addons/

cp -R odoo-union/butterlog/ soltec-localdev/custom-addons/



# Descargar los módulos complementarios de los que depende aportes 

https://apps.odoo.com/apps/modules/16.0/import_ignore_error

https://apps.odoo.com/apps/modules/16.0/web_notify


descomprimir y copiar la carpeta correspondiente al módulo en addons


# Seguir el procedimiento indicado en el repo https://github.com/Mueve-TEC/soltec-localdev

luego 

docker-compose build --no-cache

docker-compose up -d
