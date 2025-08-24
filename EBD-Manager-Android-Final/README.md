# EBD Manager - Aplicativo Android

Este é o aplicativo Android para o sistema EBD Manager, criado usando WebView para carregar o sistema web.

## 📱 Características

- **WebView nativo** carregando o sistema EBD Manager
- **Splash screen** com logo da igreja
- **Pull-to-refresh** para recarregar
- **Controle de navegação** restrito ao domínio
- **Offline básico** com cache
- **Ícone personalizado** da igreja

## 🚀 Como Compilar

### Pré-requisitos
1. **Android Studio** instalado
2. **Android SDK** (API 21 ou superior)
3. **Java 8+** configurado

### Passos para Compilar

1. **Abrir no Android Studio:**
   ```bash
   # Abrir a pasta /app/android no Android Studio
   ```

2. **Configurar SDK Path:**
   - Edite `local.properties`
   - Configure o caminho do seu Android SDK:
   ```
   sdk.dir=/caminho/para/Android/Sdk
   ```

3. **Sincronizar Gradle:**
   - No Android Studio: `File → Sync Project with Gradle Files`

4. **Compilar APK:**
   ```bash
   # Via linha de comando
   ./gradlew assembleRelease
   
   # Ou no Android Studio
   Build → Generate Signed Bundle/APK → APK
   ```

5. **APK Gerado:**
   ```
   app/build/outputs/apk/release/app-release.apk
   ```

## 🔧 Configurações

### URL do Sistema
- **URL atual:** `https://ebd-dashboard-1.preview.emergentagent.com`
- **Para alterar:** Edite `MainActivity.java` → `BASE_URL`

### Logo e Ícones
- **Splash logo:** `res/drawable/logo_ebd.png`
- **Ícones do app:** `res/mipmap-*/ic_launcher.png`

### Cores e Tema
- **Cores:** `res/values/colors.xml`
- **Tema:** `res/values/themes.xml`

## 📦 Para Play Store

### Assinar APK
1. **Criar keystore:**
   ```bash
   keytool -genkey -v -keystore ebd-manager.keystore -alias ebd -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Assinar APK:**
   ```bash
   jarsigner -verbose -sigalg SHA1withRSA -digestalg SHA1 -keystore ebd-manager.keystore app-release.apk ebd
   ```

3. **Alinhar APK:**
   ```bash
   zipalign -v 4 app-release.apk EBD-Manager-v1.0.0.apk
   ```

### Informações da Play Store
- **Nome:** EBD Manager
- **Pacote:** com.ebd.manager
- **Versão:** 1.0.0 (código 1)
- **Categoria:** Produtividade
- **Idade:** +3 anos

## 🎯 Funcionalidades

### Navegação
- ✅ Carrega sistema web em WebView
- ✅ Splash screen de 2 segundos
- ✅ Pull-to-refresh
- ✅ Botão voltar funcional
- ✅ Confirmação para sair

### Segurança
- ✅ Navegação restrita ao domínio
- ✅ JavaScript habilitado
- ✅ Cache seguro
- ✅ Backup automático

### Performance
- ✅ Cache inteligente
- ✅ User Agent customizado
- ✅ Otimizações de WebView

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
android/
├── app/
│   ├── src/main/
│   │   ├── java/com/ebd/manager/
│   │   │   ├── MainActivity.java      # WebView principal
│   │   │   └── SplashActivity.java    # Tela splash
│   │   ├── res/
│   │   │   ├── layout/               # Layouts XML
│   │   │   ├── values/               # Cores, strings, temas
│   │   │   ├── drawable/             # Logo
│   │   │   └── mipmap-*/             # Ícones
│   │   └── AndroidManifest.xml       # Configurações do app
│   └── build.gradle                  # Dependências
├── build.gradle                      # Configuração global
├── settings.gradle                   # Módulos
└── README.md                         # Este arquivo
```

### Modificações Futuras
- Para alterar URL: `MainActivity.java` → `BASE_URL`
- Para alterar cores: `res/values/colors.xml`
- Para alterar splash: `res/layout/activity_splash.xml`

## 📱 Testando

1. **Instalar APK:**
   ```bash
   adb install EBD-Manager-v1.0.0.apk
   ```

2. **Testar funcionalidades:**
   - ✅ Splash screen aparece
   - ✅ Sistema carrega corretamente
   - ✅ Login funciona
   - ✅ Pull-to-refresh funciona
   - ✅ Botão voltar funciona
   - ✅ Sair do app funciona

## 🎨 Customização

O app foi criado com as cores e logo da igreja. Para personalizar:

1. **Logo da igreja:** Substitua `logo_ebd.png`
2. **Ícones:** Substitua arquivos `ic_launcher.png`
3. **Cores:** Edite `colors.xml`
4. **Nome:** Edite `strings.xml`

---

## 📞 Suporte

Este app é um WebView wrapper do sistema EBD Manager web. Todas as funcionalidades vêm do sistema web original.

**Versão:** 1.0.0  
**Compilado:** Android Studio  
**Compatibilidade:** Android 5.0+ (API 21+)