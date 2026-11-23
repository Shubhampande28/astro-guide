package com.jyotishguru.app.ui.kundli

import androidx.annotation.StringRes
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.jyotishguru.app.R
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.ChartRequestBody
import com.jyotishguru.app.data.ChartResponse
import com.jyotishguru.app.data.TokenStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class KundliUiState(
    val chart: ChartResponse? = null,
    @StringRes val errorRes: Int? = null,
)

/** A5: fetches and holds the active profile's chart so rotating the phone
 * doesn't re-trigger the chart computation. */
class KundliViewModel(private val api: ApiService, private val tokenStore: TokenStore) : ViewModel() {
    private val _uiState = MutableStateFlow(KundliUiState())
    val uiState: StateFlow<KundliUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            try {
                val profile = api.getProfile(tokenStore.activeProfileId)
                val chart = api.computeChart(
                    ChartRequestBody(
                        birthDate = profile.birthDate,
                        birthTime = profile.birthTime ?: "12:00:00",
                        timezone = profile.timezone,
                        latitude = profile.latitude,
                        longitude = profile.longitude,
                    ),
                )
                _uiState.value = KundliUiState(chart = chart)
            } catch (e: Exception) {
                _uiState.value = KundliUiState(errorRes = R.string.kundli_load_error)
            }
        }
    }
}
