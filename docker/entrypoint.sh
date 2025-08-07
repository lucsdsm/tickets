#!/bin/sh
set -e

echo "Entrypoint: Instalando dependências do Node..."
npm install

echo "Entrypoint: Gerando build inicial e único do CSS..."
npm run build

echo "Entrypoint: Iniciando o Tailwind em modo watch para futuras alterações..."
exec npm run watch