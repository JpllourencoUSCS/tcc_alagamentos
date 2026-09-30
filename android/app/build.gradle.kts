import java.util.Properties

plugins {
    alias(libs.plugins.android.application)
}

// Chaves locais (local.properties não vai para o repositório)
val localProps = Properties().apply {
    val arquivo = rootProject.file("local.properties")
    if (arquivo.exists()) arquivo.inputStream().use { load(it) }
}

android {
    namespace = "com.example.alagamentos"
    compileSdk {
        version = release(37)
    }

    defaultConfig {
        applicationId = "com.example.alagamentos"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        manifestPlaceholders["MAPS_API_KEY"] = localProps.getProperty("MAPS_API_KEY", "")

        // Endereço da API FastAPI do backend (tcc_alagamentos/backend, "uvicorn main:app").
        // Padrão: 10.0.2.2 = localhost do computador visto de dentro do emulador.
        // Para outro endereço, defina API_BASE_URL no local.properties.
        val apiBaseUrl = localProps.getProperty("API_BASE_URL", "http://10.0.2.2:8000/")
        buildConfigField("String", "API_BASE_URL", "\"${apiBaseUrl.trimEnd('/')}/\"")
    }

    buildTypes {
        debug {
            // Backend local roda em HTTP (sem TLS) durante o desenvolvimento
            manifestPlaceholders["usesCleartextTraffic"] = "true"
        }
        release {
            manifestPlaceholders["usesCleartextTraffic"] = "false"
            optimization {
                enable = false
            }
        }
    }
    buildFeatures {
        buildConfig = true
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
        // java.time (datas ISO 8601 da API) em aparelhos com API < 26
        isCoreLibraryDesugaringEnabled = true
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.material)
    implementation(libs.retrofit)
    implementation(libs.retrofit.converter.gson)
    coreLibraryDesugaring(libs.desugar.jdk.libs)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)
    implementation("com.google.android.gms:play-services-maps:18.2.0")
}