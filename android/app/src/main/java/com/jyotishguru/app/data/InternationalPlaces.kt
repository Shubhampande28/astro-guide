package com.jyotishguru.app.data

/** A short fallback list for births outside India (the main picker is
 * IndiaPlacesRepository's State -> District -> City cascade, which covers
 * India comprehensively). Not meant to be exhaustive -- just enough for
 * common diaspora cases; a real global geocoding lookup is future work.
 */
data class InternationalPlace(
    val name: String,
    val lat: Double,
    val lon: Double,
    val timezone: String,
)

val INTERNATIONAL_PLACES = listOf(
    InternationalPlace("Dubai, UAE", 25.2048, 55.2708, "Asia/Dubai"),
    InternationalPlace("Abu Dhabi, UAE", 24.4539, 54.3773, "Asia/Dubai"),
    InternationalPlace("Singapore", 1.3521, 103.8198, "Asia/Singapore"),
    InternationalPlace("Kuala Lumpur, Malaysia", 3.1390, 101.6869, "Asia/Kuala_Lumpur"),
    InternationalPlace("London, UK", 51.5072, -0.1276, "Europe/London"),
    InternationalPlace("New York, USA", 40.7128, -74.0060, "America/New_York"),
    InternationalPlace("San Francisco, USA", 37.7749, -122.4194, "America/Los_Angeles"),
    InternationalPlace("Toronto, Canada", 43.6532, -79.3832, "America/Toronto"),
    InternationalPlace("Sydney, Australia", -33.8688, 151.2093, "Australia/Sydney"),
    InternationalPlace("Melbourne, Australia", -37.8136, 144.9631, "Australia/Melbourne"),
    InternationalPlace("Kathmandu, Nepal", 27.7172, 85.3240, "Asia/Kathmandu"),
    InternationalPlace("Dhaka, Bangladesh", 23.8103, 90.4125, "Asia/Dhaka"),
    InternationalPlace("Colombo, Sri Lanka", 6.9271, 79.8612, "Asia/Colombo"),
    InternationalPlace("Muscat, Oman", 23.5880, 58.3829, "Asia/Muscat"),
    InternationalPlace("Doha, Qatar", 25.2854, 51.5310, "Asia/Qatar"),
)

fun searchInternationalPlaces(query: String): List<InternationalPlace> {
    if (query.isBlank()) return emptyList()
    val lowered = query.trim().lowercase()
    return INTERNATIONAL_PLACES.filter { it.name.lowercase().contains(lowered) }.take(8)
}
