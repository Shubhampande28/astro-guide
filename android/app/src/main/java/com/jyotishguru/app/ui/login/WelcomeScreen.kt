package com.jyotishguru.app.ui.login

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
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
import com.jyotishguru.app.data.TokenStore
import kotlinx.coroutines.launch

/** The first screen: signing in is optional. "Skip for now" creates an
 * anonymous session (no phone number collected at all) and goes straight
 * to consent -> onboarding -> chat; "Sign in with phone" is only for
 * someone who wants their chats to follow them to another device. */
@Composable
fun WelcomeScreen(api: ApiService, tokenStore: TokenStore, onReady: () -> Unit, onSignIn: () -> Unit) {
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    val scope = rememberCoroutineScope()

    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center,
    ) {
        Text("Jyotish Guru", style = MaterialTheme.typography.headlineMedium)
        Text(
            "A Vedic astrology chat, explained simply.",
            style = MaterialTheme.typography.bodyMedium,
            modifier = Modifier.padding(top = 8.dp, bottom = 32.dp),
        )

        Button(
            onClick = onSignIn,
            enabled = !loading,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Sign in with phone")
        }
        Text(
            "Saves your chats so you can pick them up on another device.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp, bottom = 20.dp),
        )

        OutlinedButton(
            onClick = {
                error = null
                loading = true
                scope.launch {
                    try {
                        val response = api.createGuestSession()
                        tokenStore.token = response.accessToken
                        onReady()
                    } catch (e: Exception) {
                        error = "Could not start. Check your connection and try again."
                    } finally {
                        loading = false
                    }
                }
            },
            enabled = !loading,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text("Skip for now")
        }
        Text(
            "No phone number needed -- you can always sign in later from the menu.",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.padding(top = 4.dp),
        )

        if (loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        error?.let {
            Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
