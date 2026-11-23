package com.jyotishguru.app.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
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
import com.jyotishguru.app.data.TokenStore

@Composable
fun LoginScreen(api: ApiService, tokenStore: TokenStore, onLoggedIn: () -> Unit) {
    val viewModel: LoginViewModel = viewModel(
        factory = viewModelFactory { initializer { LoginViewModel(api, tokenStore) } },
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var phoneNumber by rememberSaveable { mutableStateOf("") }
    var otpCode by rememberSaveable { mutableStateOf("") }

    if (uiState.loggedIn) {
        onLoggedIn()
        return
    }

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.padding(8.dp))

        when (uiState.phase) {
            LoginPhase.PHONE -> {
                Text(stringResource(R.string.login_phone_prompt))
                OutlinedTextField(
                    value = phoneNumber,
                    onValueChange = { phoneNumber = it },
                    label = { Text(stringResource(R.string.login_phone_hint)) },
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                )
                Button(
                    onClick = { viewModel.requestOtp(phoneNumber) },
                    enabled = phoneNumber.length >= 8 && !uiState.loading,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.login_send_otp))
                }
            }

            LoginPhase.OTP -> {
                Text(stringResource(R.string.login_otp_prompt, phoneNumber))
                OutlinedTextField(
                    value = otpCode,
                    onValueChange = { otpCode = it },
                    label = { Text(stringResource(R.string.login_otp_hint)) },
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                )
                Button(
                    onClick = { viewModel.verifyOtp(phoneNumber, otpCode) },
                    enabled = otpCode.length >= 4 && !uiState.loading,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(stringResource(R.string.login_verify))
                }
            }
        }

        if (uiState.loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        uiState.errorRes?.let {
            Text(stringResource(it), color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
