package com.jyotishguru.app.ui.login

import androidx.annotation.StringRes
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.jyotishguru.app.R
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.OtpRequestBody
import com.jyotishguru.app.data.OtpVerifyBody
import com.jyotishguru.app.data.TokenStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

enum class LoginPhase { PHONE, OTP }

data class LoginUiState(
    val phase: LoginPhase = LoginPhase.PHONE,
    val loading: Boolean = false,
    @StringRes val errorRes: Int? = null,
    val loggedIn: Boolean = false,
)

/** A5: holds Login's network calls and result state so rotation and the
 * back/forward stack don't lose progress mid-login; the phone/OTP text
 * fields themselves stay as `rememberSaveable` in the composable. */
class LoginViewModel(private val api: ApiService, private val tokenStore: TokenStore) : ViewModel() {
    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState: StateFlow<LoginUiState> = _uiState.asStateFlow()

    fun requestOtp(phoneNumber: String) {
        _uiState.update { it.copy(errorRes = null, loading = true) }
        viewModelScope.launch {
            try {
                api.requestOtp(OtpRequestBody(phoneNumber))
                _uiState.update { it.copy(phase = LoginPhase.OTP, loading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(errorRes = R.string.login_otp_error, loading = false) }
            }
        }
    }

    fun verifyOtp(phoneNumber: String, otpCode: String) {
        _uiState.update { it.copy(errorRes = null, loading = true) }
        viewModelScope.launch {
            try {
                val response = api.verifyOtp(OtpVerifyBody(phoneNumber, otpCode))
                tokenStore.token = response.accessToken
                _uiState.update { it.copy(loading = false, loggedIn = true) }
            } catch (e: Exception) {
                _uiState.update { it.copy(errorRes = R.string.login_verify_error, loading = false) }
            }
        }
    }
}
