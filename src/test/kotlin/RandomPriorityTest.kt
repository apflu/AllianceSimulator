import org.junit.jupiter.api.Assertions.assertTrue
import org.junit.jupiter.api.Test
import kotlin.random.Random

class RandomPriorityTest {
    @Test
    fun getRandomFirstImplementation() {
        val strings = listOf(
            "MilestoneSaveAndSQL",
            "MilestoneAllianceResearchSystem",
            "MilestoneBasicCommandMechanism",
            "MilestoneBasicEventMechanism")
        println(strings[Random.nextInt(strings.size)])
        assertTrue(true)
    }
}