# Azure Resource Explorer Script

Este script en Python permite explorar recursos de Azure desde línea de comandos de forma interactiva.

## 🎯 Funcionalidades

- Listar todas las suscripciones a las que el usuario tiene acceso.
- Seleccionar una suscripción y un Resource Group.
- Visualizar recursos como:
  - Clusters AKS
  - Máquinas Virtuales
  - Storage Accounts
  - App Services
  - IPs Públicas
  - Redis Caches
  - CosmosDB
- Guardar logs de las acciones en:
  - `session_log.json` (estructurado)
  - `session_log.txt` (legible)

## ⚙ Requisitos

- Python 3.7+
- Azure CLI (`az`) instalado y autenticado (`az login`)
- (Opcional) `kubectl` si deseas conectarte a AKS

## 🚀 Ejecución

```bash
python connect_aks.py
Importante: si ejecutas en Windows, revisa la ruta de az.cmd en la variable AZ_PATH al inicio del script.