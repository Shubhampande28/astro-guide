import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.jyotishguru.app"
    compileSdk = 36

    defaultConfig {
        applicationId = "com.jyotishguru.app"
        minSdk = 26
        targetSdk = 36
        versionCode = 1
        versionName = "0.1.0"
    }

    buildTypes {
        debug {
            // 10.0.2.2 is the Android emulator's alias for the host
            // machine's localhost, where the backend runs via Docker
            // Compose. Cleartext HTTP to this address only is allowed by
            // src/debug/res/xml/network_security_config.xml (A2).
            buildConfigField("String", "API_BASE_URL", "\"http://10.0.2.2:8000/\"")
        }
        release {
            isMinifyEnabled = false
            // TODO(DECISIONS.md A2): replace with the real production API
            // host once it exists. Release builds never allow cleartext.
            buildConfigField("String", "API_BASE_URL", "\"https://api.jyotishguru.app/\"")
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

kotlin {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_17)
    }
}

dependencies {
    // Pinned one notch below each library's absolute latest: the newest
    // patches of core-ktx/compose/lifecycle now require compileSdk 37 and
    // AGP 9.1+, and this project deliberately stays on the AGP 8.x line
    // (compileSdk 36) rather than taking on the AGP 9 migration as part of
    // this pass -- see DECISIONS.md.
    implementation("androidx.core:core-ktx:1.18.0")
    // Back-compat per-app language support (A6): AppCompatDelegate works
    // app-wide even though this app otherwise uses plain ComponentActivity.
    implementation("androidx.appcompat:appcompat:1.8.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.10.0")
    implementation("androidx.activity:activity-compose:1.12.4")
    implementation("androidx.core:core-splashscreen:1.2.0")

    val composeBom = platform("androidx.compose:compose-bom:2026.06.01")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-core")
    implementation("androidx.navigation:navigation-compose:2.9.8")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.10.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.10.0")

    implementation("com.squareup.retrofit2:retrofit:2.11.0")
    implementation("com.squareup.retrofit2:converter-gson:2.11.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Replaces androidx.security:security-crypto (alpha, deprecated -- A4):
    // tokens are now AES/GCM-encrypted with an Android Keystore key and
    // stored as base64 in a Preferences DataStore. See DECISIONS.md.
    implementation("androidx.datastore:datastore-preferences:1.3.0")

    testImplementation("junit:junit:4.13.2")
}
