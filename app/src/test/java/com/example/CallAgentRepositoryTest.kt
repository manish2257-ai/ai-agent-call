package com.example

import com.example.data.model.UrgencyLevel
import com.example.data.repository.CallAgentRepository
import org.junit.Assert.*
import org.junit.Test

class CallAgentRepositoryTest {

    @Test
    fun testRepositoryInitialization() {
        val calls = CallAgentRepository.calls.value
        assertTrue("Calls should not be empty", calls.isNotEmpty())

        val contacts = CallAgentRepository.contacts.value
        assertTrue("VIP contacts should be seeded", contacts.isNotEmpty())

        val rules = CallAgentRepository.rules.value
        assertTrue("Urgency rules should be seeded", rules.isNotEmpty())
    }

    @Test
    fun testToggleAgentStatus() {
        val initial = CallAgentRepository.settings.value.isAgentEnabled
        CallAgentRepository.toggleAgentStatus()
        assertEquals(!initial, CallAgentRepository.settings.value.isAgentEnabled)
        // Revert
        CallAgentRepository.toggleAgentStatus()
        assertEquals(initial, CallAgentRepository.settings.value.isAgentEnabled)
    }

    @Test
    fun testSimulateOutageScenario() {
        val countBefore = CallAgentRepository.calls.value.size
        val record = CallAgentRepository.simulateCallScenario("outage")

        assertEquals(UrgencyLevel.HIGH, record.urgency)
        assertTrue(record.reason.contains("outage", ignoreCase = true))
        assertEquals(countBefore + 1, CallAgentRepository.calls.value.size)

        // Verify simulated SMS was generated
        val latestAlert = CallAgentRepository.latestAlert.value
        assertNotNull("Latest SMS alert should not be null for high urgency", latestAlert)
        assertTrue(latestAlert!!.formattedMessage.contains("HIGH"))
    }
}
