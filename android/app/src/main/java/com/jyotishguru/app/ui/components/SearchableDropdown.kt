package com.jyotishguru.app.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.unit.dp

/** A text field that filters a fixed option list as you type and shows
 * matches in a tappable list below -- used for the State/District/City
 * cascade so a birth place is picked from real places rather than typed
 * as free text (and latitude/longitude are never shown to the user). */
@Composable
fun SearchableDropdownField(
    label: String,
    value: String,
    options: List<String>,
    enabled: Boolean,
    onValueSelected: (String) -> Unit,
) {
    var query by remember(value) { mutableStateOf(value) }
    var focused by remember { mutableStateOf(false) }

    val matches = remember(query, options, focused) {
        if (!focused) {
            emptyList()
        } else if (query.isBlank()) {
            options.take(50)
        } else {
            options.filter { it.contains(query, ignoreCase = true) }.take(50)
        }
    }

    Column(modifier = Modifier.fillMaxWidth()) {
        OutlinedTextField(
            value = query,
            onValueChange = {
                query = it
                focused = true
            },
            label = { Text(label) },
            enabled = enabled,
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 4.dp)
                .onFocusChanged { if (it.isFocused) focused = true },
        )
        if (enabled && focused && matches.isNotEmpty()) {
            Card(modifier = Modifier.fillMaxWidth()) {
                LazyColumn(modifier = Modifier.heightIn(max = 240.dp)) {
                    items(matches) { option ->
                        Text(
                            option,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    query = option
                                    focused = false
                                    onValueSelected(option)
                                }
                                .padding(horizontal = 16.dp, vertical = 12.dp),
                        )
                    }
                }
            }
        }
    }
}
