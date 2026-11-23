package com.jyotishguru.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.jyotishguru.app.ui.nav.AppNavHost
import com.jyotishguru.app.ui.theme.JyotishGuruTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val app = application as JyotishGuruApp

        setContent {
            JyotishGuruTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    AppNavHost(api = app.api, tokenStore = app.tokenStore)
                }
            }
        }
    }
}
