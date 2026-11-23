package com.jyotishguru.app.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.ChatRequestBody
import com.jyotishguru.app.data.ChatResponse
import com.jyotishguru.app.data.ProfileResponse
import com.jyotishguru.app.data.TokenStore
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class DisplayMessage(
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
    // True for a locally-synthesized "failed to send" bubble: the UI shows
    // the localized home_send_error string instead of `summary` for these,
    // since a ViewModel shouldn't resolve string resources itself (A6).
    val isSendError: Boolean = false,
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

data class HomeUiState(
    val profiles: List<ProfileResponse> = emptyList(),
    val activeProfile: ProfileResponse? = null,
    val messages: List<DisplayMessage> = emptyList(),
    val language: String = "en",
    val sending: Boolean = false,
    // A1: a confirmation dialog gates account deletion; nothing is deleted
    // just by opening the menu item.
    val deleteDialogVisible: Boolean = false,
    val deleting: Boolean = false,
    val loggedOut: Boolean = false,
) {
    val previousTopic: String? get() = messages.lastOrNull { it.topic != null }?.topic
}

/** A5: owns profile loading/switching, chat history and sending, and the
 * delete-my-data flow, so none of it is lost on rotation. */
class HomeViewModel(private val api: ApiService, private val tokenStore: TokenStore) : ViewModel() {
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            val profiles = api.listProfiles()
            val active = profiles.find { it.id == tokenStore.activeProfileId } ?: profiles.firstOrNull()
            _uiState.update { it.copy(profiles = profiles, activeProfile = active, language = active?.language ?: "en") }
            active?.let { loadHistory(it.id) }
        }
    }

    private suspend fun loadHistory(profileId: Int) {
        val history = api.getHistory(profileId)
        val messages = history.reversed().map {
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
        _uiState.update { it.copy(messages = messages) }
    }

    fun switchProfile(profile: ProfileResponse) {
        tokenStore.activeProfileId = profile.id
        _uiState.update { it.copy(activeProfile = profile, language = profile.language, messages = emptyList()) }
        viewModelScope.launch { loadHistory(profile.id) }
    }

    fun setLanguage(code: String) {
        _uiState.update { it.copy(language = code) }
    }

    fun sendMessage(text: String) {
        val profile = _uiState.value.activeProfile ?: return
        if (text.isBlank()) return
        _uiState.update { it.copy(sending = true) }
        viewModelScope.launch {
            try {
                val response = api.sendChat(
                    ChatRequestBody(
                        profileId = profile.id,
                        message = text,
                        previousTopic = _uiState.value.previousTopic,
                        language = _uiState.value.language,
                    ),
                )
                _uiState.update { it.copy(messages = it.messages + response.toDisplayMessage(text), sending = false) }
            } catch (e: Exception) {
                val failed = DisplayMessage(
                    questionText = text,
                    topic = null,
                    summary = "",
                    why = emptyList(),
                    sources = emptyList(),
                    timing = emptyList(),
                    remedies = emptyList(),
                    confidence = "low",
                    isSafetyResponse = false,
                    isDeclined = false,
                    isSendError = true,
                )
                _uiState.update { it.copy(messages = it.messages + failed, sending = false) }
            }
        }
    }

    fun showDeleteDialog() {
        _uiState.update { it.copy(deleteDialogVisible = true) }
    }

    fun dismissDeleteDialog() {
        _uiState.update { it.copy(deleteDialogVisible = false) }
    }

    fun confirmDelete() {
        _uiState.update { it.copy(deleting = true) }
        viewModelScope.launch {
            try {
                api.deleteMyData()
            } catch (e: Exception) {
                // Token is likely already invalid either way; proceed to log out.
            }
            tokenStore.clear()
            _uiState.update { it.copy(deleting = false, deleteDialogVisible = false, loggedOut = true) }
        }
    }
}
