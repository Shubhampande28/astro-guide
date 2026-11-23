package com.jyotishguru.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke

/** The app's mark: an accent-colored sparkle inside a thin circle outline,
 * matching the approved prototype (CLAUDE.md 6, reference artifact link). */
@Composable
fun AppLogo(modifier: Modifier = Modifier) {
    val accent = MaterialTheme.colorScheme.primary
    Canvas(modifier = modifier) {
        val r = size.width * (16f / 36f)
        drawCircle(color = accent, radius = r, style = Stroke(width = size.width * (1.5f / 36f)))

        fun pt(x: Float, y: Float) = Offset(x / 36f * size.width, y / 36f * size.height)
        val path = Path().apply {
            moveTo(pt(18f, 7f).x, pt(18f, 7f).y)
            lineTo(pt(20.5f, 15.5f).x, pt(20.5f, 15.5f).y)
            lineTo(pt(29f, 18f).x, pt(29f, 18f).y)
            lineTo(pt(20.5f, 20.5f).x, pt(20.5f, 20.5f).y)
            lineTo(pt(18f, 29f).x, pt(18f, 29f).y)
            lineTo(pt(15.5f, 20.5f).x, pt(15.5f, 20.5f).y)
            lineTo(pt(7f, 18f).x, pt(7f, 18f).y)
            lineTo(pt(15.5f, 15.5f).x, pt(15.5f, 15.5f).y)
            close()
        }
        drawPath(path, color = accent)
    }
}
