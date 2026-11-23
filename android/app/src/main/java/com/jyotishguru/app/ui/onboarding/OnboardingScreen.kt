package com.jyotishguru.app.ui.onboarding

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
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
import com.jyotishguru.app.data.ProfileCreateBody
import kotlinx.coroutines.launch

/** F1 onboarding: name, DOB, time (+ "I don't know my time"), location,
 * language. Place search/autocomplete is not built yet (deferred -- see
 * backend DECISIONS.md), so location is entered as lat/lon directly. */
@Composable
fun OnboardingScreen(api: ApiService, onProfileCreated: (Int) -> Unit) {
    var name by remember { mutableStateOf("") }
    var birthDate by remember { mutableStateOf("") } // YYYY-MM-DD
    var birthTime by remember { mutableStateOf("") } // HH:MM
    var timeUnknown by remember { mutableStateOf(false) }
    var latitude by remember { mutableStateOf("28.6139") }
    var longitude by remember { mutableStateOf("77.2090") }
    var timezone by remember { mutableStateOf("Asia/Kolkata") }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.Top,
    ) {
        Text("Tell us about yourself", style = MaterialTheme.typography.headlineSmall)
        Text(
            "This is used to calculate your Kundli. Add family members later from the menu.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(bottom = 16.dp, top = 4.dp),
        )

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Name") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        OutlinedTextField(
            value = birthDate,
            onValueChange = { birthDate = it },
            label = { Text("Birth date (YYYY-MM-DD)") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        OutlinedTextField(
            value = birthTime,
            onValueChange = { birthTime = it },
            label = { Text("Birth time (HH:MM, 24h)") },
            enabled = !timeUnknown,
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        Row(modifier = Modifier.padding(vertical = 4.dp)) {
            Checkbox(checked = timeUnknown, onCheckedChange = { timeUnknown = it })
            Text("I don't know my birth time", modifier = Modifier.padding(top = 12.dp))
        }
        OutlinedTextField(
            value = latitude,
            onValueChange = { latitude = it },
            label = { Text("Birth place latitude") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        OutlinedTextField(
            value = longitude,
            onValueChange = { longitude = it },
            label = { Text("Birth place longitude") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        OutlinedTextField(
            value = timezone,
            onValueChange = { timezone = it },
            label = { Text("Timezone (e.g. Asia/Kolkata)") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )

        Button(
            onClick = {
                error = null
                val lat = latitude.toDoubleOrNull()
                val lon = longitude.toDoubleOrNull()
                if (name.isBlank() || birthDate.isBlank() || lat == null || lon == null) {
                    error = "Please fill in all fields correctly."
                    return@Button
                }
                loading = true
                scope.launch {
                    try {
                        val profile = api.createProfile(
                            ProfileCreateBody(
                                name = name,
                                relation = "self",
                                language = "en",
                                birthDate = birthDate,
                                birthTime = if (timeUnknown || birthTime.isBlank()) null else "$birthTime:00",
                                birthTimeUnknown = timeUnknown,
                                latitude = lat,
                                longitude = lon,
                                timezone = timezone,
                            ),
                        )
                        onProfileCreated(profile.id)
                    } catch (e: Exception) {
                        error = "Could not save your profile. Please check the fields and try again."
                    } finally {
                        loading = false
                    }
                }
            },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
        ) {
            Text("Create my Kundli")
        }

        if (loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        error?.let {
            Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
