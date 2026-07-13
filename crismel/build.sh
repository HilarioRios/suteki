#!/bin/bash
# Construye el sitio: copia la página y descarga los videos al mismo dominio
set -e
mkdir -p dist
cp index.html dist/
curl -fsSL -o dist/reply.mp4 "https://raw.githubusercontent.com/HilarioRios/suteki/b33f33d9374e0ba39e91dad0bad6dc940ba943ea/crismel/reply.mp4"
curl -fsSL -o dist/love.mp4 "https://raw.githubusercontent.com/HilarioRios/suteki/b33f33d9374e0ba39e91dad0bad6dc940ba943ea/crismel/love.mp4"
echo "Build listo: $(ls -la dist)"
