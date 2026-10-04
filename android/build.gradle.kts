// Top-level build file where you can add configuration options common to all sub-projects/modules.
plugins {
    alias(libs.plugins.android.application) apply false
}

// Pasta de build fora do projeto (opcional): quem mantém o repositório numa pasta
// sincronizada (OneDrive) tem o build quebrado por "Unable to delete directory",
// porque o sincronizador trava os arquivos intermediários. Defina, por exemplo,
// ALAGAMENTOS_BUILD_DIR=C:\gradle-build\alagamentos. Sem a variável, nada muda.
System.getenv("ALAGAMENTOS_BUILD_DIR")?.let { base ->
    allprojects {
        layout.buildDirectory.set(file("$base/${project.name}"))
    }
}