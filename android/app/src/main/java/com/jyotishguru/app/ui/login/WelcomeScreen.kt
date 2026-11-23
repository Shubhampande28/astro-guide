package com.jyotishguru.app.ui.login

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.TokenStore
import com.jyotishguru.app.ui.components.AppLogo
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
        modifier = Modifier
            .fillMaxSize()
            .padding(horizontal = 24.dp)
            .padding(top = 40.dp, bottom = 24.dp),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            AppLogo(modifier = Modifier.size(36.dp))
            Spacer(Modifier.size(10.dp))
            Text("Jyotish Guru", style = MaterialTheme.typography.headlineSmall)
        }

        Spacer(Modifier.size(20.dp))
        Text("Ask anything about your life", style = MaterialTheme.typography.headlineLarge)
        Spacer(Modifier.size(8.dp))
        Text(
            "Every answer shows the planets behind it and the classical book it comes from.",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(Modifier.size(32.dp))

        Button(
            onClick = onSignIn,
            enabled = !loading,
            shape = MaterialTheme.shapes.medium,
            modifier = Modifier.fillMaxWidth().height(52.dp),
        ) {
            Text("Sign in with phone", style = MaterialTheme.typography.labelLarge)
        }
        Text(
            "Saves your chats so you can pick them up on another device.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 8.dp),
        )

        Spacer(Modifier.size(20.dp))

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
            shape = MaterialTheme.shapes.medium,
            colors = ButtonDefaults.outlinedButtonColors(contentColor = MaterialTheme.colorScheme.secondary),
            modifier = Modifier.fillMaxWidth().height(52.dp),
        ) {
            Text("Skip for now", style = MaterialTheme.typography.labelLarge)
        }
        Text(
            "No phone number needed -- you can always sign in later from the menu.",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.padding(top = 8.dp),
        )

        if (loading) {
            CircularProgressIndicator(modifier = Modifier.padding(top = 16.dp))
        }
        error?.let {
            Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp))
        }
    }
}
