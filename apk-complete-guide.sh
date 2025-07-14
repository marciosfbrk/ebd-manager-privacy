#!/bin/bash

echo "📱 GUIA COMPLETO PARA GERAR APK - App EBD"
echo "=========================================="
echo ""

echo "🎯 PASSO 1: DEPLOY DA PWA (Teste imediato no Android)"
echo "------------------------------------------------"
echo "1. Suba sua app online primeiro"
echo "2. Use uma das opções:"
echo "   • Vercel: https://vercel.com (mais fácil)"
echo "   • Netlify: https://netlify.com (drag & drop)"
echo "   • Railway: https://railway.app (full-stack)"
echo ""
echo "RESULTADO: PWA instalável no Android"
echo ""

echo "📦 PASSO 2: APK NATIVO PARA PLAY STORE"
echo "--------------------------------------"
echo "PRÉ-REQUISITOS:"
echo "  ✓ Node.js instalado"
echo "  ✓ Android Studio instalado"
echo "  ✓ Java JDK 11+ instalado"
echo "  ✓ Sua app online (do Passo 1)"
echo ""

echo "COMANDOS PARA EXECUTAR NA SUA MÁQUINA:"
echo "-------------------------------------"
cat << 'EOF'

# 1. Instalar Capacitor
npm install -g @capacitor/cli

# 2. Na pasta do seu projeto React
cd pasta-do-seu-projeto-react
npm install @capacitor/core @capacitor/android

# 3. Inicializar Capacitor
npx cap init "App EBD" "com.ministeriobelém.appebd"

# 4. Fazer build do React
npm run build

# 5. Adicionar plataforma Android
npx cap add android

# 6. Sincronizar arquivos
npx cap sync android

# 7. Abrir no Android Studio
npx cap open android

# 8. No Android Studio:
#    - Build > Generate Signed Bundle/APK
#    - Escolha APK
#    - Crie keystore file
#    - Build Release APK

EOF

echo ""
echo "📋 ARQUIVOS QUE JÁ CRIEI PARA VOCÊ:"
echo "  ✅ manifest.json (configuração PWA)"
echo "  ✅ sw.js (service worker offline)"
echo "  ✅ icons/ (ícones em 8 tamanhos)"
echo "  ✅ Meta tags PWA no index.html"
echo "  ✅ Build otimizado em /frontend/build"
echo ""

echo "🎯 RECOMENDAÇÃO:"
echo "1. PRIMEIRO: Deploy PWA (5 min) → Teste no Android"
echo "2. DEPOIS: APK nativo (30 min) → Play Store"
echo ""

echo "📱 TESTE PWA NO ANDROID:"
echo "1. Acesse sua URL pelo Chrome Android"
echo "2. Menu ⋮ → 'Adicionar à tela inicial'"
echo "3. Funciona como app nativo!"
echo ""

echo "🆘 PRECISA DE AJUDA?"
echo "Me diga qual parte quer fazer primeiro:"
echo "  • 'deploy' → Para subir PWA online"
echo "  • 'apk' → Para gerar APK nativo"
echo "  • 'ambos' → Guia completo"