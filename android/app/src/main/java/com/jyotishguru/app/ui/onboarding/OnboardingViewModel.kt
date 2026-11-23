package com.jyotishguru.app.ui.onboarding

import androidx.annotation.StringRes
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.jyotishguru.app.R
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.ProfileCreateBody
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class OnboardingUiState(
    val loading: Boolean = false,
    @StringRes val errorRes: Int? = null,
    val createdProfileId: Int? = null,
)

/** A5: owns the create-profile network call and its result; every form
 * field stays `rememberSaveable` in the composable, since this screen (one
 * big form for now) is slated to become the 4-step wizard of Group E. */
class OnboardingViewModel(private val api: ApiService) : ViewModel() {
    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    fun createProfile(
        name: String,
        isSelf: Boolean,
        birthDate: String,
        birthTime: String,
        timeUnknown: Boolean,
        latitude: Double?,
        longitude: Double?,
        timezone: String,
    ) {
        if (name.isBlank() || birthDate.isBlank() || latitude == null || longitude == null) {
            _uiState.update { it.copy(errorRes = R.string.onboarding_validation_error) }
            return
        }
        _uiState.update { it.copy(errorRes = null, loading = true) }
        viewModelScope.launch {
            try {
                val profile = api.createProfile(
                    ProfileCreateBody(
                        name = name,
                        relation = if (isSelf) "self" else "family",
                        language = "en",
                        birthDate = birthDate,
                        birthTime = if (timeUnknown || birthTime.isBlank()) null else "$birthTime:00",
                        birthTimeUnknown = timeUnknown,
                        latitude = latitude,
                        longitude = longitude,
                        timezone = timezone,
                    ),
                )
                _uiState.update { it.copy(loading = false, createdProfileId = profile.id) }
            } catch (e: Exception) {
                _uiState.update { it.copy(errorRes = R.string.onboarding_save_error, loading = false) }
            }
        }
    }
}
