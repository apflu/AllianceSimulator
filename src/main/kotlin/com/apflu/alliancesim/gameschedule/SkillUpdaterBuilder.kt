package com.apflu.alliancesim.gameschedule

import com.apflu.alliancesim.game.GameCharacter
import kotlinx.coroutines.*

class SkillUpdaterBuilder(val characterRange: Set<GameCharacter>, val interval: Long,
                          val scope: CoroutineScope = CoroutineScope(Dispatchers.Default)) {
    fun setCharacterRange(characterRange: Set<GameCharacter>): SkillUpdaterBuilder {
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
                for (char in characterRange) {
                    char.updateSkill(interval)
                }
                delay(interval)
            }
        }
    }
}