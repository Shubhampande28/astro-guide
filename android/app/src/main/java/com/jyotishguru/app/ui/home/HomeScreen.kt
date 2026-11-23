package com.jyotishguru.app.ui.home

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
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material3.AlertDialog
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
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
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
import com.jyotishguru.app.ui.components.AnswerCardView

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    api: ApiService,
    tokenStore: TokenStore,
    onAddProfile: () -> Unit,
    onViewKundli: () -> Unit,
    onLoggedOut: () -> Unit,
) {
    val viewModel: HomeViewModel = viewModel(
        factory = viewModelFactory { initializer { HomeViewModel(api, tokenStore) } },
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    var inputText by rememberSaveable { mutableStateOf("") }
    var menuExpanded by rememberSaveable { mutableStateOf(false) }
    var profileMenuExpanded by rememberSaveable { mutableStateOf(false) }

    if (uiState.loggedOut) {
        onLoggedOut()
        return
    }

    if (uiState.deleteDialogVisible) {
        AlertDialog(
            onDismissRequest = { if (!uiState.deleting) viewModel.dismissDeleteDialog() },
            title = { Text(stringResource(R.string.home_delete_dialog_title)) },
            text = { Text(stringResource(R.string.home_delete_dialog_message)) },
            confirmButton = {
                TextButton(onClick = { viewModel.confirmDelete() }, enabled = !uiState.deleting) {
                    Text(stringResource(R.string.home_delete_dialog_confirm), color = MaterialTheme.colorScheme.error)
                }
            },
            dismissButton = {
                TextButton(onClick = { viewModel.dismissDeleteDialog() }, enabled = !uiState.deleting) {
                    Text(stringResource(R.string.home_delete_dialog_cancel))
                }
            },
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Box {
                        Text(
                            uiState.activeProfile?.name ?: stringResource(R.string.app_name),
                            modifier = Modifier.padding(end = 4.dp),
                        )
                    }
                },
                actions = {
                    IconButton(onClick = { profileMenuExpanded = true }) {
                        Icon(Icons.Default.MoreVert, contentDescription = stringResource(R.string.home_switch_profile_content_desc))
                    }
                    DropdownMenu(expanded = profileMenuExpanded, onDismissRequest = { profileMenuExpanded = false }) {
                        uiState.profiles.forEach { profile ->
                            DropdownMenuItem(
                                text = { Text(profile.name) },
                                onClick = {
                                    profileMenuExpanded = false
                                    viewModel.switchProfile(profile)
                                },
                            )
                        }
                        DropdownMenuItem(text = { Text(stringResource(R.string.home_add_family_profile)) }, onClick = {
                            profileMenuExpanded = false
                            onAddProfile()
                        })
                    }
                    IconButton(onClick = { menuExpanded = true }) {
                        Text("A/अ", modifier = Modifier.padding(horizontal = 4.dp))
                    }
                    DropdownMenu(expanded = menuExpanded, onDismissRequest = { menuExpanded = false }) {
                        listOf(
                            "en" to stringResource(R.string.home_language_english),
                            "hi" to stringResource(R.string.home_language_hindi),
                            "hinglish" to stringResource(R.string.home_language_hinglish),
                        ).forEach { (code, label) ->
                            DropdownMenuItem(text = { Text(label) }, onClick = {
                                viewModel.setLanguage(code)
                                menuExpanded = false
                            })
                        }
                        DropdownMenuItem(text = { Text(stringResource(R.string.home_my_kundli)) }, onClick = {
                            menuExpanded = false
                            onViewKundli()
                        })
                        DropdownMenuItem(text = { Text(stringResource(R.string.home_delete_my_data)) }, onClick = {
                            menuExpanded = false
                            viewModel.showDeleteDialog()
                        })
                    }
                },
            )
        },
    ) { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(horizontal = 12.dp)) {
            LazyColumn(modifier = Modifier.weight(1f).fillMaxWidth()) {
                items(uiState.messages) { message ->
                    message.questionText?.let {
                        Text(
                            it,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.fillMaxWidth().padding(top = 8.dp, start = 8.dp),
                        )
                    }
                    if (message.isSendError) {
                        Text(
                            stringResource(R.string.home_send_error),
                            color = MaterialTheme.colorScheme.error,
                            style = MaterialTheme.typography.bodyMedium,
                            modifier = Modifier.fillMaxWidth().padding(start = 8.dp, top = 4.dp),
                        )
                    } else {
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
            }

            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            ) {
                OutlinedTextField(
                    value = inputText,
                    onValueChange = { inputText = it },
                    placeholder = { Text(stringResource(R.string.home_input_placeholder)) },
                    modifier = Modifier.weight(1f),
                )
                if (uiState.sending) {
                    CircularProgressIndicator(modifier = Modifier.padding(start = 8.dp).size(24.dp))
                } else {
                    IconButton(onClick = {
                        viewModel.sendMessage(inputText)
                        inputText = ""
                    }) {
                        Icon(Icons.AutoMirrored.Filled.Send, contentDescription = stringResource(R.string.home_send_content_desc))
                    }
                }
            }
        }
    }
}
