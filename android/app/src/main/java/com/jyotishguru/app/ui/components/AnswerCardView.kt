package com.jyotishguru.app.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.jyotishguru.app.R
import com.jyotishguru.app.ui.theme.VerdictColors

/** The 6-part answer card from CLAUDE.md F3/6.4: Summary, Why, Sources,
 * Timing, Remedies, Confidence. Sections beyond the summary are
 * collapsed by default (toggle pills), matching the design spec. */
@Composable
fun AnswerCardView(
    topic: String?,
    summary: String,
    why: List<String>,
    sources: List<String>,
    timing: List<String>,
    remedies: List<String>,
    confidence: String,
    isSafetyResponse: Boolean = false,
    isDeclined: Boolean = false,
) {
    var expanded by remember { mutableStateOf(false) }

    Card(
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            if (topic != null && !isSafetyResponse && !isDeclined) {
                Text(
                    topic.replace("_", " ").replaceFirstChar { it.uppercase() },
                    color = MaterialTheme.colorScheme.secondary,
                    style = MaterialTheme.typography.labelLarge,
                )
            }
            Text(summary, style = MaterialTheme.typography.bodyLarge, modifier = Modifier.padding(top = 4.dp))

            if (!isSafetyResponse && !isDeclined && (why.isNotEmpty() || sources.isNotEmpty() || timing.isNotEmpty())) {
                Text(
                    stringResource(if (expanded) R.string.answer_hide_details else R.string.answer_why_sources_timing),
                    color = MaterialTheme.colorScheme.secondary,
                    style = MaterialTheme.typography.labelMedium,
                    modifier = Modifier
                        .padding(top = 12.dp)
                        .clickable { expanded = !expanded },
                )

                if (expanded) {
                    if (why.isNotEmpty()) {
                        SectionLabel(stringResource(R.string.answer_section_why))
                        why.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium) }
                    }
                    if (sources.isNotEmpty()) {
                        SectionLabel(stringResource(R.string.answer_section_sources))
                        Text(sources.joinToString(", "), style = MaterialTheme.typography.bodySmall)
                    }
                    if (timing.isNotEmpty()) {
                        SectionLabel(stringResource(R.string.answer_section_timing))
                        timing.forEach { Text(it, style = MaterialTheme.typography.bodyMedium) }
                    }
                    if (remedies.isNotEmpty()) {
                        SectionLabel(stringResource(R.string.answer_section_remedies))
                        remedies.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium) }
                    }
                }

                Row(
                    verticalAlignment = androidx.compose.ui.Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(6.dp),
                    modifier = Modifier.padding(top = 10.dp),
                ) {
                    val color = when (confidence) {
                        "high" -> VerdictColors.favourable()
                        "medium" -> VerdictColors.mixed()
                        else -> MaterialTheme.colorScheme.onSurfaceVariant
                    }
                    Text(
                        stringResource(R.string.answer_confidence, confidence.replaceFirstChar { it.uppercase() }),
                        color = color,
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.Medium,
                    )
                }
            }
        }
    }
}

@Composable
private fun SectionLabel(text: String) {
    Text(
        text,
        style = MaterialTheme.typography.labelMedium,
        fontWeight = FontWeight.Bold,
        modifier = Modifier.padding(top = 8.dp, bottom = 2.dp),
    )
}
