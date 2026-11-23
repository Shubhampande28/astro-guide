package com.jyotishguru.app.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.ChatRequestBody
import com.jyotishguru.app.data.ChatResponse
import com.jyotishguru.app.data.ProfileResponse
import com.jyotishguru.app.data.TokenStore
import com.jyotishguru.app.ui.components.AnswerCardView
import kotlinx.coroutines.launch

private data class DisplayMessage(
    val questionText: String?,
    val topic: String?,
    val summary: String,
    val why: List<String>,
    val sources: List<String>,
    val timing: List<String>,
    val remedies: List<String>,
    val confidence: String,
    val isSafetyResponse: Boolean,
    val isDeclined: Boolean,
)

private fun ChatResponse.toDisplayMessage(question: String) = DisplayMessage(
    questionText = question,
    topic = topic,
    summary = aiRewrittenSummary ?: summary,
    why = why,
    sources = sources,
    timing = timing,
    remedies = remedies,
    confidence = confidence,
    isSafetyResponse = isSafetyResponse,
    isDeclined = isDeclined,
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    api: ApiService,
    tokenStore: TokenStore,
    onAddProfile: () -> Unit,
    onViewKundli: () -> Unit,
    onLoggedOut: () -> Unit,
) {
    var profiles by remember { mutableStateOf<List<ProfileResponse>>(emptyList()) }
    var activeProfile by remember { mutableStateOf<ProfileResponse?>(null) }
    var messages by remember { mutableStateOf<List<DisplayMessage>>(emptyList()) }
    var inputText by remember { mutableStateOf("") }
    var previousTopic by remember { mutableStateOf<String?>(null) }
    var language by remember { mutableStateOf("en") }
    var sending by remember { mutableStateOf(false) }
    var menuExpanded by remember { mutableStateOf(false) }
    var profileMenuExpanded by remember { mutableStateOf(false) }
    val scope = rememberCoroutineScope()

    suspend fun loadHistory(profileId: Int) {
        val history = api.getHistory(profileId)
        messages = history.reversed().map {
            DisplayMessage(
                questionText = it.messageText,
                topic = it.topic,
                summary = it.summary,
                why = emptyList(),
                sources = emptyList(),
                timing = emptyList(),
                remedies = emptyList(),
                confidence = it.confidence,
                isSafetyResponse = false,
                isDeclined = false,
            )
        }
        previousTopic = history.firstOrNull()?.topic
    }

    LaunchedEffect(Unit) {
        profiles = api.listProfiles()
        val active = profiles.find { it.id == tokenStore.activeProfileId } ?: profiles.firstOrNull()
        activeProfile = active
        language = active?.language ?: "en"
        active?.let { loadHistory(it.id) }
    }

    fun sendMessage(text: String) {
        val profile = activeProfile ?: return
        if (text.isBlank()) return
        sending = true
        scope.launch {
            try {
                val response = api.sendChat(
                    ChatRequestBody(
                        profileId = profile.id,
                        message = text,
                        previousTopic = previousTopic,
                        language = language,
                    ),
                )
                previousTopic = response.topic ?: previousTopic
                messages = messages + response.toDisplayMessage(text)
                inputText = ""
            } catch (e: Exception) {
                messages = messages + DisplayMessage(
                    questionText = text,
                    topic = null,
                    summary = "Something went wrong sending that message. Please try again.",
                    why = emptyList(),
                    sources = emptyList(),
                    timing = emptyList(),
                    remedies = emptyList(),
                    confidence = "low",
                    isSafetyResponse = false,
                    isDeclined = false,
                )
            } finally {
                sending = false
            }
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Box {
                        Text(
                            activeProfile?.name ?: "Jyotish Guru",
                            modifier = Modifier.padding(end = 4.dp),
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { profileMenuExpanded = true }) {
                        Icon(Icons.Default.MoreVert, contentDescription = "Switch profile")
                    }
                    DropdownMenu(expanded = profileMenuExpanded, onDismissRequest = { profileMenuExpanded = false }) {
                        profiles.forEach { profile ->
                            DropdownMenuItem(
                                text = { Text(profile.name) },
                                onClick = {
                                    profileMenuExpanded = false
                                    activeProfile = profile
                                    tokenStore.activeProfileId = profile.id
                                    language = profile.language
                                    scope.launch { loadHistory(profile.id) }
                                },
                            )
                        }
                        DropdownMenuItem(text = { Text("Add family profile") }, onClick = {
                            profileMenuExpanded = false
                            onAddProfile()
                        })
                    }
                    IconButton(onClick = { menuExpanded = true }) {
                        Text("A/अ", modifier = Modifier.padding(horizontal = 4.dp))
                    }
                    DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) {
                        listOf("en" to "English", "hi" to "Hindi", "hinglish" to "Hinglish").forEach { (code, label) ->
                            DropdownMenuItem(text = { Text(label) }, onClick = {
                                language = code
                                menuExpanded = false
                            })
                        }
                        DropdownMenuItem(text = { Text("My Kundli") }, onClick = {
                            menuExpanded = false
                            onViewKundli()
                        })
                        DropdownMenuItem(text = { Text("Delete my data") }, onClick = {
                            menuExpanded = false
                            scope.launch {
                                try {
                                    api.deleteMyData()
                                } catch (e: Exception) {
                                    // Token is likely already invalid either way; proceed to log out.
                                }
                                tokenStore.clear()
                                onLoggedOut()
                            }
                        })
                    }
                },
            )
        },
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(horizontal = 12.dp)) {
            LazyColumn(modifier = Modifier.weight(1f).fillMaxWidth()) {
                items(messages) { message ->
                    message.questionText?.let {
                        Text(
                            it,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.fillMaxWidth().padding(top = 8.dp, start = 8.dp),
                        )
                    }
                    AnswerCardView(
                        topic = message.topic,
                        summary = message.summary,
                        why = message.why,
                        sources = message.sources,
                        timing = message.timing,
                        remedies = message.remedies,
                        confidence = message.confidence,
                        isSafetyResponse = message.isSafetyResponse,
                        isDeclined = message.isDeclined,
                    )
                }
            }

            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    placeholder = { Text("Ask anything about your life...") },
                    modifier = Modifier.weight(1f),
                )
                if (sending) {
                    CircularProgressIndicator(modifier = Modifier.padding(start = 8.dp).size(24.dp))
                } else {
                    IconButton(onClick = { sendMessage(inputText) }) {
                        Icon(Icons.Default.Send, contentDescription = "Send")
                    }
                }
            }
        }
    }
}
