package com.example

import com.example.model.AppConfigState
import com.example.model.ExotelStatus
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class AppConfigStateTest {

    @Test
    fun testDefaultStateHasZeroFakeData() {
        val state = AppConfigState()

        // Verify zero fake statistics
        assertEquals(0, state.callsToday)
        assertEquals(0, state.totalCalls)
        assertEquals(0, state.urgentEscalations)
        assertEquals(0, state.smsAlertsSent)
        assertEquals(0, state.avgCallDurationSeconds)

        // Verify zero fake numbers
        assertEquals("Not configured", state.ownerPhoneNumber)

        // Verify real production provider defaults
        assertEquals("Exotel", state.telephonyProvider)
        assertEquals("READY", state.telephonyStatus)
    }

    @Test
    fun testExotelStatusDefault() {
        val exotel = ExotelStatus()
        assertEquals("Exotel", exotel.provider)
        assertEquals("READY", exotel.status)
        assertEquals("PRODUCTION", exotel.mode)
        assertTrue(exotel.missingVariables.isEmpty())
    }
}
