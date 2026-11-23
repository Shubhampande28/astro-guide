package com.jyotishguru.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val DarkColors = darkColorScheme(
    background = BgDark,
    surface = SurfaceDark,
    surfaceVariant = Surface2Dark,
    outline = BorderDark,
    onBackground = TextDark,
    onSurface = TextDark,
    onSurfaceVariant = TextMutedDark,
    primary = Accent,
    onPrimary = BgDark,
    secondary = AccentTextDark,
    error = DangerDark,
)

private val LightColors = lightColorScheme(
    background = BgLight,
    surface = SurfaceLight,
    surfaceVariant = Surface2Light,
    outline = BorderLight,
    onBackground = TextLight,
    onSurface = TextLight,
    onSurfaceVariant = TextMutedLight,
    primary = Accent,
    onPrimary = BgDark,
    secondary = AccentTextLight,
    error = DangerLight,
)

/** Verdict colors aren't part of the Material color scheme; look them up
 * directly by verdict/confidence string where needed (CLAUDE.md 6.1: icon
 * + word, never color alone). */
object VerdictColors {
    @Composable
    fun favourable() = if (isSystemInDarkTheme()) SuccessDark else SuccessLight

    @Composable
    fun mixed() = if (isSystemInDarkTheme()) WarningDark else WarningLight

    @Composable
    fun challenging() = if (isSystemInDarkTheme()) DangerDark else DangerLight
}

@Composable
fun JyotishGuruTheme(content: @Composable () -> Unit) {
    val colors = if (isSystemInDarkTheme()) DarkColors else LightColors
    MaterialTheme(colorScheme = colors, content = content)
}
