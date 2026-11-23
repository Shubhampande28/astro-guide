package com.jyotishguru.app.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
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
import com.jyotishguru.app.data.OtpRequestBody
import com.jyotishguru.app.data.OtpVerifyBody
import com.jyotishguru.app.data.TokenStore
import kotlinx.coroutines.launch

private enum class LoginPhase { PHONE, OTP }

@Composable
fun LoginScreen(api: ApiService, tokenStore: TokenStore, onLoggedIn: () -> Unit) {
    var phase by remember { mutableStateOf(LoginPhase.PHONE) }
    var phoneNumber by remember { mutableStateOf("") }
    var otpCode by remember { mutableStateOf("") }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Jyotish Guru", style = androidx.compose.material3.MaterialTheme.typography.headlineMedium)
        androidx.compose.foundation.layout.Spacer(modifier = Modifier.padding(8.dp))

        when (phase) {
            LoginPhase.PHONE -> {
                Text("Enter your phone number")
                OutlinedTextField(
                    value = phoneNumber,
                    onValueChange = { phoneNumber = it },
                    label = { Text("+91XXXXXXXXXX") },
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                )
                Button(
                    onClick = {
                        error = null
                        loading = true
                        scope.launch {
                            try {
                                api.requestOtp(OtpRequestBody(phoneNumber))
                                phase = LoginPhase.OTP
                            } catch (e: Exception) {
                                error = "Could not send OTP. Check your connection and try again."
                            } finally {
                                loading = false
                            }
                        }
                    },
                    enabled = phoneNumber.length >= 8 && !loading,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Send OTP")
                }
            }

            LoginPhase.OTP -> {
                Text("Enter the 6-digit code sent to $phoneNumber")
                OutlinedTextField(
                    value = otpCode,
                    onValueChange = { otpCode = it },
                    label = { Text("OTP") },
                    modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                )
                Button(
                    onClick = {
                        error = null
                        loading = true
                        scope.launch {
                            try {
                                val response = api.verifyOtp(OtpVerifyBody(phoneNumber, otpCode))
                                tokenStore.token = response.accessToken
                                onLoggedIn()
                            } catch (e: Exception) {
                                error = "Incorrect or expired code. Please try again."
                            } finally {
                                loading = false
                            }
                        }
                    },
                    enabled = otpCode.length >= 4 && !loading,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text("Verify")
                }
            }
        }

        if (loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        error?.let {
            Text(it, color = androidx.compose.material3.MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
