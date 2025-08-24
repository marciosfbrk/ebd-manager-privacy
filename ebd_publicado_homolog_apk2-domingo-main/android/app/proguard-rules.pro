# EBD Manager - Proguard Rules

# Keep WebView JavaScript interface
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}

# Keep WebView classes
-keep class android.webkit.** { *; }
-keep class androidx.webkit.** { *; }

# Keep application classes
-keep class com.ebd.manager.** { *; }

# General Android optimizations
-dontwarn org.apache.http.**
-dontwarn android.net.http.AndroidHttpClient
-dontwarn com.google.android.maps.**
-dontwarn com.android.volley.toolbox.**