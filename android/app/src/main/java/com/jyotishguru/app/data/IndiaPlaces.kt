package com.jyotishguru.app.data

import android.content.Context
import com.google.gson.annotations.SerializedName
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

/** A real, offline India place picker (CLAUDE.md 5.1: "offline GeoNames
 * ... database, no paid API") -- State -> District -> City/Town, so a
 * birth place can be found by name instead of ever asking for latitude/
 * longitude directly, and disambiguated from same-named places in other
 * states/districts.
 *
 * Built from GeoNames' cities500 export (populated places, population
 * >= 500) filtered to India and joined with admin1/admin2 code names;
 * 7,324 places across all 36 states/UTs as of when this was generated.
 * See scripts/build_india_places.py (kept for reference; not run at
 * build time) and DECISIONS.md.
 */
data class IndiaPlace(
    @SerializedName("n") val name: String,
    @SerializedName("s") val state: String,
    @SerializedName("d") val district: String,
    val lat: Double,
    val lon: Double,
    @SerializedName("p") val population: Int,
)

/** India has a single timezone; GeoNames' per-row timezone column is
 * redundant here and was dropped to keep the bundled asset smaller. */
const val INDIA_TIMEZONE = "Asia/Kolkata"

class IndiaPlacesRepository(context: Context) {
    private val places: List<IndiaPlace> by lazy {
        context.assets.open("india_places.json").use { stream ->
            val type = object : TypeToken<List<IndiaPlace>>() {}.type
            Gson().fromJson(stream.bufferedReader(), type)
        }
    }

    fun states(): List<String> = places.map { it.state }.distinct().sorted()

    fun districts(state: String): List<String> =
        places.filter { it.state == state }.map { it.district }.distinct().sorted()

    fun cities(state: String, district: String): List<IndiaPlace> =
        places.filter { it.state == state && it.district == district }
            .sortedWith(compareByDescending<IndiaPlace> { it.population }.thenBy { it.name })
}
