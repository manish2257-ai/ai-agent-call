package com.example.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.model.AppConfigState
import com.example.model.CallRecord
import com.example.model.ExotelStatus
import com.example.network.BackendRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AppViewModel : ViewModel() {

    private val repository = BackendRepository()

    private val _configState = MutableStateFlow(AppConfigState(isLoading = false))
    val configState: StateFlow<AppConfigState> = _configState.asStateFlow()

    private val _exotelStatus = MutableStateFlow(ExotelStatus())
    val exotelStatus: StateFlow<ExotelStatus> = _exotelStatus.asStateFlow()

    private val _calls = MutableStateFlow<List<CallRecord>>(emptyList())
    val calls: StateFlow<List<CallRecord>> = _calls.asStateFlow()

    private val _selectedTab = MutableStateFlow(0)
    val selectedTab: StateFlow<Int> = _selectedTab.asStateFlow()

    init {
        loadData()
    }

    fun selectTab(tabIndex: Int) {
        _selectedTab.value = tabIndex
    }

    fun loadData() {
        viewModelScope.launch {
            _configState.value = _configState.value.copy(isLoading = true)

            val config = repository.fetchAppConfig()
            val exotel = repository.fetchExotelStatus()
            val callsList = repository.fetchCalls()

            _configState.value = config.copy(isLoading = false)
            _exotelStatus.value = exotel
            _calls.value = callsList
        }
    }

    fun toggleAgentOnline(enabled: Boolean) {
        // Optimistic update
        _configState.value = _configState.value.copy(
            agentEnabled = enabled,
            active = enabled
        )

        viewModelScope.launch {
            val success = repository.toggleAgentEnabled(enabled)
            if (!success) {
                // Refresh on failure
                val config = repository.fetchAppConfig()
                _configState.value = config
            }
        }
    }
}
