package com.apflu.alliancesim.gameschedule

import com.apflu.alliancesim.game.GameCharacter
import com.apflu.alliancesim.logging.LogMarkers
import kotlinx.coroutines.*
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class SkillUpdaterBuilder(val characterRange: MutableSet<GameCharacter>, val interval: Long,
                          val scope: CoroutineScope = CoroutineScope(Dispatchers.Default)) {

    private val logger: Logger = LoggerFactory.getLogger(SkillUpdaterBuilder::class.java)

    var rangeUpdated = false
    var pendingRange: Set<GameCharacter> = characterRange

    fun addCharacter(character: GameCharacter) {
        val updated = characterRange.add(character)
        if (!updated) {
            logger.info(LogMarkers.SKILL_TRAINING, "Adding $character to ${this}, but the set wasn't updated.")
        }
        rangeUpdated = true
    }

    fun addCharacter(characters: Collection<GameCharacter>) {
        // TODO
        throw UnsupportedOperationException()
    }

    fun setCharacterRange(characterRange: MutableSet<GameCharacter>): SkillUpdaterBuilder {
        return SkillUpdaterBuilder(characterRange, interval, scope)
    }

    fun setInterval(interval: Long): SkillUpdaterBuilder {
        return SkillUpdaterBuilder(characterRange, interval, scope)
    }

    fun setScope(scope: CoroutineScope): SkillUpdaterBuilder {
        return SkillUpdaterBuilder(characterRange, interval, scope)
    }

    /**
     * avoid direct usage in common circumstances
     */
    internal fun build(): Job {
        return scope.launch(start = CoroutineStart.LAZY) {
            while (true) {
                if (rangeUpdated) {
                    pendingRange = characterRange.toSet()
                }

                for (char in pendingRange) {
                    char.updateSkill(interval)
                }
                delay(interval)
            }
        }
    }
}