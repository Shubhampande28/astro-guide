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
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import com.jyotishguru.app.R
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.INDIA_TIMEZONE
import com.jyotishguru.app.data.IndiaPlacesRepository
import com.jyotishguru.app.data.InternationalPlace
import com.jyotishguru.app.data.searchInternationalPlaces
import com.jyotishguru.app.ui.components.SearchableDropdownField

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
    val viewModel: OnboardingViewModel = viewModel(
        factory = viewModelFactory { initializer { OnboardingViewModel(api) } },
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    uiState.createdProfileId?.let {
        onProfileCreated(it)
        return
    }

    var isSelf by rememberSaveable { mutableStateOf(!isAddingFamilyMember) }
    var name by rememberSaveable { mutableStateOf("") }
    var birthDate by rememberSaveable { mutableStateOf("") } // YYYY-MM-DD
    var birthTime by rememberSaveable { mutableStateOf("") } // HH:MM
    var timeUnknown by rememberSaveable { mutableStateOf(false) }

    var bornOutsideIndia by rememberSaveable { mutableStateOf(false) }

    // India cascade.
    var selectedState by rememberSaveable { mutableStateOf("") }
    var selectedDistrict by rememberSaveable { mutableStateOf("") }
    var selectedCityName by rememberSaveable { mutableStateOf("") }
    var selectedCityLat by rememberSaveable { mutableStateOf<Double?>(null) }
    var selectedCityLon by rememberSaveable { mutableStateOf<Double?>(null) }

    // International fallback. `selectedInternational` is a plain `remember`
    // (not `rememberSaveable`): it's a derived convenience, not text the
    // user typed, and is safe to lose on process death -- the query text
    // that drives it is still saved.
    var internationalQuery by rememberSaveable { mutableStateOf("") }
    var selectedInternational by remember { mutableStateOf<InternationalPlace?>(null) }

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
        Text(stringResource(R.string.onboarding_whose_kundli), style = MaterialTheme.typography.headlineSmall)
        Text(
            stringResource(R.string.onboarding_subtitle),
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(bottom = 12.dp, top = 4.dp),
        )

        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(bottom = 16.dp)) {
            FilterChip(selected = isSelf, onClick = { isSelf = true }, label = { Text(stringResource(R.string.onboarding_myself)) })
            FilterChip(
                selected = !isSelf,
                onClick = { isSelf = false },
                label = { Text(stringResource(R.string.onboarding_family_member)) },
            )
        }

        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text(stringResource(if (isSelf) R.string.onboarding_name_self else R.string.onboarding_name_family)) },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        OutlinedTextField(
            value = birthDate,
            onValueChange = { birthDate = it },
            label = { Text(stringResource(R.string.onboarding_birth_date)) },
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        OutlinedTextField(
            value = birthTime,
            onValueChange = { birthTime = it },
            label = { Text(stringResource(R.string.onboarding_birth_time)) },
            enabled = !timeUnknown,
            modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
        )
        Row(modifier = Modifier.padding(vertical = 4.dp)) {
            Checkbox(checked = timeUnknown, onCheckedChange = { timeUnknown = it })
            Text(stringResource(R.string.onboarding_time_unknown), modifier = Modifier.padding(top = 12.dp))
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
            Text(stringResource(R.string.onboarding_born_outside_india), modifier = Modifier.padding(top = 12.dp))
        }

        if (!bornOutsideIndia) {
            SearchableDropdownField(
                label = stringResource(R.string.onboarding_state),
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
                label = stringResource(R.string.onboarding_district),
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
                label = stringResource(R.string.onboarding_city),
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
                label = { Text(stringResource(R.string.onboarding_city_outside)) },
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
                viewModel.createProfile(
                    name = name,
                    isSelf = isSelf,
                    birthDate = birthDate,
                    birthTime = birthTime,
                    timeUnknown = timeUnknown,
                    latitude = lat,
                    longitude = lon,
                    timezone = timezone,
                )
            },
            enabled = !uiState.loading,
            modifier = Modifier.fillMaxWidth().padding(top = 16.dp),
        ) {
            Text(stringResource(R.string.onboarding_create_kundli))
        }

        if (uiState.loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        uiState.errorRes?.let {
            Text(stringResource(it), color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
