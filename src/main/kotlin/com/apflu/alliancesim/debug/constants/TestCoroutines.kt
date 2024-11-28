package com.apflu.alliancesim.debug.constants

import io.github.oshai.kotlinlogging.KotlinLogging
import kotlinx.coroutines.*

object TestCoroutines {
    private val logger = KotlinLogging.logger {}

    @OptIn(DelicateCoroutinesApi::class)
    suspend fun doInfiniteWait() {
        val job = GlobalScope.launch {
            while (true) {
                delay(10000L)
                logger.debug { "Waiting with infinite Coroutine." }
            }
        }
        try {
            job.join()
        } catch (e: CancellationException) {
            logger.debug { "Job was cancelled." }
        }
    }
}