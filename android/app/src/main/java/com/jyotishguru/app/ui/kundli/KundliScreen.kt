package com.jyotishguru.app.ui.kundli

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Divider
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.ChartRequestBody
import com.jyotishguru.app.data.ChartResponse
import com.jyotishguru.app.data.TokenStore

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KundliScreen(api: ApiService, tokenStore: TokenStore, onBack: () -> Unit) {
    var chart by remember { mutableStateOf<ChartResponse?>(null) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        try {
            val profile = api.getProfile(tokenStore.activeProfileId)
            chart = api.computeChart(
                ChartRequestBody(
                    birthDate = profile.birthDate,
                    birthTime = profile.birthTime ?: "12:00:00",
                    timezone = profile.timezone,
                    latitude = profile.latitude,
                    longitude = profile.longitude,
                ),
            )
        } catch (e: Exception) {
            error = "Could not load your Kundli. Please try again."
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("My Kundli") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                },
            )
        },
    ) { padding ->
        Box(modifier = Modifier.fillMaxSize().padding(padding)) {
            when {
                error != null -> Text(error!!, modifier = Modifier.padding(24.dp))
                chart == null -> CircularProgressIndicator(modifier = Modifier.align(Alignment.Center))
                else -> KundliContent(chart!!)
            }
        }
    }
}

@Composable
private fun KundliContent(chart: ChartResponse) {
    LazyColumn(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        item {
            Text("Lagna (Ascendant)", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 16.dp))
            Text("${chart.lagna.sign}, ${"%.2f".format(chart.lagna.degreeInSign)}° — ${chart.lagna.nakshatra} pada ${chart.lagna.pada}")
            Text(
                "Current dasha: ${chart.currentMahaDasha ?: "-"} / ${chart.currentAntarDasha ?: "-"}",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(top = 4.dp, bottom = 12.dp),
            )
            Divider()
            Text("Grahas", style = MaterialTheme.typography.titleMedium, modifier = Modifier.padding(top = 12.dp, bottom = 4.dp))
            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                HeaderCell("Graha", 1.2f)
                HeaderCell("Sign", 1f)
                HeaderCell("House", 0.6f)
                HeaderCell("Dignity", 1f)
            }
        }
        items(chart.grahas) { graha ->
            Row(modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                Cell(graha.graha + if (graha.retrograde) " (R)" else "", 1.2f)
                Cell(graha.sign, 1f)
                Cell(graha.house.toString(), 0.6f)
                Cell(graha.dignity, 1f)
            }
        }
        item {
            Divider(modifier = Modifier.padding(top = 12.dp))
            Text(
                "Vimshottari Dasha Timeline",
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(top = 12.dp, bottom = 4.dp),
            )
        }
        items(chart.vimshottari) { maha ->
            Text(
                "${maha.lord}: ${maha.start.take(10)} → ${maha.end.take(10)}",
                modifier = Modifier.padding(vertical = 2.dp),
            )
        }
        item { Box(modifier = Modifier.padding(bottom = 24.dp)) }
    }
}

@Composable
private fun RowScope.HeaderCell(text: String, weight: Float) {
    Text(text, fontWeight = FontWeight.Bold, style = MaterialTheme.typography.labelMedium, modifier = Modifier.weight(weight))
}

@Composable
private fun RowScope.Cell(text: String, weight: Float) {
    Text(text, style = MaterialTheme.typography.bodySmall, modifier = Modifier.weight(weight))
}
