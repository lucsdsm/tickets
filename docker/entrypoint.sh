#!/bin/sh
set -e

echo "Entrypoint: Instalando dependências..."
npm install

echo "Entrypoint: Gerando build inicial do CSS..."
npm run build

echo "Entrypoint: Iniciando reconstrução contínua do CSS..."

while true; do
  npm run build
  sleep 2
done