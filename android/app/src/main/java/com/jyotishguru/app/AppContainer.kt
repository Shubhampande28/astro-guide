package com.jyotishguru.app

import android.app.Application
import com.jyotishguru.app.data.ApiClient
import com.jyotishguru.app.data.TokenStore

class JyotishGuruApp : Application() {
    lateinit var tokenStore: TokenStore
        private set

    lateinit var api: com.jyotishguru.app.data.ApiService
        private set

    override fun onCreate() {
        super.onCreate()
        tokenStore = TokenStore(this)
        api = ApiClient.create(tokenStore)
    }
}
