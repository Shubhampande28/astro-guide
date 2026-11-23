package com.jyotishguru.app.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.jyotishguru.app.data.ApiService
import kotlinx.coroutines.launch

/** CLAUDE.md principle 4 (DPDP): explicit consent before any birth data is
 * stored. F1's consent screen. */
@Composable
fun ConsentScreen(api: ApiService, onConsented: () -> Unit) {
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Before we begin", style = MaterialTheme.typography.headlineSmall)
        Text(
            "We'll ask for your (or your family member's) name, date, time, and place of " +
                "birth to calculate a Kundli. This data is encrypted, never sold, and you can " +
                "delete it at any time from Settings.",
            modifier = Modifier.padding(vertical = 16.dp),
        )
        Button(
            onClick = {
                error = null
                loading = true
                scope.launch {
                    try {
                        api.giveConsent()
                        onConsented()
                    } catch (e: Exception) {
                        error = "Something went wrong. Please try again."
                    } finally {
                        loading = false
                    }
                }
            },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("I agree, continue")
        }
        if (loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        error?.let {
            Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
