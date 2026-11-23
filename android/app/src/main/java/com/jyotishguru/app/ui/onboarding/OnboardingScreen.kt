package com.jyotishguru.app.ui.onboarding

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.Checkbox
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
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
import com.jyotishguru.app.data.INDIA_TIMEZONE
import com.jyotishguru.app.data.IndiaPlacesRepository
import com.jyotishguru.app.data.InternationalPlace
import com.jyotishguru.app.data.ProfileCreateBody
import com.jyotishguru.app.data.searchInternationalPlaces
import com.jyotishguru.app.ui.components.SearchableDropdownField
import kotlinx.coroutines.launch

/** F1 onboarding: who it's for (myself vs. a family member), name, DOB,
 * time (+ "I don't know my time"), and birth place picked as State ->
 * District -> City/Town for India (IndiaPlacesRepository, a real offline
 * GeoNames-based dataset covering all 36 states/UTs), or a short
 * international list for births outside India. Latitude/longitude are
 * looked up from the chosen place and sent to the backend without ever
 * being shown to the user.
 *
 * `isAddingFamilyMember` just sets the default selection; the user can
 * still switch it. It's true when reached via Home's "Add family
 * profile", false for the first-ever profile on a fresh account.
 */
@Composable
fun OnboardingScreen(
    api: ApiService,
    indiaPlaces: IndiaPlacesRepository,
    isAddingFamilyMember: Boolean = false,
    onProfileCreated: (Int) -> Unit,
) {
    var isSelf by remember { mutableStateOf(!isAddingFamilyMember) }
    var name by remember { mutableStateOf("") }
    var birthDate by remember { mutableStateOf("") } // YYYY-MM-DD
    var birthTime by remember { mutableStateOf("") } // HH:MM
    var timeUnknown by remember { mutableStateOf(false) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }

    var bornOutsideIndia by remember { mutableStateOf(false) }

    // India cascade.
    var selectedState by remember { mutableStateOf("") }
    var selectedDistrict by remember { mutableStateOf("") }
    var selectedCityName by remember { mutableStateOf("") }
    var selectedCityLat by remember { mutableStateOf<Double?>(null) }
    var selectedCityLon by remember { mutableStateOf<Double?>(null) }

    // International fallback.
    var internationalQuery by remember { mutableStateOf("") }
    var selectedInternational by remember { mutableStateOf<InternationalPlace?>(null) }

    val scope = rememberCoroutineScope()

    val districts = if (selectedState.isNotBlank()) indiaPlaces.districts(selectedState) else emptyList()
    val cities = if (selectedDistrict.isNotBlank()) indiaPlaces.cities(selectedState, selectedDistrict) else emptyList()
    val internationalSuggestions =
        if (selectedInternational?.name == internationalQuery) emptyList() else searchInternationalPlaces(internationalQuery)

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(24.dp),
        verticalArrangement = Arrangement.Top,
    ) {
        Text("Whose Kundli is this?", style = MaterialTheme.typography.headlineSmall)
        Text(
            "This is used to calculate the Kundli. You can add up to 5 profiles.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(bottom = 12.dp, top = 4.dp),
        )

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(bottom = 16.dp)) {
            FilterChip(selected = isSelf, onClick = { isSelf = true }, label = { Text("Myself") })
            FilterChip(
                selected = !isSelf,
                onClick = { isSelf = false },
                label = { Text("A family member") },
            )
        }

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text(if (isSelf) "Your name" else "Their name") },
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
            Text("Birth time isn't known", modifier = Modifier.padding(top = 12.dp))
        }

        Row(modifier = Modifier.padding(top = 8.dp, bottom = 4.dp)) {
            Checkbox(
                checked = bornOutsideIndia,
                onCheckedChange = {
                    bornOutsideIndia = it
                    selectedState = ""
                    selectedDistrict = ""
                    selectedCityName = ""
                    selectedCityLat = null
                    selectedCityLon = null
                    selectedInternational = null
                    internationalQuery = ""
                },
            )
            Text("Born outside India", modifier = Modifier.padding(top = 12.dp))
        }

        if (!bornOutsideIndia) {
            SearchableDropdownField(
                label = "State",
                value = selectedState,
                options = indiaPlaces.states(),
                enabled = true,
                onValueSelected = {
                    selectedState = it
                    selectedDistrict = ""
                    selectedCityName = ""
                    selectedCityLat = null
                    selectedCityLon = null
                },
            )
            SearchableDropdownField(
                label = "District",
                value = selectedDistrict,
                options = districts,
                enabled = selectedState.isNotBlank(),
                onValueSelected = {
                    selectedDistrict = it
                    selectedCityName = ""
                    selectedCityLat = null
                    selectedCityLon = null
                },
            )
            SearchableDropdownField(
                label = "City / Town",
                value = selectedCityName,
                options = cities.map { it.name },
                enabled = selectedDistrict.isNotBlank(),
                onValueSelected = { chosenName ->
                    val match = cities.firstOrNull { it.name == chosenName }
                    selectedCityName = chosenName
                    selectedCityLat = match?.lat
                    selectedCityLon = match?.lon
                },
            )
        } else {
            OutlinedTextField(
                value = internationalQuery,
                onValueChange = {
                    internationalQuery = it
                    if (selectedInternational?.name != it) selectedInternational = null
                },
                label = { Text("Birth city (outside India)") },
                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
            )
            if (internationalSuggestions.isNotEmpty()) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column {
                        internationalSuggestions.forEach { place ->
                            Text(
                                place.name,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable {
                                        selectedInternational = place
                                        internationalQuery = place.name
                                    }
                                    .padding(horizontal = 16.dp, vertical = 12.dp),
                            )
                        }
                    }
                }
            }
        }

        Button(
            onClick = {
                error = null
                val lat: Double?
                val lon: Double?
                val timezone: String
                if (bornOutsideIndia) {
                    lat = selectedInternational?.lat
                    lon = selectedInternational?.lon
                    timezone = selectedInternational?.timezone ?: ""
                } else {
                    lat = selectedCityLat
                    lon = selectedCityLon
                    timezone = INDIA_TIMEZONE
                }
                if (name.isBlank() || birthDate.isBlank() || lat == null || lon == null) {
                    error = "Please fill in all fields and pick a birth place from the list."
                    return@Button
                }
                loading = true
                scope.launch {
                    try {
                        val profile = api.createProfile(
                            ProfileCreateBody(
                                name = name,
                                relation = if (isSelf) "self" else "family",
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
                        error = "Could not save this profile. Please check the fields and try again."
                    } finally {
                        loading = false
                    }
                }
            },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
        ) {
            Text("Create Kundli")
        }

        if (loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        error?.let {
            Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
