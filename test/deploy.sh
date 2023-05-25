#!/bin/bash
docker pull postgres:13
docker stack deploy -c docker-compose.yml Odoo_desarrollo
