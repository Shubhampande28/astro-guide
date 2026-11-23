package com.jyotishguru.app.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.jyotishguru.app.data.TOPICS

private val TOPIC_LABELS = mapOf(
    "career" to "Career",
    "marriage" to "Marriage",
    "money" to "Money",
    "health" to "Health",
    "education" to "Education",
    "foreign_travel" to "Foreign travel",
    "children" to "Children",
    "property" to "Property",
)

/** F4: topic chips for Career, Marriage, Money, Health, Education,
 * Foreign travel, Children, Property. */
@Composable
fun TopicChips(onTopicSelected: (String) -> Unit) {
    LazyRow(
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
    ) {
        items(TOPICS) { topic ->
            FilterChip(
                selected = false,
                onClick = { onTopicSelected(topic) },
                label = { Text(TOPIC_LABELS[topic] ?: topic) },
            )
        }
    }
}
