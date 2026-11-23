package com.jyotishguru.app

import android.app.Application
import com.jyotishguru.app.data.ApiClient
import com.jyotishguru.app.data.ApiService
import com.jyotishguru.app.data.IndiaPlacesRepository
import com.jyotishguru.app.data.TokenStore

class JyotishGuruApp : Application() {
    lateinit var tokenStore: TokenStore
        private set

    lateinit var api: ApiService
        private set

    lateinit var indiaPlaces: IndiaPlacesRepository
        private set

    override fun onCreate() {
        super.onCreate()
        tokenStore = TokenStore(this)
        api = ApiClient.create(tokenStore)
        indiaPlaces = IndiaPlacesRepository(this)
    }
}
