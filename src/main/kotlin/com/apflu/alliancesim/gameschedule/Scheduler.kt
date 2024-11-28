package com.apflu.alliancesim.gameschedule

import com.apflu.alliancesim.game.GameCharacter
import com.apflu.alliancesim.game.SpaceObject
import com.apflu.alliancesim.game.equipment.ShipActiveModule
import com.apflu.alliancesim.game.equipment.ShipModuleRepeatable
import kotlinx.coroutines.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * 此模块较为复杂。如果有一定理解上的困难的话，不必过多纠结。
 *
 * 未来还会继续扩充。
 */
object Scheduler {
    private val logger: Logger = LoggerFactory.getLogger(Scheduler::class.java)
    // TODO: 用Dispatchers重写，或是MutableStateFlow/Channel。
    private val jobMap = mutableMapOf<ShipActiveModule, Job>()
    private val skillUpdaterMap = mutableMapOf<SkillUpdaterBuilder, Job>()

    fun registerModule(module: ShipActiveModule, target: SpaceObject?) {
        val job = CoroutineScope(Dispatchers.Default).launch {
            try {
                do {
                    val repeat = (module as? ShipModuleRepeatable)?.repeat == true
                    module.onCycleStart(target)
                    delay((module.interval * 1000).toLong())
                    module.onCycleEnd(target)
                } while (repeat)
            } catch (e: CancellationException) {
                logger.debug("module ${module.name}'s activation is interrupted.")
            }
        }
        jobMap[module] = job
        logger.trace("registered module ${module.name} for its timer.")
    }

    /**
     * 停止武器/
     */
    fun unregisterModule(module: ShipActiveModule) {
        val targetJob = jobMap[module]
        targetJob?.cancel()
        jobMap.remove(module)
        logger.trace("unregistered module ${module.name} for its timer.")
    }

    fun startSkillUpdater(updater: SkillUpdaterBuilder, runWhenIntersectExist: Boolean = true) {
        val trackingCharacters = skillUpdaterMap.keys.fold(setOf<GameCharacter>()) { acc, set ->
            acc.union(set.characterRange)
        }

        val intersect = updater.characterRange.intersect(trackingCharacters)

        if (intersect.isNotEmpty()) {
            for (character in intersect) {
                logger.warn("character $character exists in multiple SkillUpdater!")
            }

            if (!runWhenIntersectExist) {
                throw IllegalArgumentException(updater.toString())
            }
        }

        skillUpdaterMap.put(updater, updater.build())
    }
}