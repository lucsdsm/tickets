#!/bin/sh

set -e

echo "Entrypoint: Instalando dependências do Node..."
npm install

echo "Entrypoint: Iniciando o build do Tailwind CSS em modo watch..."

exec npm run build:css