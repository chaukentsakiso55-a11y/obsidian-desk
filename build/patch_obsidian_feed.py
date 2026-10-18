from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def replace_once(path, old, new):
    p = root / path
    text = p.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected block not found in {path}")
    if text.count(old) != 1:
        raise SystemExit(f"Expected exactly one match in {path}, found {text.count(old)}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")

runtime = "app/android/app/src/main/kotlin/com/orailnoor/droiddesk/runtime/LinuxRuntime.kt"

replace_once(
    runtime,
    '''        val boundedCommand = if (cmd.startsWith("dpkg --configure")) {
            "timeout --signal=TERM --kill-after=5s 90s $cmd"
        } else {
            cmd
        }
''',
    '''        val boundedCommand = when {
            cmd.startsWith("dpkg --configure") ->
                "timeout --signal=TERM --kill-after=5s 90s $cmd"
            cmd.startsWith("pkg install") ||
                cmd.startsWith("pkg update") ||
                cmd.startsWith("apt-get update") ->
                "timeout --signal=TERM --kill-after=15s 300s $cmd || { sleep 2; timeout --signal=TERM --kill-after=15s 300s $cmd; }"
            else -> cmd
        }
''',
)

helper = r'''
    private fun fetchObsidianFeedText(relativePath: String): String? {
        return runCatching {
            val safePath = relativePath.trimStart('/')
            val url = java.net.URL(
                "https://raw.githubusercontent.com/chaukentsakiso55-a11y/obsidian-desk/main/$safePath"
            )
            val connection = url.openConnection() as java.net.HttpURLConnection
            connection.connectTimeout = 12_000
            connection.readTimeout = 25_000
            connection.instanceFollowRedirects = true
            connection.setRequestProperty("User-Agent", "ObsidianDesk/0.2")
            try {
                if (connection.responseCode !in 200..299) return@runCatching null
                connection.inputStream.bufferedReader().use { it.readText() }
            } finally {
                connection.disconnect()
            }
        }.getOrNull()
    }

    private fun obsidianPackageList(name: String, fallback: String): String {
        val remote = fetchObsidianFeedText("essentials/packages/$name.txt")
            ?.lineSequence()
            ?.map { it.substringBefore('#').trim() }
            ?.filter { it.isNotEmpty() }
            ?.flatMap { it.split(Regex("\\s+")).asSequence() }
            ?.toList()
            .orEmpty()

        if (remote.isEmpty()) return fallback
        if (remote.any { !it.matches(Regex("[a-z0-9][a-z0-9+.-]{0,127}")) }) {
            Log.w(TAG, "Rejected invalid package name from Obsidian essentials feed")
            return fallback
        }
        return remote.distinct().joinToString(" ")
    }

    private fun writeObsidianBundledAppLauncher(appId: String) {
        val spec = when (appId) {
            "ember" -> Triple("obsidian-ember", "/root/Applications/Ember/main.py", "Ember")
            "mark54" -> Triple("obsidian-mark54", "/root/Applications/MarkLIV/main.py", "Mark LIV")
            else -> return
        }
        val launcher = File(binDir, spec.first)
        launcher.writeText(
            """
            #!\${File(binDir, "bash").absolutePath}
            export DISPLAY="\${'$'}{DISPLAY:-:0}"
            export TMPDIR="\${tmpDir.absolutePath}"
            mkdir -p "\${tmpDir.absolutePath}/proot"
            exec "\${File(binDir, "proot-distro").absolutePath}" login debian \
                --bind "\${tmpDir.absolutePath}:/tmp" \
                --env PROOT_TMP_DIR="\${tmpDir.absolutePath}/proot" \
                --env PROOT_LOADER="\${File(prefixDir, "libexec/proot/loader").absolutePath}" \
                --env PROOT_LOADER_32="\${File(prefixDir, "libexec/proot/loader32").absolutePath}" -- \
                env DISPLAY="\${'$'}DISPLAY" HOME=/root python3 "\${spec.second}"
            """.trimIndent() + "\n",
        )
        launcher.setExecutable(true, false)

        val desktopDir = File(prefixDir, "share/applications").apply { mkdirs() }
        File(desktopDir, "\${spec.first}.desktop").writeText(
            """
            [Desktop Entry]
            Type=Application
            Name=\${spec.third}
            Comment=Obsidian Desk bundled application
            Exec=\${launcher.absolutePath}
            Icon=applications-development
            Terminal=false
            Categories=Utility;
            """.trimIndent() + "\n",
        )
        refreshDesktopMenus()
    }

    private fun installObsidianBundledApp(
        appId: String,
        onProgress: ((Double, String) -> Unit)? = null,
    ): Boolean {
        val feedId = when (appId) {
            "ember" -> "ember"
            "mark54" -> "mark54"
            else -> return false
        }

        if (!isMinimalDebianInstalled()) {
            onProgress?.invoke(
                0.08,
                "Preparing Debian compatibility for \${if (appId == "ember") "Ember" else "Mark LIV"}...",
            )
            val debianReady = installMinimalDebian { progress, status ->
                val scaled = if (progress < 0) progress else 0.08 + progress * 0.34
                onProgress?.invoke(scaled, status)
            }
            if (!debianReady) return false
        }

        onProgress?.invoke(0.46, "Downloading verified installer from Obsidian Desk...")
        val installerText = fetchObsidianFeedText("essentials/apps/$feedId/install.sh")
            ?: return false
        if (!installerText.startsWith("#!/bin/bash") || installerText.length < 80) {
            Log.e(TAG, "Rejected invalid Obsidian app installer for $appId")
            return false
        }

        val installer = File(tmpDir, "obsidian-$feedId-install.sh")
        installer.writeText(installerText)
        installer.setExecutable(true, false)
        File(tmpDir, "proot").mkdirs()

        onProgress?.invoke(
            0.58,
            "Installing \${if (appId == "ember") "Ember" else "Mark LIV"}...",
        )
        val proot = File(binDir, "proot-distro")
        val command = """
            "\${proot.absolutePath}" login debian \
                --bind "\${tmpDir.absolutePath}:/tmp" \
                --env PROOT_TMP_DIR="\${tmpDir.absolutePath}/proot" \
                --env PROOT_LOADER="\${File(prefixDir, "libexec/proot/loader").absolutePath}" \
                --env PROOT_LOADER_32="\${File(prefixDir, "libexec/proot/loader32").absolutePath}" -- \
                bash "/tmp/\${installer.name}"
        """.trimIndent().replace("\n", " ")

        val output = executeCommand(
            "timeout --signal=TERM --kill-after=20s 900s $command",
        )
        installer.delete()
        if (output.startsWith("Error:")) return false

        writeObsidianBundledAppLauncher(appId)
        val launcherName = if (appId == "ember") "obsidian-ember" else "obsidian-mark54"
        return File(binDir, launcherName).canExecute()
    }

'''

replace_once(
    runtime,
    '''    fun installDesktopEnvironmentNative(
        desktopEnv: String = "xfce4",
''',
    helper + '''    fun installDesktopEnvironmentNative(
        desktopEnv: String = "xfce4",
''',
)

replace_once(
    runtime,
    '''        if (!installPackageGroup("pkg install -y xorg-xrandr pulseaudio xclip xkeyboard-config")) {
            Log.e(TAG, "Native X11 runtime package install failed")
            return false
        }
''',
    '''        val runtimePackages = obsidianPackageList(
            "runtime",
            "xorg-xrandr pulseaudio xclip xkeyboard-config",
        )
        if (!installPackageGroup("pkg install -y $runtimePackages")) {
            Log.e(TAG, "Native X11 runtime package install failed")
            return false
        }
''',
)

replace_once(
    runtime,
    '''        val desktopPackages = when (selectedDesktop) {
            "lxqt" -> "lxqt qterminal pcmanfm-qt featherpad"
            "mate" -> "mate mate-terminal gvfs mate-applets"
            "kde" -> "plasma-desktop konsole dolphin"
            else -> "xfce4 xfce4-terminal xfce4-whiskermenu-plugin xfce4-notifyd thunar mousepad"
        }
''',
    '''        val desktopPackages = obsidianPackageList(
            selectedDesktop,
            when (selectedDesktop) {
                "lxqt" -> "lxqt qterminal pcmanfm-qt featherpad"
                "mate" -> "mate mate-terminal gvfs mate-applets"
                "kde" -> "plasma-desktop konsole dolphin"
                else -> "xfce4 xfce4-terminal xfce4-whiskermenu-plugin xfce4-notifyd thunar mousepad"
            },
        )
''',
)

replace_once(
    runtime,
    '''        val nativeTools = "git wget curl openssh htop python clang"
''',
    '''        val nativeTools = obsidianPackageList(
            "tools",
            "git wget curl openssh htop python clang",
        )
''',
)

replace_once(
    runtime,
    '''        "proot_debian" to isMinimalDebianInstalled(),
''',
    '''        "proot_debian" to isMinimalDebianInstalled(),
        "ember" to File(binDir, "obsidian-ember").canExecute(),
        "mark54" to File(binDir, "obsidian-mark54").canExecute(),
''',
)

replace_once(
    runtime,
    '''            "proot_debian" -> installMinimalDebian(onProgress)
            else -> false
''',
    '''            "proot_debian" -> installMinimalDebian(onProgress)
            "ember" -> installObsidianBundledApp("ember", onProgress)
            "mark54" -> installObsidianBundledApp("mark54", onProgress)
            else -> false
''',
)

catalog = "app/lib/screens/apps/app_catalog_screen.dart"
replace_once(
    catalog,
    '''    _FeaturedApp(
      'imagemagick',
      'ImageMagick',
      'Image conversion and processing toolkit.',
      Icons.image_rounded,
      DroidTheme.primaryLight,
    ),
  ];
''',
    '''    _FeaturedApp(
      'imagemagick',
      'ImageMagick',
      'Image conversion and processing toolkit.',
      Icons.image_rounded,
      DroidTheme.primaryLight,
    ),
    _FeaturedApp(
      'ember',
      'Ember',
      'Linux-compatible Ember V11 assistant for Obsidian Desk.',
      Icons.auto_awesome_rounded,
      Color(0xFF22D3EE),
      optional: true,
    ),
    _FeaturedApp(
      'mark54',
      'Mark LIV · Mark 54',
      'Legacy Linux compatibility port of the older Mark companion.',
      Icons.smart_toy_rounded,
      Color(0xFF9B7BFF),
      optional: true,
    ),
  ];
''',
)

print("Applied Obsidian essentials feed and bundled app catalog.")
