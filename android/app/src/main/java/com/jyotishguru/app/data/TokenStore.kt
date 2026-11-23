package com.jyotishguru.app.data

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.emptyPreferences
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking

private val Context.secureDataStore by preferencesDataStore(name = "secure_prefs")

/** Stores the JWT access token encrypted at rest on the device (A4).
 *
 * Values are AES/GCM-encrypted with [KeystoreCrypto] before being written
 * to a Preferences DataStore -- replacing androidx.security:security-crypto,
 * which has sat in alpha and is no longer maintained (see DECISIONS.md).
 *
 * The public API stays synchronous (plain `var` properties) because every
 * existing call site -- the OkHttp auth interceptor on a background thread,
 * and several `LaunchedEffect`/`scope.launch` blocks on the main thread --
 * expects that. A small, one-time `runBlocking` read at construction
 * (during `Application.onCreate`, before any UI) mirrors what the previous
 * `EncryptedSharedPreferences.create(...)` already did synchronously; after
 * that, reads are served from an in-memory cache and writes persist
 * asynchronously, so no caller ever blocks on disk I/O. */
class TokenStore(private val context: Context) {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    @Volatile private var cachedToken: String? = null

    @Volatile private var cachedActiveProfileId: Int = -1

    init {
        val initial = runBlocking(Dispatchers.IO) { readPrefs() }
        cachedToken = initial[KEY_TOKEN]?.let { KeystoreCrypto.decrypt(it) }
        cachedActiveProfileId = initial[KEY_ACTIVE_PROFILE]?.let { KeystoreCrypto.decrypt(it)?.toIntOrNull() } ?: -1
    }

    var token: String?
        get() = cachedToken
        set(value) {
            cachedToken = value
            scope.launch {
                context.secureDataStore.edit { prefs ->
                    if (value == null) prefs.remove(KEY_TOKEN) else prefs[KEY_TOKEN] = KeystoreCrypto.encrypt(value)
                }
            }
        }

    var activeProfileId: Int
        get() = cachedActiveProfileId
        set(value) {
            cachedActiveProfileId = value
            scope.launch {
                context.secureDataStore.edit { prefs -> prefs[KEY_ACTIVE_PROFILE] = KeystoreCrypto.encrypt(value.toString()) }
            }
        }

    fun clear() {
        cachedToken = null
        cachedActiveProfileId = -1
        scope.launch { context.secureDataStore.edit { it.clear() } }
    }

    private suspend fun readPrefs(): Preferences = try {
        context.secureDataStore.data.first()
    } catch (e: Exception) {
        emptyPreferences()
    }

    companion object {
        private val KEY_TOKEN = stringPreferencesKey("access_token")
        private val KEY_ACTIVE_PROFILE = stringPreferencesKey("active_profile_id")
    }
}
