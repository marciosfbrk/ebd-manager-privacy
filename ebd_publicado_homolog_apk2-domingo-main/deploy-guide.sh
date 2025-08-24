#!/bin/bash

echo "🚀 Preparando deploy do App EBD..."

# Opção 1: Deploy no Vercel
echo ""
echo "=== OPÇÃO 1: VERCEL (Recomendado) ==="
echo "1. Instale Vercel CLI: npm i -g vercel"
echo "2. Na pasta /app/frontend execute: vercel"
echo "3. Siga as instruções (primeira vez)"
echo "4. Para redeploy: vercel --prod"
echo ""

# Opção 2: Deploy no Netlify
echo "=== OPÇÃO 2: NETLIFY ==="
echo "1. Acesse: https://netlify.com"
echo "2. Drag & drop a pasta 'build' no site"
echo "3. Ou conecte GitHub e auto-deploy"
echo ""

# Opção 3: Deploy no Railway
echo "=== OPÇÃO 3: RAILWAY (Full-stack) ==="
echo "1. Acesse: https://railway.app"
echo "2. Connect GitHub repository"
echo "3. Deploy automático com backend"
echo ""

echo "✅ Build pronto em: /app/frontend/build"
echo "✅ PWA configurada"
echo "✅ Pronto para deploy!"

# Mostrar arquivos importantes
echo ""
echo "📁 Arquivos PWA criados:"
echo "  ✓ manifest.json"
echo "  ✓ sw.js (Service Worker)"
echo "  ✓ icons/ (8 tamanhos diferentes)"
echo "  ✓ Meta tags no index.html"