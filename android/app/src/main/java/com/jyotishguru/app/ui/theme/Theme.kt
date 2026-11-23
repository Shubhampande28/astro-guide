package com.jyotishguru.app.ui.theme

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.unit.dp

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
    fun favourable() = SuccessDark

    @Composable
    fun mixed() = WarningDark

    @Composable
    fun challenging() = DangerDark
}

// CLAUDE.md 6.3: radius 12 inputs, 14 buttons, 16 cards, 999 chips/pills.
// Material3 picks a shape role per component (TextField ~ small, Button ~
// medium/large, Card ~ large), so the scale maps onto those roles here.
private val AppShapes = Shapes(
    extraSmall = RoundedCornerShape(12.dp),
    small = RoundedCornerShape(12.dp),
    medium = RoundedCornerShape(14.dp),
    large = RoundedCornerShape(16.dp),
    extraLarge = RoundedCornerShape(28.dp),
)

@Composable
fun JyotishGuruTheme(content: @Composable () -> Unit) {
    // CLAUDE.md 6.1: dark is the default personality of the app (night sky,
    // not neon) -- it isn't meant to follow the device's system theme.
    val colors = DarkColors
    MaterialTheme(colorScheme = colors, typography = JyotishGuruTypography, shapes = AppShapes, content = content)
}
